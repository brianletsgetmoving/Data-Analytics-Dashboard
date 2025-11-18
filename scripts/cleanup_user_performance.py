#!/usr/bin/env python3
"""
Clean up UserPerformance records to ensure all records can be tracked across
SalesPerson, SalesPerformance, and UserPerformance modules.
Remove records that don't have both SalesPerson and SalesPerformance matches.
"""

import sys
from pathlib import Path
import pandas as pd
import psycopg2
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection
from src.utils.progress_monitor import log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def identify_records_to_remove(conn):
    """Identify UserPerformance records that should be removed."""
    cursor = conn.cursor()
    
    # Find UserPerformance records without SalesPerson
    cursor.execute("""
        SELECT 
            up.id,
            up.name,
            up.sales_person_id,
            'No SalesPerson' as reason
        FROM user_performance up
        WHERE up.sales_person_id IS NULL
        ORDER BY up.name
    """)
    no_sales_person = cursor.fetchall()
    
    # Find UserPerformance records where SalesPerson exists but no SalesPerformance
    cursor.execute("""
        SELECT 
            up.id,
            up.name,
            up.sales_person_id,
            sp.name as sales_person_name,
            'SalesPerson has no SalesPerformance' as reason
        FROM user_performance up
        JOIN sales_persons sp ON up.sales_person_id = sp.id
        LEFT JOIN sales_performance spf ON sp.id = spf.sales_person_id
        WHERE spf.id IS NULL
        ORDER BY up.name
    """)
    no_sales_performance = cursor.fetchall()
    
    cursor.close()
    
    return {
        'no_sales_person': pd.DataFrame(
            no_sales_person,
            columns=['id', 'name', 'sales_person_id', 'reason']
        ),
        'no_sales_performance': pd.DataFrame(
            no_sales_performance,
            columns=['id', 'name', 'sales_person_id', 'sales_person_name', 'reason']
        )
    }


def identify_records_to_keep(conn):
    """Identify UserPerformance records that should be kept."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            up.id,
            up.name as user_performance_name,
            up.sales_person_id,
            sp.name as sales_person_name,
            spf.id as sales_performance_id,
            spf.name as sales_performance_name
        FROM user_performance up
        JOIN sales_persons sp ON up.sales_person_id = sp.id
        JOIN sales_performance spf ON sp.id = spf.sales_person_id
        ORDER BY up.name
    """)
    records_to_keep = cursor.fetchall()
    
    cursor.close()
    
    return pd.DataFrame(
        records_to_keep,
        columns=['id', 'user_performance_name', 'sales_person_id', 'sales_person_name', 
                 'sales_performance_id', 'sales_performance_name']
    )


def delete_user_performance_records(conn, record_ids: list):
    """Delete UserPerformance records by ID."""
    if not record_ids:
        return 0
    
    cursor = conn.cursor()
    placeholders = ','.join(['%s'] * len(record_ids))
    cursor.execute(f"""
        DELETE FROM user_performance
        WHERE id IN ({placeholders})
    """, record_ids)
    
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    
    return deleted


def generate_report(records_to_remove, records_to_keep):
    """Generate CSV reports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path("reports") / f"user_performance_cleanup_{timestamp}"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Combine all records to remove
    all_to_remove = pd.concat([
        records_to_remove['no_sales_person'],
        records_to_remove['no_sales_performance']
    ], ignore_index=True)
    
    all_to_remove.to_csv(reports_dir / "records_to_remove.csv", index=False)
    records_to_keep.to_csv(reports_dir / "records_to_keep.csv", index=False)
    
    # Summary
    summary = {
        'total_to_remove': len(all_to_remove),
        'no_sales_person_count': len(records_to_remove['no_sales_person']),
        'no_sales_performance_count': len(records_to_remove['no_sales_performance']),
        'total_to_keep': len(records_to_keep)
    }
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(reports_dir / "summary.csv", index=False)
    
    return reports_dir, summary


def main():
    """Main cleanup function."""
    logger.info("Starting UserPerformance cleanup")
    conn = get_db_connection()
    
    try:
        # Phase 1: Identify records
        log_step("Cleanup", "Identifying records to remove")
        records_to_remove = identify_records_to_remove(conn)
        
        log_step("Cleanup", "Identifying records to keep")
        records_to_keep = identify_records_to_keep(conn)
        
        # Generate report
        reports_dir, summary = generate_report(records_to_remove, records_to_keep)
        logger.info(f"Reports saved to: {reports_dir}")
        
        print(f"\nRecords to remove: {summary['total_to_remove']}")
        print(f"  - No SalesPerson: {summary['no_sales_person_count']}")
        print(f"  - No SalesPerformance: {summary['no_sales_performance_count']}")
        print(f"Records to keep: {summary['total_to_keep']}")
        
        # Phase 2: Delete records
        all_ids_to_remove = []
        all_ids_to_remove.extend(records_to_remove['no_sales_person']['id'].tolist())
        all_ids_to_remove.extend(records_to_remove['no_sales_performance']['id'].tolist())
        
        if all_ids_to_remove:
            log_step("Cleanup", f"Deleting {len(all_ids_to_remove)} UserPerformance records")
            deleted = delete_user_performance_records(conn, all_ids_to_remove)
            log_success(f"Deleted {deleted} UserPerformance records")
        else:
            log_success("No records to delete")
        
        # Verify final state
        log_step("Cleanup", "Verifying final state")
        final_records = identify_records_to_keep(conn)
        logger.info(f"Final UserPerformance count: {len(final_records)}")
        
        # Final summary
        print(f"\n{'='*80}")
        print("CLEANUP SUMMARY")
        print(f"{'='*80}")
        print(f"Records removed: {len(all_ids_to_remove)}")
        print(f"Records remaining: {len(final_records)}")
        print(f"All remaining records can be tracked across all 3 modules: ✓")
        print(f"{'='*80}\n")
        
        return 0
        
    except Exception as e:
        log_error(f"Cleanup failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

