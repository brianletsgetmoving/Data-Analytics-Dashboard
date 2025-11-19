#!/usr/bin/env python3
"""
Remove normalized_name column from Branch model.
"""

import sys
from pathlib import Path
import psycopg2
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "remove_branch_normalized_name"


def remove_normalized_name_column(conn, dry_run: bool = True) -> bool:
    """Remove normalized_name column from branches table."""
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'branches' 
                AND column_name = 'normalized_name'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            logger.info("Column 'normalized_name' does not exist in 'branches' table")
            return True
        
        if dry_run:
            logger.info("[DRY RUN] Would remove column 'normalized_name' from 'branches' table")
            return True
        
        # Drop index first if it exists
        cursor.execute("""
            DROP INDEX IF EXISTS branches_normalized_name_idx
        """)
        logger.info("Dropped index on normalized_name (if it existed)")
        
        # Remove column
        cursor.execute("""
            ALTER TABLE branches DROP COLUMN normalized_name
        """)
        conn.commit()
        
        logger.info("Successfully removed 'normalized_name' column from 'branches' table")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error removing column: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove normalized_name from Branch')
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
        logger.info("REMOVE BRANCH NORMALIZED_NAME")
        logger.info("="*80)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        remove_normalized_name_column(conn, dry_run)
        
        logger.info("\n" + "="*80)
        logger.info("COMPLETE")
        logger.info("="*80)
        
        if not dry_run:
            check_and_log_execution(conn, SCRIPT_NAME, log_execution=True)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

