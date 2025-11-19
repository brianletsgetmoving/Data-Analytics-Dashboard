#!/usr/bin/env python3
"""
Populate first_lead_date and conversion_date fields in Customer table 
for lead journey tracking.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "populate_customer_timeline_fields"


def populate_customer_timeline_fields(conn, dry_run: bool = True):
    """Populate first_lead_date and conversion_date for customers."""
    cursor = conn.cursor()
    
    # Update first_lead_date from earliest lead_status, bad_lead, or lost_lead
    # Note: lead_status doesn't have customer_id directly, we need to go through booked_opportunities
    cursor.execute("""
        UPDATE customers c
        SET first_lead_date = subq.earliest_lead_date,
            updated_at = NOW()
        FROM (
            SELECT 
                c.id as customer_id,
                MIN(earliest_date) as earliest_lead_date
            FROM customers c
            LEFT JOIN (
                SELECT bo.customer_id, MIN(ls.created_at) as earliest_date
                FROM lead_status ls
                JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
                WHERE bo.customer_id IS NOT NULL
                GROUP BY bo.customer_id
                UNION ALL
                SELECT customer_id, MIN(date_lead_received) as earliest_date
                FROM bad_leads bl
                WHERE customer_id IS NOT NULL AND date_lead_received IS NOT NULL
                GROUP BY customer_id
                UNION ALL
                SELECT bo.customer_id, MIN(ll.date_received) as earliest_date
                FROM lost_leads ll
                JOIN booked_opportunities bo ON ll.booked_opportunity_id = bo.id
                WHERE bo.customer_id IS NOT NULL AND ll.date_received IS NOT NULL
                GROUP BY bo.customer_id
            ) leads ON leads.customer_id = c.id
            WHERE earliest_date IS NOT NULL
            GROUP BY c.id
        ) subq
        WHERE c.id = subq.customer_id
          AND (c.first_lead_date IS NULL OR c.first_lead_date > subq.earliest_lead_date)
    """)
    
    first_lead_updated = cursor.rowcount
    
    # Update conversion_date from earliest booked_opportunity or job
    cursor.execute("""
        UPDATE customers c
        SET conversion_date = subq.earliest_conversion_date,
            updated_at = NOW()
        FROM (
            SELECT 
                c.id as customer_id,
                MIN(earliest_date) as earliest_conversion_date
            FROM customers c
            LEFT JOIN (
                SELECT customer_id, MIN(booked_date) as earliest_date
                FROM booked_opportunities bo
                WHERE customer_id IS NOT NULL AND booked_date IS NOT NULL
                GROUP BY customer_id
                UNION ALL
                SELECT customer_id, MIN(job_date) as earliest_date
                FROM jobs j
                WHERE customer_id IS NOT NULL 
                  AND job_date IS NOT NULL
                  AND opportunity_status IN ('BOOKED', 'CLOSED')
                GROUP BY customer_id
            ) conversions ON conversions.customer_id = c.id
            WHERE earliest_date IS NOT NULL
            GROUP BY c.id
        ) subq
        WHERE c.id = subq.customer_id
          AND (c.conversion_date IS NULL OR c.conversion_date > subq.earliest_conversion_date)
    """)
    
    conversion_updated = cursor.rowcount
    
    if not dry_run:
        conn.commit()
        logger.info(f"Updated first_lead_date for {first_lead_updated} customers")
        logger.info(f"Updated conversion_date for {conversion_updated} customers")
    else:
        logger.info(f"[DRY RUN] Would update first_lead_date for {first_lead_updated} customers")
        logger.info(f"[DRY RUN] Would update conversion_date for {conversion_updated} customers")
    
    cursor.close()
    return first_lead_updated, conversion_updated


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate customer timeline fields')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the updates (overrides dry-run)')
    parser.add_argument('--force', action='store_true',
                       help='Force execution even if already run')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
        # Check if script should run (idempotency check)
        if not dry_run and not check_and_log_execution(conn, SCRIPT_NAME, force=args.force,
                                                      notes="Populate customer timeline fields"):
            return 0
        
        # Check if there's any work to do
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM customers WHERE first_lead_date IS NULL) as missing_first_lead,
                (SELECT COUNT(*) FROM customers WHERE conversion_date IS NULL) as missing_conversion
        """)
        result = cursor.fetchone()
        cursor.close()
        
        missing_first_lead = result[0] if result else 0
        missing_conversion = result[1] if result else 0
        
        if missing_first_lead == 0 and missing_conversion == 0:
            logger.info("No missing timeline fields found. All customer timeline fields are already populated.")
            return 0
        
        logger.info(f"Found {missing_first_lead} customers missing first_lead_date and {missing_conversion} missing conversion_date")
        logger.info("Populating customer timeline fields...")
        first_lead_count, conversion_count = populate_customer_timeline_fields(conn, dry_run=dry_run)
        
        print("\n" + "="*80)
        print("CUSTOMER TIMELINE POPULATION SUMMARY")
        print("="*80)
        print(f"Customers with first_lead_date updated: {first_lead_count}")
        print(f"Customers with conversion_date updated: {conversion_count}")
        print("="*80 + "\n")
        
        if dry_run:
            logger.info("Dry run complete. Review the output and run with --execute to apply changes.")
        else:
            logger.info("Population complete!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Population failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

