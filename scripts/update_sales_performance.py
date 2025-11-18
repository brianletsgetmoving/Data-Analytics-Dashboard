#!/usr/bin/env python3
"""
Update SalesPerformance with CSV data from SmartMoving.
Parses CSV, matches to SalesPerson records, and updates/creates records.
"""

import sys
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import uuid
from datetime import datetime
import logging
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection
from src.utils.progress_monitor import log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_number(value):
    """Remove commas and convert to integer."""
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, str):
        value = value.replace(',', '').replace('$', '').strip()
        if value == '':
            return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def clean_decimal(value):
    """Remove $, commas, and convert to decimal."""
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '').strip()
        if value == '':
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


def parse_csv(csv_path: Path) -> pd.DataFrame:
    """Parse and clean SalesPerformance CSV."""
    log_step("Import", f"Parsing CSV: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Clean names
    df['Name'] = df['Name'].str.strip()
    
    # Clean and convert numeric fields
    df['leads_received'] = df['# Leads Received'].apply(clean_number)
    df['bad'] = df['Bad'].apply(clean_number)
    df['percent_bad'] = df['% Bad'].apply(clean_percentage)
    df['sent'] = df['Sent'].apply(clean_number)
    df['percent_sent'] = df['% Sent'].apply(clean_percentage)
    df['pending'] = df['Pending'].apply(clean_number)
    df['percent_pending'] = df['% Pending'].apply(clean_percentage)
    df['booked'] = df['Booked'].apply(clean_number)
    df['percent_booked'] = df['% Booked'].apply(clean_percentage)
    df['lost'] = df['Lost'].apply(clean_number)
    df['percent_lost'] = df['% Lost'].apply(clean_percentage)
    df['cancelled'] = df['Cancelled'].apply(clean_number)
    df['percent_cancelled'] = df['% Cancelled'].apply(clean_percentage)
    df['booked_total'] = df['Booked Total'].apply(clean_decimal)
    df['average_booking'] = df['Average Booking'].apply(clean_decimal)
    
    # Rename Name column
    df['name'] = df['Name']
    
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
            'andres i': 'andres (spanish)',
            'asif': 'asif k',
            'aurie ': 'aurie a',
            'aurie': 'aurie a',
            'martin ': 'martin $',
            'martin': 'martin $',
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


def create_sales_person(conn, name: str) -> str:
    """Create new SalesPerson record."""
    cursor = conn.cursor()
    sp_id = str(uuid.uuid4())
    normalized = name.lower().strip()
    
    cursor.execute("""
        INSERT INTO sales_persons (id, name, normalized_name, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (sp_id, name, normalized))
    
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    if result:
        return result[0]
    return sp_id


def upsert_sales_performance(conn, row: pd.Series, sales_person_id: str):
    """Update or insert SalesPerformance record."""
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute("""
        SELECT id FROM sales_performance WHERE name = %s
    """, (row['name'],))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing
        cursor.execute("""
            UPDATE sales_performance SET
                sales_person_id = %s,
                leads_received = %s,
                bad = %s,
                percent_bad = %s,
                sent = %s,
                percent_sent = %s,
                pending = %s,
                percent_pending = %s,
                booked = %s,
                percent_booked = %s,
                lost = %s,
                percent_lost = %s,
                cancelled = %s,
                percent_cancelled = %s,
                booked_total = %s,
                average_booking = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (
            sales_person_id,
            row['leads_received'],
            row['bad'],
            row['percent_bad'],
            row['sent'],
            row['percent_sent'],
            row['pending'],
            row['percent_pending'],
            row['booked'],
            row['percent_booked'],
            row['lost'],
            row['percent_lost'],
            row['cancelled'],
            row['percent_cancelled'],
            row['booked_total'],
            row['average_booking'],
            existing[0]
        ))
    else:
        # Insert new
        spf_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO sales_performance (
                id, name, sales_person_id, leads_received, bad, percent_bad,
                sent, percent_sent, pending, percent_pending,
                booked, percent_booked, lost, percent_lost,
                cancelled, percent_cancelled, booked_total, average_booking,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
        """, (
            spf_id,
            row['name'],
            sales_person_id,
            row['leads_received'],
            row['bad'],
            row['percent_bad'],
            row['sent'],
            row['percent_sent'],
            row['pending'],
            row['percent_pending'],
            row['booked'],
            row['percent_booked'],
            row['lost'],
            row['percent_lost'],
            row['cancelled'],
            row['percent_cancelled'],
            row['booked_total'],
            row['average_booking']
        ))
    
    conn.commit()
    cursor.close()


def main():
    """Main import function."""
    csv_path = Path("/Users/buyer/Downloads/sales-person-performance (1).xlsx - data (1).csv")
    
    if not csv_path.exists():
        log_error(f"CSV file not found: {csv_path}")
        return 1
    
    logger.info("Starting SalesPerformance update")
    conn = get_db_connection()
    
    try:
        # Parse CSV
        df = parse_csv(csv_path)
        
        # Process each record
        log_step("Import", f"Processing {len(df)} records")
        created_sp = 0
        updated_spf = 0
        created_spf = 0
        errors = []
        
        for idx, row in df.iterrows():
            name = row['name']
            
            # Match to SalesPerson
            sp_id, matched_name = match_to_sales_person(conn, name)
            
            if not sp_id:
                # Create new SalesPerson
                log_step("Import", f"Creating SalesPerson for: {name}")
                sp_id = create_sales_person(conn, name)
                created_sp += 1
            elif matched_name != name:
                logger.info(f"Matched '{name}' to SalesPerson '{matched_name}'")
            
            # Check if SalesPerformance exists
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sales_performance WHERE name = %s", (name,))
            existing = cursor.fetchone()
            cursor.close()
            
            if existing:
                updated_spf += 1
            else:
                created_spf += 1
            
            # Upsert SalesPerformance
            try:
                upsert_sales_performance(conn, row, sp_id)
            except Exception as e:
                logger.error(f"Error processing {name}: {e}")
                errors.append({'name': name, 'error': str(e)})
        
        # Summary
        log_success(f"SalesPerformance update complete:")
        log_success(f"  Created SalesPersons: {created_sp}")
        log_success(f"  Created SalesPerformance: {created_spf}")
        log_success(f"  Updated SalesPerformance: {updated_spf}")
        
        if errors:
            log_error(f"  Errors: {len(errors)}")
            for err in errors:
                logger.error(f"    {err['name']}: {err['error']}")
        
        return 0
        
    except Exception as e:
        log_error(f"Update failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

