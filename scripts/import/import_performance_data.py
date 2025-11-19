#!/usr/bin/env python3
"""
Import performance data from CSVs using sales-performance naming convention.
Overwrites UserPerformance and SalesPerformance tables.
"""

import sys
from pathlib import Path
import psycopg2
import pandas as pd
import logging
from typing import Dict, Optional
from decimal import Decimal
import re
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "import_performance_data"

# Paths to CSV files
RINGCENTRAL_CSV = Path(__file__).parent.parent.parent / "data/raw/RingCentral_PR_Users_Users_11_17_2025_3_24_34_PM.xlsx - Users.csv"
SALES_PERFORMANCE_CSV = Path(__file__).parent.parent.parent / "data/raw/sales-person-performance (1).xlsx - data (1).csv"


def clean_numeric_value(value) -> Optional[Decimal]:
    """Clean and convert numeric values, removing $ and commas."""
    if pd.isna(value) or value is None:
        return None
    
    # Convert to string and clean
    str_value = str(value).strip()
    
    # Remove $ and commas
    str_value = str_value.replace('$', '').replace(',', '').strip()
    
    # Remove % if present (for percentages)
    if str_value.endswith('%'):
        str_value = str_value[:-1].strip()
    
    if not str_value or str_value == '':
        return None
    
    try:
        return Decimal(str_value)
    except:
        return None


def clean_percentage(value) -> Optional[Decimal]:
    """Clean percentage values."""
    if pd.isna(value) or value is None:
        return None
    
    str_value = str(value).strip()
    
    # Remove % if present
    if str_value.endswith('%'):
        str_value = str_value[:-1].strip()
    
    if not str_value or str_value == '':
        return None
    
    try:
        return Decimal(str_value)
    except:
        return None


def parse_time_string(time_str) -> Optional[str]:
    """Parse time string like '00:04:20' to keep as string."""
    if pd.isna(time_str) or time_str is None:
        return None
    
    str_value = str(time_str).strip()
    if not str_value or str_value == '':
        return None
    
    return str_value


def create_or_update_salesperson(conn, name: str, dry_run: bool = True) -> Optional[str]:
    """Create or update SalesPerson record, return ID."""
    cursor = conn.cursor()
    
    try:
        # Check if exists
        cursor.execute("""
            SELECT id FROM sales_persons WHERE name = %s
        """, (name,))
        result = cursor.fetchone()
        
        if result:
            salesperson_id = result[0]
            logger.debug(f"SalesPerson '{name}' already exists: {salesperson_id}")
            return salesperson_id
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create SalesPerson: {name}")
            return None
        
        # Create new SalesPerson
        cursor.execute("""
            INSERT INTO sales_persons (id, name, created_at, updated_at)
            VALUES (gen_random_uuid(), %s, NOW(), NOW())
            RETURNING id
        """, (name,))
        salesperson_id = cursor.fetchone()[0]
        conn.commit()
        
        logger.info(f"Created SalesPerson: {name} ({salesperson_id})")
        return salesperson_id
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating SalesPerson '{name}': {e}")
        return None
    finally:
        cursor.close()


def import_sales_performance(conn, dry_run: bool = True) -> int:
    """Import SalesPerformance data from CSV (primary source for naming)."""
    if not SALES_PERFORMANCE_CSV.exists():
        logger.error(f"Sales performance CSV not found: {SALES_PERFORMANCE_CSV}")
        return 0
    
    logger.info(f"Reading sales performance CSV: {SALES_PERFORMANCE_CSV}")
    df = pd.read_csv(SALES_PERFORMANCE_CSV)
    
    # Clean column names (remove spaces, handle special chars)
    # Important: CSV has trailing spaces in column names
    df.columns = df.columns.str.strip()
    
    # Debug: print column names
    logger.debug(f"CSV columns: {list(df.columns)}")
    
    logger.info(f"Found {len(df)} rows in sales performance CSV")
    
    if dry_run:
        logger.info("[DRY RUN] Would import sales performance data")
        return len(df)
    
    cursor = conn.cursor()
    imported = 0
    
    try:
        # Clear existing data
        cursor.execute("TRUNCATE TABLE sales_performance CASCADE")
        logger.info("Cleared existing sales_performance data")
        
        for idx, row in df.iterrows():
            try:
                # Get Name column (handle variations with trailing spaces)
                # CSV has "Name        " with trailing spaces
                name = None
                for col in df.columns:
                    col_clean = col.strip().lower()
                    if col_clean == 'name':
                        if pd.notna(row.get(col)):
                            name = str(row[col]).strip()
                        break
                
                if not name:
                    logger.warning(f"Row {idx + 1}: Missing name, skipping")
                    continue
                
                # Create/update SalesPerson
                salesperson_id = create_or_update_salesperson(conn, name, dry_run=False)
                
                # Clean numeric values
                leads_received = int(clean_numeric_value(row.get('# Leads Received', 0)) or 0)
                bad = int(clean_numeric_value(row.get('Bad', 0)) or 0)
                percent_bad = clean_percentage(row.get('% Bad'))
                sent = int(clean_numeric_value(row.get('Sent', 0)) or 0)
                percent_sent = clean_percentage(row.get('% Sent'))
                pending = int(clean_numeric_value(row.get('Pending', 0)) or 0)
                percent_pending = clean_percentage(row.get('% Pending'))
                booked = int(clean_numeric_value(row.get('Booked', 0)) or 0)
                percent_booked = clean_percentage(row.get('% Booked'))
                lost = int(clean_numeric_value(row.get('Lost', 0)) or 0)
                percent_lost = clean_percentage(row.get('% Lost'))
                cancelled = int(clean_numeric_value(row.get('Cancelled', 0)) or 0)
                percent_cancelled = clean_percentage(row.get('% Cancelled'))
                booked_total = clean_numeric_value(row.get('Booked Total'))
                average_booking = clean_numeric_value(row.get('Average Booking'))
                
                # Insert or update
                cursor.execute("""
                    INSERT INTO sales_performance (
                        id, name, sales_person_id,
                        leads_received, bad, percent_bad,
                        sent, percent_sent,
                        pending, percent_pending,
                        booked, percent_booked,
                        lost, percent_lost,
                        cancelled, percent_cancelled,
                        booked_total, average_booking,
                        created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s,
                        NOW(), NOW()
                    )
                    ON CONFLICT (name) DO UPDATE SET
                        sales_person_id = EXCLUDED.sales_person_id,
                        leads_received = EXCLUDED.leads_received,
                        bad = EXCLUDED.bad,
                        percent_bad = EXCLUDED.percent_bad,
                        sent = EXCLUDED.sent,
                        percent_sent = EXCLUDED.percent_sent,
                        pending = EXCLUDED.pending,
                        percent_pending = EXCLUDED.percent_pending,
                        booked = EXCLUDED.booked,
                        percent_booked = EXCLUDED.percent_booked,
                        lost = EXCLUDED.lost,
                        percent_lost = EXCLUDED.percent_lost,
                        cancelled = EXCLUDED.cancelled,
                        percent_cancelled = EXCLUDED.percent_cancelled,
                        booked_total = EXCLUDED.booked_total,
                        average_booking = EXCLUDED.average_booking,
                        updated_at = NOW()
                """, (
                    name, salesperson_id,
                    leads_received, bad, percent_bad,
                    sent, percent_sent,
                    pending, percent_pending,
                    booked, percent_booked,
                    lost, percent_lost,
                    cancelled, percent_cancelled,
                    booked_total, average_booking
                ))
                
                imported += 1
                
            except Exception as e:
                logger.error(f"Error importing row {idx + 1}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Imported {imported} sales performance records")
        return imported
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error importing sales performance: {e}")
        raise
    finally:
        cursor.close()


def match_name_to_sales_performance(ringcentral_name: str, sales_performance_names: list) -> Optional[str]:
    """Match RingCentral name to sales-performance format."""
    if not ringcentral_name:
        return None
    
    # Try exact match first
    if ringcentral_name in sales_performance_names:
        return ringcentral_name
    
    # Try fuzzy matching - extract first name/last name
    # RingCentral format: "Alejandro (Spanish & French)"
    # Sales-performance format: "Alejandro"
    
    # Extract name before parentheses
    base_name = ringcentral_name.split('(')[0].strip()
    
    # Try matching base name
    for sp_name in sales_performance_names:
        if base_name.lower() == sp_name.lower():
            return sp_name
        if base_name.lower() in sp_name.lower() or sp_name.lower() in base_name.lower():
            return sp_name
    
    return None


def import_user_performance(conn, dry_run: bool = True) -> int:
    """Import UserPerformance data from RingCentral CSV, matching to sales-performance names."""
    if not RINGCENTRAL_CSV.exists():
        logger.error(f"RingCentral CSV not found: {RINGCENTRAL_CSV}")
        return 0
    
    logger.info(f"Reading RingCentral CSV: {RINGCENTRAL_CSV}")
    df = pd.read_csv(RINGCENTRAL_CSV)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    logger.info(f"Found {len(df)} rows in RingCentral CSV")
    
    # Get sales-performance names for matching
    if SALES_PERFORMANCE_CSV.exists():
        sp_df = pd.read_csv(SALES_PERFORMANCE_CSV)
        sp_df.columns = sp_df.columns.str.strip()
        # Try different column name variations
        name_col = None
        for col in sp_df.columns:
            if col.lower() in ['name', 'name ']:
                name_col = col
                break
        if name_col:
            sales_performance_names = [str(name).strip() for name in sp_df[name_col].dropna().unique()]
        else:
            logger.warning(f"Could not find 'Name' column in sales performance CSV. Columns: {list(sp_df.columns)}")
            sales_performance_names = []
    else:
        sales_performance_names = []
    
    if dry_run:
        logger.info("[DRY RUN] Would import user performance data")
        return len(df)
    
    cursor = conn.cursor()
    imported = 0
    
    try:
        # Clear existing data
        cursor.execute("TRUNCATE TABLE user_performance CASCADE")
        logger.info("Cleared existing user_performance data")
        
        for idx, row in df.iterrows():
            try:
                ringcentral_name = str(row['Name']).strip() if pd.notna(row.get('Name')) else None
                if not ringcentral_name:
                    logger.warning(f"Row {idx + 1}: Missing name, skipping")
                    continue
                
                # Match to sales-performance format
                matched_name = match_name_to_sales_performance(ringcentral_name, sales_performance_names)
                if not matched_name:
                    # Use RingCentral name if no match found
                    matched_name = ringcentral_name
                    logger.warning(f"Could not match '{ringcentral_name}' to sales-performance format, using as-is")
                
                # Create/update SalesPerson with matched name
                salesperson_id = create_or_update_salesperson(conn, matched_name, dry_run=False)
                
                # Parse data
                user_status = str(row.get('User Status', '')).strip() if pd.notna(row.get('User Status')) else None
                total_calls = int(clean_numeric_value(row.get('Total Calls', 0)) or 0)
                avg_calls_per_day = clean_numeric_value(row.get('Avg. Calls/Day'))
                inbound_count = int(clean_numeric_value(row.get('# Inbound', 0)) or 0)
                outbound_count = int(clean_numeric_value(row.get('# Outbound', 0)) or 0)
                missed_percent = clean_percentage(row.get('% Missed (w/VM)'))
                avg_handle_time = parse_time_string(row.get('Avg. Handle Time'))
                
                # Insert or update
                cursor.execute("""
                    INSERT INTO user_performance (
                        id, name, sales_person_id,
                        user_status, total_calls, avg_calls_per_day,
                        inbound_count, outbound_count,
                        missed_percent, avg_handle_time,
                        created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s,
                        NOW(), NOW()
                    )
                    ON CONFLICT (name) DO UPDATE SET
                        sales_person_id = EXCLUDED.sales_person_id,
                        user_status = EXCLUDED.user_status,
                        total_calls = EXCLUDED.total_calls,
                        avg_calls_per_day = EXCLUDED.avg_calls_per_day,
                        inbound_count = EXCLUDED.inbound_count,
                        outbound_count = EXCLUDED.outbound_count,
                        missed_percent = EXCLUDED.missed_percent,
                        avg_handle_time = EXCLUDED.avg_handle_time,
                        updated_at = NOW()
                """, (
                    ringcentral_name, salesperson_id,  # Keep original RingCentral name in user_performance
                    user_status, total_calls, avg_calls_per_day,
                    inbound_count, outbound_count,
                    missed_percent, avg_handle_time
                ))
                
                imported += 1
                
            except Exception as e:
                logger.error(f"Error importing row {idx + 1}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Imported {imported} user performance records")
        return imported
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error importing user performance: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import performance data from CSVs')
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
        logger.info("IMPORT PERFORMANCE DATA")
        logger.info("="*80)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Step 1: Import SalesPerformance (primary source)
        logger.info("\nStep 1: Importing SalesPerformance data...")
        sales_perf_count = import_sales_performance(conn, dry_run)
        
        # Step 2: Import UserPerformance (match to sales-performance names)
        logger.info("\nStep 2: Importing UserPerformance data...")
        user_perf_count = import_user_performance(conn, dry_run)
        
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"SalesPerformance records imported: {sales_perf_count}")
        logger.info(f"UserPerformance records imported: {user_perf_count}")
        logger.info("="*80)
        
        if not dry_run:
            check_and_log_execution(conn, SCRIPT_NAME, log_execution=True)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

