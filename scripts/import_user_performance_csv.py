#!/usr/bin/env python3
"""
Import UserPerformance CSV file, overwriting existing data.
Links all records to SalesPerson records by name matching.
"""

import sys
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import uuid
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection
from src.utils.progress_monitor import log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_number(value):
    """Convert to integer."""
    if pd.isna(value) or value == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def clean_decimal(value):
    """Convert to decimal."""
    if pd.isna(value) or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def clean_percentage(value):
    """Remove % sign and convert to decimal."""
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, str):
        value = value.replace('%', '').strip()
        if value == '':
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_time(value):
    """Parse time string (e.g., '00:04:20') to text."""
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, str):
        return value.strip()
    return str(value)


def parse_csv(csv_path: Path) -> pd.DataFrame:
    """Parse and clean UserPerformance CSV."""
    log_step("Import", f"Parsing CSV: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Clean names
    df['name'] = df['Name'].str.strip()
    df['user_status'] = df['User Status'].str.strip()
    
    # Clean and convert numeric fields
    df['total_calls'] = df['Total Calls'].apply(clean_number)
    df['avg_calls_per_day'] = df['Avg. Calls/Day'].apply(clean_decimal)
    df['inbound_count'] = df['# Inbound'].apply(clean_number)
    df['outbound_count'] = df['# Outbound'].apply(clean_number)
    df['missed_percent'] = df['% Missed (w/VM) '].apply(clean_percentage)
    df['avg_handle_time'] = df['Avg. Handle Time'].apply(parse_time)
    
    logger.info(f"Parsed {len(df)} records from CSV")
    return df


def match_to_sales_person(conn, name: str) -> tuple:
    """
    Match CSV name to SalesPerson record.
    Returns (sales_person_id, matched_name) or (None, None) if no match.
    """
    cursor = conn.cursor()
    
    try:
        # Try exact match first
        cursor.execute("""
            SELECT id, name FROM sales_persons 
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
        """, (name,))
        result = cursor.fetchone()
        
        if result and len(result) >= 2:
            return result[0], result[1]
        
        # Try normalized match
        cursor.execute("""
            SELECT id, name FROM sales_persons 
            WHERE LOWER(TRIM(normalized_name)) = LOWER(TRIM(%s))
        """, (name,))
        result = cursor.fetchone()
        
        if result and len(result) >= 2:
            return result[0], result[1]
        
        # Try partial matches
        name_lower = name.lower().strip()
        
        # Handle specific variations
        name_mappings = {
            'alejandro (spanish & french)': 'alejandro',
            'andres (spanish)': 'andres i',
            'bobby s': 'bobby',
            'daud p': 'daud',
            'said elmi': 'said',
            'josephine orji': 'josephine o',
            'robert j': 'rob',
        }
        
        mapped_name = name_mappings.get(name_lower, name_lower)
        
        # Try with mapped name
        cursor.execute("""
            SELECT id, name FROM sales_persons 
            WHERE LOWER(TRIM(name)) = %s
               OR LOWER(TRIM(normalized_name)) = %s
        """, (mapped_name, mapped_name))
        result = cursor.fetchone()
        
        if result and len(result) >= 2:
            return result[0], result[1]
        
        # Try partial matches
        pattern_start = name_lower + '%'
        pattern_end = '%' + name_lower
        cursor.execute("""
            SELECT id, name FROM sales_persons 
            WHERE LOWER(TRIM(name)) LIKE %s
               OR LOWER(TRIM(name)) LIKE %s
               OR LOWER(TRIM(normalized_name)) LIKE %s
               OR LOWER(TRIM(normalized_name)) LIKE %s
        """, (pattern_start, pattern_end, pattern_start, pattern_end))
        result = cursor.fetchone()
        
        if result and len(result) >= 2:
            return result[0], result[1]
        
        return None, None
    finally:
        cursor.close()


def delete_all_user_performance(conn):
    """Delete all existing UserPerformance records."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_performance")
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    return deleted


def insert_user_performance(conn, records):
    """Insert UserPerformance records."""
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO user_performance (
            id, name, user_status, total_calls, avg_calls_per_day,
            inbound_count, outbound_count, missed_percent, avg_handle_time,
            sales_person_id, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
        )
    """
    
    execute_batch(cursor, insert_query, records, page_size=100)
    conn.commit()
    cursor.close()


def main():
    """Main import function."""
    csv_path = Path("/Users/buyer/Downloads/RingCentral_PR_Users_Users_11_17_2025_3_24_34_PM.xlsx - Users.csv")
    
    if not csv_path.exists():
        log_error(f"CSV file not found: {csv_path}")
        return 1
    
    logger.info("Starting UserPerformance import")
    conn = get_db_connection()
    
    try:
        # Parse CSV
        df = parse_csv(csv_path)
        
        # Delete all existing records
        log_step("Import", "Deleting existing UserPerformance records")
        deleted = delete_all_user_performance(conn)
        logger.info(f"Deleted {deleted} existing records")
        
        # Process each record
        log_step("Import", f"Processing {len(df)} records")
        records = []
        linked_count = 0
        unlinked_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            name = row['name']
            
            # Match to SalesPerson
            sp_id, matched_name = match_to_sales_person(conn, name)
            
            if sp_id:
                linked_count += 1
                if matched_name != name:
                    logger.info(f"Matched '{name}' to SalesPerson '{matched_name}'")
            else:
                unlinked_count += 1
                logger.info(f"No SalesPerson match for: {name} (new agent?)")
            
            # Prepare record
            up_id = str(uuid.uuid4())
            record = (
                up_id,
                row['name'],
                row['user_status'],
                row['total_calls'],
                row['avg_calls_per_day'],
                row['inbound_count'],
                row['outbound_count'],
                row['missed_percent'],
                row['avg_handle_time'],
                sp_id  # Can be None for new agents
            )
            records.append(record)
        
        # Insert all records
        log_step("Import", f"Inserting {len(records)} records")
        insert_user_performance(conn, records)
        
        # Summary
        log_success(f"UserPerformance import complete:")
        log_success(f"  Total records: {len(records)}")
        log_success(f"  Linked to SalesPerson: {linked_count}")
        log_success(f"  Unlinked (new agents): {unlinked_count}")
        
        if errors:
            log_error(f"  Errors: {len(errors)}")
            for err in errors:
                logger.error(f"    {err}")
        
        return 0
        
    except Exception as e:
        log_error(f"Import failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

