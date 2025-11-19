#!/usr/bin/env python3
"""
Fix database issues:
1. Link jobs to customers (handle NULL opportunity_status)
2. Verify and fix quote number linkages
3. Implement duplicate job detection logic
4. Remove test branches and associated customers
"""

import sys
from pathlib import Path
import psycopg2
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def link_jobs_to_customers(conn, dry_run: bool = True):
    """Link jobs to customers using multiple strategies."""
    cursor = conn.cursor()
    
    # Strategy 1: Link via booked_opportunities (most reliable)
    logger.info("Strategy 1: Linking jobs via booked_opportunities...")
    cursor.execute("""
        UPDATE jobs j
        SET customer_id = bo.customer_id,
            updated_at = NOW()
        FROM booked_opportunities bo
        WHERE j.customer_id IS NULL
          AND bo.customer_id IS NOT NULL
          AND (
              (j.customer_email IS NOT NULL AND bo.email = TRIM(j.customer_email))
              OR (j.customer_phone IS NOT NULL AND bo.phone_number = TRIM(j.customer_phone))
              OR (j.customer_name IS NOT NULL AND bo.customer_name = TRIM(j.customer_name))
          )
    """)
    via_bo = cursor.rowcount
    logger.info(f"  Linked {via_bo:,} jobs via booked_opportunities")
    
    # Strategy 2: Direct customer matching with normalization
    logger.info("Strategy 2: Direct customer matching...")
    cursor.execute("""
        UPDATE jobs j
        SET customer_id = c.id,
            updated_at = NOW()
        FROM customers c
        WHERE j.customer_id IS NULL
          AND (
              (j.customer_email IS NOT NULL AND c.email = TRIM(LOWER(j.customer_email)))
              OR (j.customer_phone IS NOT NULL AND c.phone = REGEXP_REPLACE(TRIM(j.customer_phone), '[^0-9]', '', 'g'))
          )
    """)
    direct = cursor.rowcount
    logger.info(f"  Linked {direct:,} jobs via direct customer matching")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return via_bo + direct


def fix_quote_number_linkages(conn, dry_run: bool = True):
    """Fix quote number linkages for lead_status and lost_leads."""
    cursor = conn.cursor()
    
    # Link lead_status to booked_opportunities
    logger.info("Linking LeadStatus to BookedOpportunities via quote_number...")
    cursor.execute("""
        UPDATE lead_status ls
        SET booked_opportunity_id = bo.id,
            updated_at = NOW()
        FROM booked_opportunities bo
        WHERE ls.quote_number = bo.quote_number
          AND ls.booked_opportunity_id IS NULL
    """)
    ls_linked = cursor.rowcount
    logger.info(f"  Linked {ls_linked:,} LeadStatus records")
    
    # Link lost_leads to booked_opportunities
    logger.info("Linking LostLeads to BookedOpportunities via quote_number...")
    cursor.execute("""
        UPDATE lost_leads ll
        SET booked_opportunity_id = bo.id,
            updated_at = NOW()
        FROM booked_opportunities bo
        WHERE ll.quote_number = bo.quote_number
          AND ll.booked_opportunity_id IS NULL
    """)
    ll_linked = cursor.rowcount
    logger.info(f"  Linked {ll_linked:,} LostLead records")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return ls_linked, ll_linked


def detect_duplicate_jobs(conn, dry_run: bool = True):
    """Detect and mark duplicate jobs based on multiple criteria."""
    cursor = conn.cursor()
    
    logger.info("Detecting duplicate jobs...")
    
    # Mark duplicates based on job_id (exact duplicates)
    cursor.execute("""
        WITH duplicates AS (
            SELECT id, job_id,
                   ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY created_at) as rn
            FROM jobs
            WHERE job_id IS NOT NULL
        )
        UPDATE jobs j
        SET is_duplicate = true,
            updated_at = NOW()
        FROM duplicates d
        WHERE j.id = d.id
          AND d.rn > 1
          AND j.is_duplicate = false
    """)
    by_job_id = cursor.rowcount
    logger.info(f"  Marked {by_job_id:,} duplicates by job_id")
    
    # Mark duplicates based on customer + date + cost (similar jobs)
    cursor.execute("""
        WITH duplicates AS (
            SELECT id, customer_id, job_date, total_estimated_cost,
                   ROW_NUMBER() OVER (
                       PARTITION BY customer_id, job_date, total_estimated_cost 
                       ORDER BY created_at
                   ) as rn
            FROM jobs
            WHERE customer_id IS NOT NULL
              AND job_date IS NOT NULL
              AND total_estimated_cost IS NOT NULL
        )
        UPDATE jobs j
        SET is_duplicate = true,
            updated_at = NOW()
        FROM duplicates d
        WHERE j.id = d.id
          AND d.rn > 1
          AND j.is_duplicate = false
    """)
    by_similarity = cursor.rowcount
    logger.info(f"  Marked {by_similarity:,} duplicates by similarity")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return by_job_id + by_similarity


def remove_test_branches_and_customers(conn, dry_run: bool = True):
    """Remove test branches and their associated customers."""
    cursor = conn.cursor()
    
    # Get test branch IDs
    cursor.execute("""
        SELECT id, name
        FROM branches
        WHERE LOWER(name) LIKE '%test%'
           OR LOWER(name) LIKE '%xxx%'
           OR LOWER(name) LIKE '%no longer active%'
           OR LOWER(name) LIKE '%close all test%'
    """)
    test_branches = cursor.fetchall()
    
    if not test_branches:
        logger.info("No test branches found")
        return 0, 0
    
    branch_ids = [b[0] for b in test_branches]
    branch_names = [b[1] for b in test_branches]
    
    logger.info(f"Found {len(test_branches)} test branches:")
    for name in branch_names:
        logger.info(f"  - {name}")
    
    # Find customers only associated with test branches
    cursor.execute("""
        WITH test_customers AS (
            SELECT DISTINCT c.id
            FROM customers c
            INNER JOIN booked_opportunities bo ON c.id = bo.customer_id
            WHERE bo.branch_id = ANY(%s)
            
            UNION
            
            SELECT DISTINCT c.id
            FROM customers c
            INNER JOIN jobs j ON c.id = j.customer_id
            WHERE j.branch_id = ANY(%s)
        ),
        non_test_customers AS (
            SELECT DISTINCT c.id
            FROM customers c
            INNER JOIN booked_opportunities bo ON c.id = bo.customer_id
            WHERE bo.branch_id IS NOT NULL
              AND bo.branch_id != ALL(%s)
            
            UNION
            
            SELECT DISTINCT c.id
            FROM customers c
            INNER JOIN jobs j ON c.id = j.customer_id
            WHERE j.branch_id IS NOT NULL
              AND j.branch_id != ALL(%s)
        )
        SELECT tc.id
        FROM test_customers tc
        WHERE NOT EXISTS (
            SELECT 1 FROM non_test_customers ntc WHERE ntc.id = tc.id
        )
    """, (branch_ids, branch_ids, branch_ids, branch_ids))
    
    test_customer_ids = [row[0] for row in cursor.fetchall()]
    
    logger.info(f"Found {len(test_customer_ids):,} customers only associated with test branches")
    
    if not dry_run:
        # Delete test customers (cascade will handle related records)
        if test_customer_ids:
            placeholders = ','.join(['%s'] * len(test_customer_ids))
            cursor.execute(f"""
                DELETE FROM customers
                WHERE id IN ({placeholders})
            """, test_customer_ids)
            customers_deleted = cursor.rowcount
        else:
            customers_deleted = 0
        
        # Delete test branches
        placeholders = ','.join(['%s'] * len(branch_ids))
        cursor.execute(f"""
            DELETE FROM branches
            WHERE id IN ({placeholders})
        """, branch_ids)
        branches_deleted = cursor.rowcount
        
        conn.commit()
        logger.info(f"Deleted {customers_deleted:,} test customers and {branches_deleted} test branches")
    else:
        customers_deleted = len(test_customer_ids)
        branches_deleted = len(test_branches)
        logger.info(f"[DRY RUN] Would delete {customers_deleted:,} customers and {branches_deleted} branches")
    
    cursor.close()
    return customers_deleted, branches_deleted


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix database issues')
    parser.add_argument('--execute', action='store_true', help='Execute changes (default is dry-run)')
    parser.add_argument('--skip-jobs', action='store_true', help='Skip jobs to customers linking')
    parser.add_argument('--skip-quotes', action='store_true', help='Skip quote number linkages')
    parser.add_argument('--skip-duplicates', action='store_true', help='Skip duplicate detection')
    parser.add_argument('--skip-test-cleanup', action='store_true', help='Skip test branch/customer removal')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING changes to database.")
    
    conn = get_db_connection()
    
    try:
        results = {}
        
        if not args.skip_jobs:
            logger.info("\n" + "="*80)
            logger.info("STEP 1: Linking Jobs to Customers")
            logger.info("="*80)
            results['jobs_linked'] = link_jobs_to_customers(conn, dry_run=dry_run)
        
        if not args.skip_quotes:
            logger.info("\n" + "="*80)
            logger.info("STEP 2: Fixing Quote Number Linkages")
            logger.info("="*80)
            ls_linked, ll_linked = fix_quote_number_linkages(conn, dry_run=dry_run)
            results['quote_linkages'] = (ls_linked, ll_linked)
        
        if not args.skip_duplicates:
            logger.info("\n" + "="*80)
            logger.info("STEP 3: Detecting Duplicate Jobs")
            logger.info("="*80)
            results['duplicates'] = detect_duplicate_jobs(conn, dry_run=dry_run)
        
        if not args.skip_test_cleanup:
            logger.info("\n" + "="*80)
            logger.info("STEP 4: Removing Test Branches and Customers")
            logger.info("="*80)
            customers_deleted, branches_deleted = remove_test_branches_and_customers(conn, dry_run=dry_run)
            results['test_cleanup'] = (customers_deleted, branches_deleted)
        
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        if 'jobs_linked' in results:
            logger.info(f"Jobs linked to customers: {results['jobs_linked']:,}")
        if 'quote_linkages' in results:
            ls, ll = results['quote_linkages']
            logger.info(f"LeadStatus linked: {ls:,}, LostLeads linked: {ll:,}")
        if 'duplicates' in results:
            logger.info(f"Duplicate jobs marked: {results['duplicates']:,}")
        if 'test_cleanup' in results:
            cust, br = results['test_cleanup']
            logger.info(f"Test customers deleted: {cust:,}, Test branches deleted: {br}")
        logger.info("="*80)
        
        if dry_run:
            logger.info("\nDry run complete. Review the output and run with --execute to apply changes.")
        else:
            logger.info("\nAll fixes applied successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

