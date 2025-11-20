#!/usr/bin/env python3
"""
Whitelist approved branches and cascade delete all others along with associated records.
"""

import sys
from pathlib import Path
import psycopg2
import logging
from typing import List, Set, Dict
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution, script_already_executed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "whitelist_branches"

# Approved branches list (exact or fuzzy match)
APPROVED_BRANCHES = [
    'ABBOTSFORD',
    'AJAX',
    'ALEXANDRIA',
    'ARLINGTON',
    'AURORA',
    'AUSTIN',
    'BARRIE',
    'BOISE',
    'BRAMPTON',
    'BRANTFORD',
    'BURLINGTON',
    'BURNABY',
    'CALGARY',
    'COLORADO SPRINGS',
    'COQUITLAM',
    'DOWNTOWN TORONTO',
    'EDMONTON',
    'FREDERICTON',
    'HALIFAX',
    'HAMILTON',
    'HOUSTON',
    'KELOWNA',
    'KINGSTON',
    'LETHBRIDGE',
    'LITTLE FERRY',
    'LONDON',
    'MARIETTA',
    'MARKHAM',
    'MILTON',
    'MISSISSAUGA',
    'MONCTON',
    'MONTRÈAL',
    'MONTREAL',
    'MONTREAL NORTH',
    'NASHVILLE',
    'NEW JERSEY',
    'NORTH YORK',
    'NORTHERN VIRGINIA',
    'OAKVILLE',
    'OSHAWA',
    'OTTAWA',
    'PETERBOROUGH',
    'PHILADELPHIA',
    'PHOENIX',
    'REGINA',
    'RICHMOND',
    'SAINT JOHN',
    'SASKATOON',
    'SCARBOROUGH',
    'ST. CATHARINES',
    'SURREY',
    'THE WOODLANDS',
    'TULSA',
    'VANCOUVER',
    'VAUGHAN',
    'VICTORIA ISLAND',
    'WASHINGTON DC',
    'WATERLOO/KITCHENER',
    'WINDSOR',
    'WINNIPEG'
]


def normalize_branch_name(name: str) -> str:
    """Normalize branch name for matching."""
    if not name:
        return ""
    # Convert to uppercase and strip
    normalized = name.upper().strip()
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def is_approved_branch(branch_name: str) -> bool:
    """Check if a branch name matches an approved branch."""
    if not branch_name:
        return False
    
    # Explicitly exclude branches with certain patterns (even if they contain approved names)
    excluded_patterns = [
        '(No New Bookings Until Further Notice)',
        'Let\'S Get Moving',  # Variations like "Abbotsford Let'S Get Moving"
        'MovedIn',
        'Cold Call Lead',
        'Lead Saver',
        '(On Hold)',
        'Xxx',
        'Xxxduplicate',
        'Xxxno Longer Active',
        'Xxxxx -- No Longer Active',
    ]
    
    normalized = normalize_branch_name(branch_name)
    for pattern in excluded_patterns:
        if pattern.upper() in normalized:
            return False
    
    # Check exact match
    if normalized in [normalize_branch_name(b) for b in APPROVED_BRANCHES]:
        return True
    
    # Check if any approved branch is contained in the name (fuzzy match)
    # But only if it's a clean match (not with excluded patterns)
    for approved in APPROVED_BRANCHES:
        approved_normalized = normalize_branch_name(approved)
        # Only match if the approved name is the main part (not just a substring)
        if approved_normalized == normalized:
            return True
        # Allow partial match only if the branch name starts with or equals the approved name
        if normalized.startswith(approved_normalized + ' ') or normalized == approved_normalized:
            return True
    
    return False


def get_branches_to_delete(conn) -> List[tuple]:
    """Get list of branches that should be deleted (not in whitelist)."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name
            FROM branches
            ORDER BY name
        """)
        all_branches = cursor.fetchall()
        
        branches_to_delete = []
        for branch_id, branch_name in all_branches:
            if not is_approved_branch(branch_name):
                branches_to_delete.append((branch_id, branch_name))
        
        return branches_to_delete
    
    finally:
        cursor.close()


def get_associated_records(conn, branch_ids: List[str]) -> Dict:
    """Get counts of records associated with branches to be deleted."""
    cursor = conn.cursor()
    results = {}
    
    try:
        placeholders = ','.join(['%s'] * len(branch_ids))
        
        # Count Jobs
        cursor.execute(f"""
            SELECT COUNT(*) FROM jobs WHERE branch_id IN ({placeholders})
        """, branch_ids)
        results['jobs'] = cursor.fetchone()[0]
        
        # Count BookedOpportunities
        cursor.execute(f"""
            SELECT COUNT(*) FROM booked_opportunities WHERE branch_id IN ({placeholders})
        """, branch_ids)
        results['booked_opportunities'] = cursor.fetchone()[0]
        
        # Count leads (formerly lead_status) - check which table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            )
        """)
        leads_exists = cursor.fetchone()[0]
        table_name = 'leads' if leads_exists else 'lead_status'
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name} WHERE branch_id IN ({placeholders})
        """, branch_ids)
        results['leads'] = cursor.fetchone()[0]
        
        # Count Customers ONLY associated with these branches
        cursor.execute(f"""
            WITH branch_customers AS (
                SELECT DISTINCT customer_id
                FROM jobs
                WHERE branch_id IN ({placeholders})
                AND customer_id IS NOT NULL
                
                UNION
                
                SELECT DISTINCT customer_id
                FROM booked_opportunities
                WHERE branch_id IN ({placeholders})
                AND customer_id IS NOT NULL
            ),
            other_customers AS (
                SELECT DISTINCT customer_id
                FROM jobs
                WHERE branch_id IS NOT NULL
                AND branch_id != ALL(ARRAY[{placeholders}])
                AND customer_id IS NOT NULL
                
                UNION
                
                SELECT DISTINCT customer_id
                FROM booked_opportunities
                WHERE branch_id IS NOT NULL
                AND branch_id != ALL(ARRAY[{placeholders}])
                AND customer_id IS NOT NULL
            )
            SELECT COUNT(*)
            FROM branch_customers bc
            WHERE NOT EXISTS (
                SELECT 1 FROM other_customers oc WHERE oc.customer_id = bc.customer_id
            )
        """, branch_ids + branch_ids + branch_ids + branch_ids)
        results['customers'] = cursor.fetchone()[0]
        
        return results
    
    finally:
        cursor.close()


def cascade_delete_branches(conn, branch_ids: List[str], dry_run: bool = True) -> Dict:
    """Cascade delete branches and all associated records."""
    cursor = conn.cursor()
    results = {
        'jobs_deleted': 0,
        'booked_opportunities_deleted': 0,
        'leads_deleted': 0,
        'customers_deleted': 0,
        'branches_deleted': 0
    }
    
    try:
        if not branch_ids:
            logger.info("No branches to delete")
            return results
        
        placeholders = ','.join(['%s'] * len(branch_ids))
        
        if dry_run:
            logger.info(f"[DRY RUN] Would delete records associated with {len(branch_ids)} branches")
            return results
        
        # Step 1: Delete Jobs
        cursor.execute(f"""
            DELETE FROM jobs WHERE branch_id IN ({placeholders})
        """, branch_ids)
        results['jobs_deleted'] = cursor.rowcount
        logger.info(f"Deleted {results['jobs_deleted']} jobs")
        
        # Step 2: Delete BookedOpportunities
        cursor.execute(f"""
            DELETE FROM booked_opportunities WHERE branch_id IN ({placeholders})
        """, branch_ids)
        results['booked_opportunities_deleted'] = cursor.rowcount
        logger.info(f"Deleted {results['booked_opportunities_deleted']} booked opportunities")
        
        # Step 3: Delete leads (check which table exists)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            )
        """)
        leads_exists = cursor.fetchone()[0]
        table_name = 'leads' if leads_exists else 'lead_status'
        
        cursor.execute(f"""
            DELETE FROM {table_name} WHERE branch_id IN ({placeholders})
        """, branch_ids)
        results['leads_deleted'] = cursor.rowcount
        logger.info(f"Deleted {results['leads_deleted']} leads")
        
        # Step 4: Delete Customers ONLY associated with these branches
        cursor.execute(f"""
            WITH branch_customers AS (
                SELECT DISTINCT customer_id
                FROM jobs
                WHERE branch_id IN ({placeholders})
                AND customer_id IS NOT NULL
                
                UNION
                
                SELECT DISTINCT customer_id
                FROM booked_opportunities
                WHERE branch_id IN ({placeholders})
                AND customer_id IS NOT NULL
            ),
            other_customers AS (
                SELECT DISTINCT customer_id
                FROM jobs
                WHERE branch_id IS NOT NULL
                AND branch_id != ALL(ARRAY[{placeholders}])
                AND customer_id IS NOT NULL
                
                UNION
                
                SELECT DISTINCT customer_id
                FROM booked_opportunities
                WHERE branch_id IS NOT NULL
                AND branch_id != ALL(ARRAY[{placeholders}])
                AND customer_id IS NOT NULL
            )
            DELETE FROM customers
            WHERE id IN (
                SELECT bc.customer_id
                FROM branch_customers bc
                WHERE NOT EXISTS (
                    SELECT 1 FROM other_customers oc WHERE oc.customer_id = bc.customer_id
                )
            )
        """, branch_ids + branch_ids + branch_ids + branch_ids)
        results['customers_deleted'] = cursor.rowcount
        logger.info(f"Deleted {results['customers_deleted']} customers")
        
        # Step 5: Delete Branches
        cursor.execute(f"""
            DELETE FROM branches WHERE id IN ({placeholders})
        """, branch_ids)
        results['branches_deleted'] = cursor.rowcount
        logger.info(f"Deleted {results['branches_deleted']} branches")
        
        conn.commit()
        return results
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during cascade delete: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Whitelist approved branches and delete others')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    parser.add_argument('--force', action='store_true', help='Force execution even if already run')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    # Check if script has already been executed
    if not dry_run:
        conn = get_db_connection()
        try:
            if not args.force and script_already_executed(conn, SCRIPT_NAME):
                logger.info(f"Script '{SCRIPT_NAME}' has already been executed. Use --force to re-run.")
                return
        finally:
            conn.close()
    
    conn = get_db_connection()
    
    try:
        logger.info("="*80)
        logger.info("BRANCH WHITELIST CLEANUP")
        logger.info("="*80)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Get branches to delete
        logger.info("\nIdentifying branches to delete...")
        branches_to_delete = get_branches_to_delete(conn)
        
        if not branches_to_delete:
            logger.info("No branches to delete - all branches are approved")
            return
        
        branch_ids = [b[0] for b in branches_to_delete]
        branch_names = [b[1] for b in branches_to_delete]
        
        logger.info(f"\nFound {len(branches_to_delete)} branches to delete:")
        for name in branch_names[:20]:  # Show first 20
            logger.info(f"  - {name}")
        if len(branch_names) > 20:
            logger.info(f"  ... and {len(branch_names) - 20} more")
        
        # Get associated records count
        logger.info("\nCounting associated records...")
        associated = get_associated_records(conn, branch_ids)
        logger.info(f"  Jobs: {associated['jobs']:,}")
        logger.info(f"  BookedOpportunities: {associated['booked_opportunities']:,}")
        logger.info(f"  Leads: {associated['leads']:,}")
        logger.info(f"  Customers (only associated): {associated['customers']:,}")
        
        # Perform cascade delete
        logger.info("\nPerforming cascade delete...")
        results = cascade_delete_branches(conn, branch_ids, dry_run)
        
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"Branches to delete: {len(branches_to_delete)}")
        logger.info(f"Jobs deleted: {results['jobs_deleted']:,}")
        logger.info(f"BookedOpportunities deleted: {results['booked_opportunities_deleted']:,}")
        logger.info(f"Leads deleted: {results['leads_deleted']:,}")
        logger.info(f"Customers deleted: {results['customers_deleted']:,}")
        logger.info(f"Branches deleted: {results['branches_deleted']}")
        logger.info("="*80)
        
        if not dry_run:
            # Log execution
            from scripts.utils.script_execution import log_script_execution
            log_script_execution(conn, SCRIPT_NAME, "Branch whitelist cleanup completed")
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

