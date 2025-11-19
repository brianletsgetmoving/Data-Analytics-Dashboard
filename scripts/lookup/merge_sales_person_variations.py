#!/usr/bin/env python3
"""
Merge SalesPerson name variations into single canonical records.
Updates all foreign key relationships to point to canonical record.
"""

import sys
from pathlib import Path
import psycopg2
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.progress_monitor import log_step, log_success, log_error
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "merge_sales_person_variations"


# Define name variations to merge (canonical name -> variations)
NAME_VARIATIONS = {
    'Bobby S': ['Bobby', 'Bobby S'],
    'Alejandro (Spanish & French)': ['Alejandro', 'Alejandro (Spanish & French)'],
    'Daud P': ['Daud', 'Daud P'],
    'Said Elmi': ['Said', 'Said Elmi'],
    'Josephine Orji': ['Josephine O', 'Josephine Orji'],
    'Robert J': ['Rob', 'Robert J'],
    'Andres (Spanish)': ['Andres I', 'Andres (Spanish)'],
}


def find_sales_persons_by_names(conn, names: list) -> list:
    """Find SalesPerson records by names."""
    cursor = conn.cursor()
    placeholders = ','.join(['%s'] * len(names))
    cursor.execute(f"""
        SELECT id, name, normalized_name
        FROM sales_persons
        WHERE name IN ({placeholders})
    """, names)
    results = cursor.fetchall()
    cursor.close()
    return results


def count_relationships(conn, sales_person_id: str) -> int:
    """Count total relationships for a SalesPerson."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM jobs WHERE sales_person_id = %s) +
            (SELECT COUNT(*) FROM booked_opportunities WHERE sales_person_id = %s) +
            (SELECT COUNT(*) FROM lead_status WHERE sales_person_id = %s) +
            (SELECT COUNT(*) FROM user_performance WHERE sales_person_id = %s) +
            (SELECT COUNT(*) FROM sales_performance WHERE sales_person_id = %s) as total
    """, (sales_person_id, sales_person_id, sales_person_id, sales_person_id, sales_person_id))
    
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else 0


def merge_sales_person_variations(conn, canonical_name: str, variation_names: list):
    """Merge SalesPerson variations into canonical record."""
    cursor = conn.cursor()
    
    # Find all variation records
    all_names = [canonical_name] + variation_names
    records = find_sales_persons_by_names(conn, all_names)
    
    if len(records) < 2:
        logger.info(f"Only {len(records)} record(s) found for {canonical_name}, skipping merge")
        cursor.close()
        return 0
    
    # Find canonical record (prefer exact match, then most relationships)
    canonical_id = None
    canonical_record = None
    
    for sp_id, sp_name, sp_normalized in records:
        if sp_name == canonical_name:
            canonical_id = sp_id
            canonical_record = (sp_id, sp_name, sp_normalized)
            break
    
    if not canonical_id:
        # Use record with most relationships
        best_record = None
        best_count = -1
        for sp_id, sp_name, sp_normalized in records:
            count = count_relationships(conn, sp_id)
            if count > best_count:
                best_count = count
                best_record = (sp_id, sp_name, sp_normalized)
        canonical_id = best_record[0]
        canonical_record = best_record
        logger.info(f"Using {best_record[1]} as canonical (most relationships: {best_count})")
    
    # Update canonical name if needed
    if canonical_record[1] != canonical_name:
        cursor.execute("""
            UPDATE sales_persons
            SET name = %s, normalized_name = %s, updated_at = NOW()
            WHERE id = %s
        """, (canonical_name, canonical_name.lower().strip(), canonical_id))
        logger.info(f"Updated canonical name to: {canonical_name}")
    
    # Merge relationships from duplicates
    duplicates = [r for r in records if r[0] != canonical_id]
    total_updated = 0
    
    for dup_id, dup_name, dup_normalized in duplicates:
        # Update jobs
        cursor.execute("""
            UPDATE jobs SET sales_person_id = %s WHERE sales_person_id = %s
        """, (canonical_id, dup_id))
        jobs_updated = cursor.rowcount
        
        # Update booked_opportunities
        cursor.execute("""
            UPDATE booked_opportunities SET sales_person_id = %s WHERE sales_person_id = %s
        """, (canonical_id, dup_id))
        bo_updated = cursor.rowcount
        
        # Update lead_status
        cursor.execute("""
            UPDATE lead_status SET sales_person_id = %s WHERE sales_person_id = %s
        """, (canonical_id, dup_id))
        ls_updated = cursor.rowcount
        
        # Update user_performance
        cursor.execute("""
            UPDATE user_performance SET sales_person_id = %s WHERE sales_person_id = %s
        """, (canonical_id, dup_id))
        up_updated = cursor.rowcount
        
        # Update sales_performance
        cursor.execute("""
            UPDATE sales_performance SET sales_person_id = %s WHERE sales_person_id = %s
        """, (canonical_id, dup_id))
        spf_updated = cursor.rowcount
        
        # Update names in related tables
        cursor.execute("""
            UPDATE sales_performance SET name = %s WHERE name = %s
        """, (canonical_name, dup_name))
        spf_names_updated = cursor.rowcount
        
        cursor.execute("""
            UPDATE user_performance SET name = %s WHERE name = %s
        """, (canonical_name, dup_name))
        up_names_updated = cursor.rowcount
        
        total_updated += jobs_updated + bo_updated + ls_updated + up_updated + spf_updated
        
        logger.info(f"Merged {dup_name} into {canonical_name}: "
                   f"{jobs_updated} jobs, {bo_updated} BO, {ls_updated} LS, "
                   f"{up_updated} UP, {spf_updated} SPF, "
                   f"{spf_names_updated} SPF names, {up_names_updated} UP names")
        
        # Delete duplicate SalesPerson
        cursor.execute("DELETE FROM sales_persons WHERE id = %s", (dup_id,))
        logger.info(f"Deleted duplicate SalesPerson: {dup_name}")
    
    conn.commit()
    cursor.close()
    return total_updated


def main():
    """Main merge function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Merge SalesPerson name variations')
    parser.add_argument('--force', action='store_true',
                       help='Force execution even if already run')
    
    args = parser.parse_args()
    
    logger.info("Starting SalesPerson name variation merge")
    conn = get_db_connection()
    
    try:
        # Check if script should run (idempotency check)
        if not check_and_log_execution(conn, SCRIPT_NAME, force=args.force,
                                       notes="Merge SalesPerson name variations"):
            return 0
        
        # Check if there's any work to do
        cursor = conn.cursor()
        all_names = []
        for canonical_name, variation_names in NAME_VARIATIONS.items():
            all_names.extend([canonical_name] + variation_names)
        
        placeholders = ','.join(['%s'] * len(all_names))
        cursor.execute(f"""
            SELECT COUNT(DISTINCT name)
            FROM sales_persons
            WHERE name IN ({placeholders})
        """, all_names)
        result = cursor.fetchone()
        distinct_count = result[0] if result else 0
        cursor.close()
        
        if distinct_count <= len(NAME_VARIATIONS):
            logger.info("No variations found to merge. All SalesPerson names are already canonical.")
            return 0
        
        total_merged = 0
        
        for canonical_name, variation_names in NAME_VARIATIONS.items():
            log_step("Merge", f"Merging variations for: {canonical_name}")
            merged = merge_sales_person_variations(conn, canonical_name, variation_names)
            total_merged += merged
        
        log_success(f"Name variation merge complete: {total_merged} relationships updated")
        return 0
        
    except Exception as e:
        log_error(f"Merge failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

