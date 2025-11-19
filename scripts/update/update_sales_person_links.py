#!/usr/bin/env python3
"""
Update all SalesPerson links in Jobs, BookedOpportunities, and leads using sales-performance naming convention.
"""

import sys
from pathlib import Path
import psycopg2
import logging
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "update_sales_person_links"


def get_salesperson_name_mapping(conn) -> Dict[str, str]:
    """Get mapping of all sales person names to their IDs."""
    cursor = conn.cursor()
    mapping = {}
    
    try:
        cursor.execute("""
            SELECT id, name FROM sales_persons ORDER BY name
        """)
        
        for salesperson_id, name in cursor.fetchall():
            mapping[name] = salesperson_id
        
        logger.info(f"Found {len(mapping)} SalesPerson records")
        return mapping
    
    finally:
        cursor.close()


def normalize_name_for_matching(name: str) -> str:
    """Normalize name for matching (extract base name, remove extra info)."""
    if not name:
        return ""
    
    # Remove content in parentheses
    import re
    normalized = re.sub(r'\([^)]*\)', '', name).strip()
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized


def match_name_to_salesperson(name: str, salesperson_map: Dict[str, str]) -> Optional[str]:
    """Match a name to a SalesPerson ID using sales-performance naming."""
    if not name:
        return None
    
    # Try exact match first
    if name in salesperson_map:
        return salesperson_map[name]
    
    # Try normalized match
    normalized = normalize_name_for_matching(name)
    if normalized in salesperson_map:
        return salesperson_map[normalized]
    
    # Try case-insensitive match
    name_lower = name.lower().strip()
    for sp_name, sp_id in salesperson_map.items():
        if sp_name.lower().strip() == name_lower:
            return sp_id
    
    # Try normalized case-insensitive match
    normalized_lower = normalized.lower()
    for sp_name, sp_id in salesperson_map.items():
        sp_normalized = normalize_name_for_matching(sp_name).lower()
        if sp_normalized == normalized_lower:
            return sp_id
    
    # Try partial match (contains)
    for sp_name, sp_id in salesperson_map.items():
        if normalized_lower in sp_name.lower() or sp_name.lower() in normalized_lower:
            return sp_id
    
    return None


def update_jobs_salesperson_links(conn, salesperson_map: Dict[str, str], dry_run: bool = True) -> int:
    """Update SalesPerson links in Jobs table."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # Get all jobs with sales_person_name but no sales_person_id or mismatched
        cursor.execute("""
            SELECT id, sales_person_name, sales_person_id
            FROM jobs
            WHERE sales_person_name IS NOT NULL
            ORDER BY sales_person_name
        """)
        
        jobs = cursor.fetchall()
        logger.info(f"Found {len(jobs)} jobs with sales_person_name")
        
        if dry_run:
            logger.info("[DRY RUN] Would update jobs sales_person_id links")
            return len(jobs)
        
        for job_id, sales_person_name, current_sales_person_id in jobs:
            matched_id = match_name_to_salesperson(sales_person_name, salesperson_map)
            
            if matched_id and matched_id != current_sales_person_id:
                cursor.execute("""
                    UPDATE jobs
                    SET sales_person_id = %s, updated_at = NOW()
                    WHERE id = %s
                """, (matched_id, job_id))
                updated += 1
        
        conn.commit()
        logger.info(f"Updated {updated} jobs with SalesPerson links")
        return updated
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating jobs: {e}")
        raise
    finally:
        cursor.close()


def update_booked_opportunities_salesperson_links(conn, salesperson_map: Dict[str, str], dry_run: bool = True) -> int:
    """Update SalesPerson links in BookedOpportunities table."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # BookedOpportunities don't have sales_person_name, so we need to check existing links
        # or match via other means. For now, we'll update existing links that might be wrong.
        # This might need to be enhanced based on actual data structure.
        
        cursor.execute("""
            SELECT COUNT(*) FROM booked_opportunities WHERE sales_person_id IS NOT NULL
        """)
        total_with_links = cursor.fetchone()[0]
        
        logger.info(f"Found {total_with_links} booked opportunities with sales_person_id")
        
        # For now, we'll just verify existing links are valid
        if dry_run:
            logger.info("[DRY RUN] Would verify booked opportunities sales_person_id links")
            return 0
        
        # Verify and fix invalid links
        cursor.execute("""
            UPDATE booked_opportunities bo
            SET sales_person_id = NULL, updated_at = NOW()
            WHERE bo.sales_person_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM sales_persons sp WHERE sp.id = bo.sales_person_id
            )
        """)
        fixed = cursor.rowcount
        
        conn.commit()
        logger.info(f"Fixed {fixed} invalid SalesPerson links in booked_opportunities")
        return fixed
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating booked_opportunities: {e}")
        raise
    finally:
        cursor.close()


def update_leads_salesperson_links(conn, salesperson_map: Dict[str, str], dry_run: bool = True) -> int:
    """Update SalesPerson links in leads table (or lead_status if not yet renamed)."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # Check if leads table exists, otherwise use lead_status
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            )
        """)
        leads_exists = cursor.fetchone()[0]
        table_name = 'leads' if leads_exists else 'lead_status'
        
        # Similar to booked_opportunities, leads might not have sales_person_name
        # We'll verify and fix invalid links
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name} WHERE sales_person_id IS NOT NULL
        """)
        total_with_links = cursor.fetchone()[0]
        
        logger.info(f"Found {total_with_links} leads with sales_person_id")
        
        if dry_run:
            logger.info("[DRY RUN] Would verify leads sales_person_id links")
            return 0
        
        # Verify and fix invalid links
        cursor.execute(f"""
            UPDATE {table_name} l
            SET sales_person_id = NULL, updated_at = NOW()
            WHERE l.sales_person_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM sales_persons sp WHERE sp.id = l.sales_person_id
            )
        """)
        fixed = cursor.rowcount
        
        conn.commit()
        logger.info(f"Fixed {fixed} invalid SalesPerson links in leads")
        return fixed
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating leads: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update SalesPerson links in all modules')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    # Check if script has already been executed
    if not dry_run:
        conn = get_db_connection()
        try:
            if check_and_log_execution(conn, SCRIPT_NAME):
                logger.info(f"Script '{SCRIPT_NAME}' has already been executed. Use --force to re-run.")
                return
        finally:
            conn.close()
    
    conn = get_db_connection()
    
    try:
        logger.info("="*80)
        logger.info("UPDATE SALESPERSON LINKS")
        logger.info("="*80)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Get SalesPerson mapping
        logger.info("\nLoading SalesPerson name mapping...")
        salesperson_map = get_salesperson_name_mapping(conn)
        
        if not salesperson_map:
            logger.warning("No SalesPerson records found. Run import_performance_data first.")
            return
        
        # Update Jobs
        logger.info("\nUpdating Jobs SalesPerson links...")
        jobs_updated = update_jobs_salesperson_links(conn, salesperson_map, dry_run)
        
        # Update BookedOpportunities
        logger.info("\nUpdating BookedOpportunities SalesPerson links...")
        bo_updated = update_booked_opportunities_salesperson_links(conn, salesperson_map, dry_run)
        
        # Update leads
        logger.info("\nUpdating leads SalesPerson links...")
        leads_updated = update_leads_salesperson_links(conn, salesperson_map, dry_run)
        
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"Jobs updated: {jobs_updated}")
        logger.info(f"BookedOpportunities fixed: {bo_updated}")
        logger.info(f"Leads fixed: {leads_updated}")
        logger.info("="*80)
        
        if not dry_run:
            check_and_log_execution(conn, SCRIPT_NAME, log_execution=True)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

