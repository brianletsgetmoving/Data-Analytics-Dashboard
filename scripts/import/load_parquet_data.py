"""
Load parquet files into PostgreSQL database tables.

This script loads all processed parquet files into their corresponding database tables.
It handles data type conversions and maps parquet column names to database column names.
"""

import os
import sys
import argparse
import logging
import uuid
from pathlib import Path
from typing import Optional

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import get_db_connection
from utils.script_execution import log_script_execution, script_already_executed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root directory (2 levels up from scripts/import/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'processed'


def map_job_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map parquet columns to database columns for jobs table."""
    column_mapping = {
        'job_id': 'job_id',
        'job_number': 'job_number',
        'opportunity_status': 'opportunity_status',
        'job_date': 'job_date',
        'sales_person_name': 'sales_person_name',
        'branch_name': 'branch_name',
        'job_type': 'job_type',
        'customer_name': 'customer_name',
        'customer_email': 'customer_email',
        'customer_phone': 'customer_phone',
        'referral_source': 'referral_source',
        'affiliate_name': 'affiliate_name',
        'created_at_utc': 'created_at_utc',
        'booked_at_utc': 'booked_at_utc',
        'hourly_rate_quoted': 'hourly_rate_quoted',
        'total_estimated_cost': 'total_estimated_cost',
        'actual_number_crew': 'actual_number_crew',
        'actual_number_trucks': 'actual_number_trucks',
        'hourly_rate_billed': 'hourly_rate_billed',
        'total_actual_cost': 'total_actual_cost',
        'origin_address': 'origin_address',
        'origin_street': 'origin_street',
        'origin_city': 'origin_city',
        'origin_state': 'origin_state',
        'origin_zip': 'origin_zip',
        'origin_type': 'origin_type',
        'destination_address': 'destination_address',
        'destination_street': 'destination_street',
        'destination_city': 'destination_city',
        'destination_state': 'destination_state',
        'destination_zip': 'destination_zip',
        'destination_type': 'destination_type',
        'is_duplicate': 'is_duplicate',
    }
    
    # Only keep columns that exist in both mapping and dataframe
    available_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
    df_mapped = df[list(available_mapping.keys())].copy()
    df_mapped = df_mapped.rename(columns=available_mapping)
    
    return df_mapped


def load_jobs(conn: psycopg2.extensions.connection, dry_run: bool = True) -> int:
    """Load job data from all year parquet files."""
    job_files = [
        '2019.xlsx - jobs.parquet',
        '2020.xlsx - jobs.parquet',
        '2021.xlsx - jobs.parquet',
        '2022.xlsx - jobs.parquet',
        '2023.xlsx - jobs.parquet',
        '2024.xlsx - jobs.parquet',
        '2025.xlsx - jobs.parquet',
    ]
    
    total_loaded = 0
    
    for job_file in job_files:
        file_path = DATA_DIR / job_file
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
        
        logger.info(f"Loading {job_file}...")
        df = pd.read_parquet(file_path)
        df_mapped = map_job_columns(df)
        
        # Convert datetime columns
        for col in ['job_date', 'created_at_utc', 'booked_at_utc']:
            if col in df_mapped.columns:
                df_mapped[col] = pd.to_datetime(df_mapped[col], errors='coerce')
        
        # Convert numeric columns
        for col in ['hourly_rate_quoted', 'total_estimated_cost', 'hourly_rate_billed', 'total_actual_cost']:
            if col in df_mapped.columns:
                df_mapped[col] = pd.to_numeric(df_mapped[col], errors='coerce')
        
        # Convert boolean columns
        if 'is_duplicate' in df_mapped.columns:
            df_mapped['is_duplicate'] = df_mapped['is_duplicate'].fillna(False).astype(bool)
        
        # Clean enum values (strip whitespace)
        if 'opportunity_status' in df_mapped.columns:
            df_mapped['opportunity_status'] = df_mapped['opportunity_status'].astype(str).str.strip()
            # Map to valid enum values or None
            valid_statuses = ['QUOTED', 'BOOKED', 'LOST', 'CANCELLED', 'CLOSED']
            df_mapped['opportunity_status'] = df_mapped['opportunity_status'].apply(
                lambda x: x if x in valid_statuses else None
            )
        
        # Replace NaN/NaT with None for PostgreSQL
        df_mapped = df_mapped.where(pd.notnull(df_mapped), None)
        
        # Convert datetime NaT to None explicitly
        for col in ['job_date', 'created_at_utc', 'booked_at_utc']:
            if col in df_mapped.columns:
                df_mapped[col] = df_mapped[col].apply(lambda x: None if pd.isna(x) else x)
        
        if dry_run:
            logger.info(f"DRY RUN: Would load {len(df_mapped)} rows from {job_file}")
            total_loaded += len(df_mapped)
        else:
            cursor = conn.cursor()
            try:
                # Get column names (exclude auto-generated columns)
                # id, created_at, updated_at need to be generated
                excluded_cols = {'created_at', 'updated_at', 'id'}
                columns = [col for col in df_mapped.columns if col not in excluded_cols]
                
                # Add auto-generated columns
                from datetime import datetime
                now = datetime.utcnow()
                if 'id' not in df_mapped.columns:
                    df_mapped['id'] = [str(uuid.uuid4()) for _ in range(len(df_mapped))]
                if 'created_at' not in df_mapped.columns:
                    df_mapped['created_at'] = now
                if 'updated_at' not in df_mapped.columns:
                    df_mapped['updated_at'] = now
                
                # Add these columns to the insert list
                columns.insert(0, 'id')
                columns.append('created_at')
                columns.append('updated_at')
                
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                
                # Prepare data for bulk insert, converting NaT/NaN to None
                def clean_value(val):
                    if pd.isna(val):
                        return None
                    if isinstance(val, pd.Timestamp) and pd.isna(val):
                        return None
                    return val
                
                # Only include columns we're inserting
                df_for_insert = df_mapped[columns]
                values = [tuple(clean_value(val) for val in row) for row in df_for_insert.values]
                
                # Use execute_values for bulk insert
                query = f"""
                    INSERT INTO jobs ({column_names})
                    VALUES %s
                    ON CONFLICT (job_id) DO NOTHING
                """
                
                execute_values(cursor, query, values, page_size=1000)
                conn.commit()
                loaded = cursor.rowcount
                total_loaded += loaded
                logger.info(f"Loaded {loaded} rows from {job_file}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Error loading {job_file}: {e}")
                raise
            finally:
                cursor.close()
    
    return total_loaded


def load_table_from_parquet(
    conn: psycopg2.extensions.connection,
    table_name: str,
    parquet_file: str,
    column_mapping: Optional[dict] = None,
    dry_run: bool = True
) -> int:
    """Generic function to load a parquet file into a database table."""
    file_path = DATA_DIR / parquet_file
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return 0
    
    logger.info(f"Loading {parquet_file} into {table_name}...")
    df = pd.read_parquet(file_path)
    
    # Apply column mapping if provided
    if column_mapping:
        available_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_mapping.keys())].copy()
        df = df.rename(columns=available_mapping)
    
    # Clean numeric columns (remove $, commas, whitespace)
    numeric_cols = ['hourly_rate', 'estimated_amount', 'invoiced_amount', 
                    'total_estimated_cost', 'total_actual_cost', 'hourly_rate_quoted', 'hourly_rate_billed',
                    'leads_received', 'bad', 'sent', 'pending', 'booked', 'lost', 'cancelled',
                    'booked_total', 'average_booking', 'percent_bad', 'percent_sent', 'percent_pending',
                    'percent_booked', 'percent_lost', 'percent_cancelled']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Replace NaN with None for PostgreSQL
    df = df.where(pd.notnull(df), None)
    
    # Add auto-generated columns (id, created_at, updated_at)
    from datetime import datetime
    import uuid
    now = datetime.utcnow()
    if 'id' not in df.columns:
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    if 'created_at' not in df.columns:
        df['created_at'] = now
    if 'updated_at' not in df.columns:
        df['updated_at'] = now
    
    if dry_run:
        logger.info(f"DRY RUN: Would load {len(df)} rows into {table_name}")
        return len(df)
    
    cursor = conn.cursor()
    try:
        # Get actual table columns from database
        cursor_temp = conn.cursor()
        cursor_temp.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        db_columns = [row[0] for row in cursor_temp.fetchall()]
        cursor_temp.close()
        
        # Only include columns that exist in both dataframe and database
        # Include created_at and updated_at since we're generating them
        available_cols = [col for col in df.columns if col in db_columns]
        columns = available_cols
        
        # Clean values: convert NaT/NaN to None
        def clean_value(val):
            if pd.isna(val):
                return None
            if isinstance(val, pd.Timestamp) and pd.isna(val):
                return None
            return val
        
        df_for_insert = df[columns]
        values = [tuple(clean_value(val) for val in row) for row in df_for_insert.values]
        
        # Get primary key or unique column for conflict handling
        if table_name == 'booked_opportunities':
            conflict_col = 'quote_number'
        elif table_name == 'lead_status':
            conflict_col = 'quote_number'
        elif table_name == 'lost_leads':
            conflict_col = 'quote_number'
        elif table_name == 'user_performance':
            conflict_col = 'name'
        elif table_name == 'sales_performance':
            conflict_col = 'name'
        else:
            conflict_col = None
        
        column_names = ', '.join(columns)
        
        if conflict_col and conflict_col in columns:
            query = f"""
                INSERT INTO {table_name} ({column_names})
                VALUES %s
                ON CONFLICT ({conflict_col}) DO NOTHING
            """
        else:
            query = f"""
                INSERT INTO {table_name} ({column_names})
                VALUES %s
            """
        
        execute_values(cursor, query, values, page_size=1000)
        conn.commit()
        loaded = cursor.rowcount
        logger.info(f"Loaded {loaded} rows into {table_name}")
        return loaded
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading {table_name}: {e}")
        raise
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description='Load parquet files into database')
    parser.add_argument('--execute', action='store_true', help='Execute the import (default is dry-run)')
    parser.add_argument('--force', action='store_true', help='Force execution even if already run')
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to actually import data.")
    
    conn = get_db_connection()
    
    try:
        script_name = 'load_parquet_data'
        
        # Check if already executed
        if not args.force and script_already_executed(conn, script_name):
            logger.info(f"Script {script_name} has already been executed. Use --force to run again.")
            return
        
        total_loaded = 0
        
        # 1. Load Jobs (from 7 year files)
        logger.info("=" * 60)
        logger.info("Step 1: Loading Jobs")
        logger.info("=" * 60)
        jobs_loaded = load_jobs(conn, dry_run=dry_run)
        total_loaded += jobs_loaded
        logger.info(f"Total jobs loaded: {jobs_loaded}")
        
        # 2. Load BookedOpportunities
        logger.info("=" * 60)
        logger.info("Step 2: Loading BookedOpportunities")
        logger.info("=" * 60)
        bo_mapping = {
            'quote': 'quote_number',
            'email': 'email',
            'phone_number': 'phone_number',
            'customer_name': 'customer_name',
            'branch_name': 'branch_name',
            'moving_from': 'moving_from',
            'moving_to': 'moving_to',
            'service_date': 'service_date',
            'service_type': 'service_type',
            'hourly_rate': 'hourly_rate',
            'estimated_amount': 'estimated_amount',
            'invoiced_amount': 'invoiced_amount',
            'referral_source': 'referral_source',
            'status': 'status',
            'booked_date': 'booked_date',
        }
        bo_loaded = load_table_from_parquet(
            conn, 'booked_opportunities', 'booked_opportunities.parquet', 
            column_mapping=bo_mapping, dry_run=dry_run
        )
        total_loaded += bo_loaded
        
        # 3. Load LeadStatus
        logger.info("=" * 60)
        logger.info("Step 3: Loading LeadStatus")
        logger.info("=" * 60)
        ls_mapping = {
            'quote': 'quote_number',
            'branch_name': 'branch_name',
            'status': 'status',
            'referral_source': 'referral_source',
            'time_to_contact': 'time_to_contact',
            # sales_person will be linked via lookup scripts later
        }
        ls_loaded = load_table_from_parquet(
            conn, 'lead_status', 'lead_status.parquet',
            column_mapping=ls_mapping, dry_run=dry_run
        )
        total_loaded += ls_loaded
        
        # 4. Load BadLeads
        logger.info("=" * 60)
        logger.info("Step 4: Loading BadLeads")
        logger.info("=" * 60)
        bl_loaded = load_table_from_parquet(
            conn, 'bad_leads', 'bad_leads.parquet', dry_run=dry_run
        )
        total_loaded += bl_loaded
        
        # 5. Load LostLeads
        logger.info("=" * 60)
        logger.info("Step 5: Loading LostLeads")
        logger.info("=" * 60)
        ll_mapping = {
            'quote': 'quote_number',
            'name': 'name',
            'lost_date': 'lost_date',
            'move_date': 'move_date',
            'reason': 'reason',
            'date_received': 'date_received',
            'time_to_first_contact': 'time_to_first_contact',
            'referral_source': 'referral_source',  # Will be mapped to lead_source_id later
        }
        ll_loaded = load_table_from_parquet(
            conn, 'lost_leads', 'lost_leads.parquet',
            column_mapping=ll_mapping, dry_run=dry_run
        )
        total_loaded += ll_loaded
        
        # 6. Load UserPerformance
        logger.info("=" * 60)
        logger.info("Step 6: Loading UserPerformance")
        logger.info("=" * 60)
        # Only include columns that exist in the database schema
        up_loaded = load_table_from_parquet(
            conn, 'user_performance', 'user_performance.parquet', 
            column_mapping=None, dry_run=dry_run  # Will filter columns dynamically
        )
        total_loaded += up_loaded
        
        # 7. Load SalesPerformance
        logger.info("=" * 60)
        logger.info("Step 7: Loading SalesPerformance")
        logger.info("=" * 60)
        sp_loaded = load_table_from_parquet(
            conn, 'sales_performance', 'sales_performance.parquet',
            column_mapping=None, dry_run=dry_run
        )
        total_loaded += sp_loaded
        
        logger.info("=" * 60)
        logger.info(f"Total rows loaded: {total_loaded}")
        logger.info("=" * 60)
        
        if not dry_run:
            log_script_execution(conn, script_name, f"Loaded {total_loaded} total rows")
            logger.info("Data import completed successfully!")
        else:
            logger.info("DRY RUN completed. Use --execute to import data.")
            
    except Exception as e:
        logger.error(f"Error during data import: {e}", exc_info=True)
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()

