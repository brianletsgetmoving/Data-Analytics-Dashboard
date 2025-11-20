#!/usr/bin/env python3
"""
Clean up SalesPerson records to match sales-person-performance CSV as source of truth.
Removes any SalesPerson records that don't exist in the CSV.
"""
import sys
from pathlib import Path
import pandas as pd
import psycopg2
import logging
from typing import Set, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the CSV file (source of truth)
CSV_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "sales-person-performance (1).xlsx - data (1).csv"


def get_valid_names_from_csv() -> Set[str]:
    """Extract valid SalesPerson names from the CSV file."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
    
    logger.info(f"Reading CSV file: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    
    # Clean column names (remove spaces)
    df.columns = df.columns.str.strip()
    
    # Get Name column
    name_col = None
    for col in df.columns:
        if col.strip().lower() == 'name':
            name_col = col
            break
    
    if not name_col:
        raise ValueError(f"Could not find 'Name' column in CSV. Columns: {list(df.columns)}")
    
    # Extract names and clean them
    valid_names = set()
    for name in df[name_col].dropna():
        cleaned_name = str(name).strip()
        if cleaned_name:
            valid_names.add(cleaned_name)
    
    logger.info(f"Found {len(valid_names)} valid names in CSV")
    return valid_names


def get_salesperson_records(conn) -> List[tuple]:
    """Get all SalesPerson records from database."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name 
            FROM sales_persons 
            ORDER BY name
        """)
        return cursor.fetchall()
    finally:
        cursor.close()


def find_salespersons_to_delete(conn, valid_names: Set[str]) -> List[str]:
    """Find SalesPerson IDs that should be deleted."""
    all_salespersons = get_salesperson_records(conn)
    to_delete = []
    seen_names = set()  # Track names we've seen to handle duplicates
    
    logger.info(f"Checking {len(all_salespersons)} SalesPerson records...")
    
    for sp_id, sp_name in all_salespersons:
        cleaned_name = str(sp_name).strip() if sp_name else ""
        
        # Check if name matches any valid name (exact match after trimming)
        if cleaned_name not in valid_names:
            to_delete.append(sp_id)
            logger.debug(f"  Will delete: '{sp_name}' -> '{cleaned_name}' (id: {sp_id})")
        elif cleaned_name in seen_names:
            # This is a duplicate - keep the first one, delete this one
            to_delete.append(sp_id)
            logger.debug(f"  Will delete duplicate: '{sp_name}' (id: {sp_id})")
        else:
            seen_names.add(cleaned_name)
    
    logger.info(f"Found {len(to_delete)} SalesPerson records to delete")
    return to_delete


def ensure_salespersons_exist(conn, valid_names: Set[str], dry_run: bool = True) -> int:
    """Ensure SalesPerson records exist for all valid CSV names."""
    cursor = conn.cursor()
    created = 0
    
    try:
        for name in valid_names:
            # Check if exists (using TRIM to handle trailing spaces)
            cursor.execute("""
                SELECT id FROM sales_persons WHERE TRIM(name) = %s
            """, (name,))
            exists = cursor.fetchone()
            
            if not exists:
                if dry_run:
                    logger.debug(f"  Would create SalesPerson: '{name}'")
                else:
                    # Check if normalized_name column exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'sales_persons' 
                            AND column_name = 'normalized_name'
                        )
                    """)
                    has_normalized = cursor.fetchone()[0]
                    
                    if has_normalized:
                        # Use normalized name (lowercase, trimmed)
                        normalized = name.lower().strip()
                        cursor.execute("""
                            INSERT INTO sales_persons (id, name, normalized_name, created_at, updated_at)
                            VALUES (gen_random_uuid(), %s, %s, NOW(), NOW())
                            ON CONFLICT (name) DO NOTHING
                        """, (name, normalized))
                    else:
                        cursor.execute("""
                            INSERT INTO sales_persons (id, name, created_at, updated_at)
                            VALUES (gen_random_uuid(), %s, NOW(), NOW())
                            ON CONFLICT (name) DO NOTHING
                        """, (name,))
                    if cursor.rowcount > 0:
                        created += 1
        
        if not dry_run and created > 0:
            conn.commit()
            logger.info(f"✓ Created {created} new SalesPerson records")
        elif dry_run:
            logger.info(f"[DRY RUN] Would create {len(valid_names)} SalesPerson records (if missing)")
        
        return created
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating SalesPerson records: {e}")
        raise
    finally:
        cursor.close()


def delete_salespersons(conn, salesperson_ids: List[str], dry_run: bool = True) -> dict:
    """
    Delete SalesPerson records and return counts of affected records.
    Foreign keys should cascade, but we'll check what gets deleted.
    """
    if not salesperson_ids:
        logger.info("No SalesPerson records to delete")
        return {}
    
    cursor = conn.cursor()
    results = {}
    
    try:
        placeholders = ','.join(['%s'] * len(salesperson_ids))
        
        # Count affected records in related tables
        tables_to_check = [
            ('jobs', 'sales_person_id'),
            ('booked_opportunities', 'sales_person_id'),
            ('leads', 'sales_person_id'),
            ('sales_performance', 'sales_person_id'),
            ('user_performance', 'sales_person_id'),
        ]
        
        logger.info("Counting affected records in related tables...")
        for table_name, column_name in tables_to_check:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE {column_name} IN ({placeholders})
            """, salesperson_ids)
            count = cursor.fetchone()[0]
            results[table_name] = count
            if count > 0:
                logger.info(f"  {table_name}: {count:,} records will have {column_name} set to NULL")
        
        if dry_run:
            logger.info("[DRY RUN] Would delete SalesPerson records")
            return results
        
        # Delete SalesPerson records
        # Foreign keys should cascade or set to NULL
        logger.info("Deleting SalesPerson records...")
        cursor.execute(f"""
            DELETE FROM sales_persons 
            WHERE id IN ({placeholders})
        """, salesperson_ids)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"✓ Deleted {deleted_count:,} SalesPerson records")
        results['deleted_salespersons'] = deleted_count
        
        return results
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting SalesPerson records: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up SalesPerson records to match CSV')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    logger.info("="*80)
    logger.info("CLEANUP SALESPERSONS FROM CSV")
    logger.info("="*80)
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    # Get valid names from CSV
    valid_names = get_valid_names_from_csv()
    logger.info(f"Valid names: {sorted(list(valid_names))[:10]}..." if len(valid_names) > 10 else f"Valid names: {sorted(list(valid_names))}")
    
    # Connect to database
    conn = get_db_connection()
    
    try:
        # Step 1: Ensure all CSV names have SalesPerson records
        logger.info("")
        logger.info("Step 1: Ensuring SalesPerson records exist for all CSV names...")
        created_count = ensure_salespersons_exist(conn, valid_names, dry_run)
        
        # Step 2: Find SalesPersons to delete
        logger.info("")
        logger.info("Step 2: Finding SalesPerson records to delete...")
        salesperson_ids_to_delete = find_salespersons_to_delete(conn, valid_names)
        
        if not salesperson_ids_to_delete:
            logger.info("✓ All SalesPerson records match CSV - no cleanup needed")
            if created_count > 0:
                logger.info(f"✓ Created {created_count} new SalesPerson records")
            return
        
        # Show what will be deleted
        cursor = conn.cursor()
        try:
            placeholders = ','.join(['%s'] * len(salesperson_ids_to_delete))
            cursor.execute(f"""
                SELECT name 
                FROM sales_persons 
                WHERE id IN ({placeholders})
                ORDER BY name
            """, salesperson_ids_to_delete)
            names_to_delete = [row[0] for row in cursor.fetchall()]
            logger.info(f"\nSalesPerson records to delete ({len(names_to_delete)}):")
            for name in names_to_delete[:20]:  # Show first 20
                logger.info(f"  - {name}")
            if len(names_to_delete) > 20:
                logger.info(f"  ... and {len(names_to_delete) - 20} more")
        finally:
            cursor.close()
        
        # Step 3: Delete SalesPersons
        logger.info("")
        logger.info("Step 3: Deleting SalesPerson records not in CSV...")
        results = delete_salespersons(conn, salesperson_ids_to_delete, dry_run)
        
        logger.info("")
        logger.info("="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        if created_count > 0:
            logger.info(f"SalesPerson records created: {created_count:,}")
        logger.info(f"SalesPerson records to delete: {len(salesperson_ids_to_delete):,}")
        for table, count in results.items():
            if table != 'deleted_salespersons' and count > 0:
                logger.info(f"  {table} records affected: {count:,}")
        if not dry_run:
            logger.info(f"  ✓ Deleted: {results.get('deleted_salespersons', 0):,}")
        logger.info("="*80)
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()

