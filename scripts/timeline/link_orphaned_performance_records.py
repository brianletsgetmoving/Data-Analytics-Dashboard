#!/usr/bin/env python3
"""
Create migration to link orphaned UserPerformance and SalesPerformance records 
to SalesPerson using improved name matching.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection
from src.utils.name_normalization import find_best_match, calculate_name_similarity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_all_sales_persons(conn):
    """Get all SalesPerson records."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, normalized_name
        FROM sales_persons
        ORDER BY name
    """)
    results = cursor.fetchall()
    cursor.close()
    return results


def link_orphaned_user_performance(conn, dry_run: bool = True):
    """Link orphaned UserPerformance records to SalesPerson."""
    cursor = conn.cursor()
    
    # Get all orphaned UserPerformance records
    cursor.execute("""
        SELECT id, name
        FROM user_performance
        WHERE sales_person_id IS NULL
        ORDER BY name
    """)
    orphaned_records = cursor.fetchall()
    
    # Get all SalesPerson records
    sales_persons = get_all_sales_persons(conn)
    sales_person_list = [(sp[0], sp[1]) for sp in sales_persons]
    
    linked_count = 0
    failed_count = 0
    updates = []
    
    for up_id, up_name in orphaned_records:
        match = find_best_match(up_name, sales_person_list)
        
        if match:
            sp_id, score, match_type = match
            updates.append({
                'user_performance_id': up_id,
                'user_performance_name': up_name,
                'sales_person_id': sp_id,
                'sales_person_name': next(sp[1] for sp in sales_persons if sp[0] == sp_id),
                'similarity_score': score,
                'match_type': match_type
            })
            
            if not dry_run:
                cursor.execute("""
                    UPDATE user_performance
                    SET sales_person_id = %s, updated_at = NOW()
                    WHERE id = %s
                """, (sp_id, up_id))
                linked_count += 1
                logger.info(f"Linked UserPerformance '{up_name}' to SalesPerson '{updates[-1]['sales_person_name']}' "
                          f"(score: {score:.2f}, type: {match_type})")
            else:
                linked_count += 1
                logger.info(f"[DRY RUN] Would link UserPerformance '{up_name}' to SalesPerson '{updates[-1]['sales_person_name']}' "
                          f"(score: {score:.2f}, type: {match_type})")
        else:
            failed_count += 1
            logger.warning(f"No match found for UserPerformance '{up_name}'")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return {
        'linked': linked_count,
        'failed': failed_count,
        'updates': updates
    }


def link_orphaned_sales_performance(conn, dry_run: bool = True):
    """Link orphaned SalesPerformance records to SalesPerson."""
    cursor = conn.cursor()
    
    # Get all orphaned SalesPerformance records
    cursor.execute("""
        SELECT id, name
        FROM sales_performance
        WHERE sales_person_id IS NULL
        ORDER BY name
    """)
    orphaned_records = cursor.fetchall()
    
    # Get all SalesPerson records
    sales_persons = get_all_sales_persons(conn)
    sales_person_list = [(sp[0], sp[1]) for sp in sales_persons]
    
    linked_count = 0
    failed_count = 0
    updates = []
    
    for spf_id, spf_name in orphaned_records:
        match = find_best_match(spf_name, sales_person_list)
        
        if match:
            sp_id, score, match_type = match
            updates.append({
                'sales_performance_id': spf_id,
                'sales_performance_name': spf_name,
                'sales_person_id': sp_id,
                'sales_person_name': next(sp[1] for sp in sales_persons if sp[0] == sp_id),
                'similarity_score': score,
                'match_type': match_type
            })
            
            if not dry_run:
                cursor.execute("""
                    UPDATE sales_performance
                    SET sales_person_id = %s, updated_at = NOW()
                    WHERE id = %s
                """, (sp_id, spf_id))
                linked_count += 1
                logger.info(f"Linked SalesPerformance '{spf_name}' to SalesPerson '{updates[-1]['sales_person_name']}' "
                          f"(score: {score:.2f}, type: {match_type})")
            else:
                linked_count += 1
                logger.info(f"[DRY RUN] Would link SalesPerformance '{spf_name}' to SalesPerson '{updates[-1]['sales_person_name']}' "
                          f"(score: {score:.2f}, type: {match_type})")
        else:
            failed_count += 1
            logger.warning(f"No match found for SalesPerformance '{spf_name}'")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return {
        'linked': linked_count,
        'failed': failed_count,
        'updates': updates
    }


def main():
    """Main linking function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Link orphaned performance records')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the updates (overrides dry-run)')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
        logger.info("Linking orphaned UserPerformance records...")
        up_results = link_orphaned_user_performance(conn, dry_run=dry_run)
        
        logger.info("Linking orphaned SalesPerformance records...")
        spf_results = link_orphaned_sales_performance(conn, dry_run=dry_run)
        
        # Print summary
        print("\n" + "="*80)
        print("LINKING SUMMARY")
        print("="*80)
        print(f"UserPerformance:")
        print(f"  Linked: {up_results['linked']}")
        print(f"  Failed: {up_results['failed']}")
        print(f"SalesPerformance:")
        print(f"  Linked: {spf_results['linked']}")
        print(f"  Failed: {spf_results['failed']}")
        print(f"Total linked: {up_results['linked'] + spf_results['linked']}")
        print(f"Total failed: {up_results['failed'] + spf_results['failed']}")
        print("="*80 + "\n")
        
        if dry_run:
            logger.info("Dry run complete. Review the output and run with --execute to apply changes.")
        else:
            logger.info("Linking complete!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Linking failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

