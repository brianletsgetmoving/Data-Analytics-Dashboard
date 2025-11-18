"""
Analyze jobs in X Test Location branch to understand field differences
and identify which fields to exclude for duplicate detection.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import psycopg2
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get PostgreSQL database connection."""
    db_url = os.getenv("DATABASE_URL", "postgresql://buyer@localhost:5432/data_analytics")
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
        parts = db_url.split("@")
        if len(parts) == 2:
            user = parts[0].split(":")[0] if ":" in parts[0] else parts[0]
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 5432
            database = host_port_db[1].split("?")[0] if len(host_port_db) > 1 else "data_analytics"
        else:
            host, port, database, user = "localhost", 5432, "data_analytics", "buyer"
    else:
        host, port, database, user = "localhost", 5432, "data_analytics", "buyer"
    return psycopg2.connect(host=host, port=port, database=database, user=user)


def main():
    """Analyze test location jobs."""
    logger.info("Analyzing jobs in X Test Location branches...")
    
    conn = get_db_connection()
    
    try:
        # Get all jobs in X Test Location branches
        query = """
            SELECT 
                id, job_id, job_number, opportunity_status, job_date,
                customer_name, customer_email, customer_phone,
                branch_name, sales_person_name, job_type,
                total_estimated_cost, total_actual_cost,
                origin_city, destination_city,
                created_at_utc, booked_at_utc,
                created_at, updated_at,
                is_duplicate
            FROM jobs
            WHERE branch_name LIKE '%Test Location%'
            ORDER BY job_date DESC, id
        """
        
        df = pd.read_sql_query(query, conn)
        
        print(f"\n{'='*80}")
        print(f"JOBS IN X TEST LOCATION BRANCHES")
        print(f"{'='*80}")
        print(f"Total jobs: {len(df)}")
        
        if df.empty:
            print("No jobs found in test location branches")
            return
        
        print(f"\nBranch names:")
        print(df['branch_name'].value_counts())
        
        print(f"\n{'='*80}")
        print("SAMPLE JOBS (first 10):")
        print(f"{'='*80}")
        for idx, row in df.head(10).iterrows():
            print(f"\nJob {idx+1}:")
            print(f"  ID: {row['id']}")
            print(f"  Job ID: {row['job_id']}")
            print(f"  Job Number: {row['job_number']}")
            print(f"  Customer: {row['customer_name']}")
            print(f"  Status: {row['opportunity_status']}")
            print(f"  Date: {row['job_date']}")
            print(f"  Branch: {row['branch_name']}")
            print(f"  Is Duplicate: {row['is_duplicate']}")
        
        # Analyze field differences
        print(f"\n{'='*80}")
        print("FIELD VARIATION ANALYSIS")
        print(f"{'='*80}")
        print("Analyzing which fields vary most/least across test jobs...")
        
        field_variation = {}
        for col in df.columns:
            if col not in ['id', 'created_at', 'updated_at']:
                unique_count = df[col].nunique()
                total_count = len(df)
                null_count = df[col].isna().sum()
                field_variation[col] = {
                    'unique_values': unique_count,
                    'total': total_count,
                    'null_count': null_count,
                    'variation_pct': (unique_count / total_count * 100) if total_count > 0 else 0,
                    'null_pct': (null_count / total_count * 100) if total_count > 0 else 0
                }
        
        print("\nFields with MOST variation (likely to differ between duplicates):")
        sorted_fields = sorted(field_variation.items(), key=lambda x: x[1]['variation_pct'], reverse=True)
        for field, stats in sorted_fields[:15]:
            print(f"  {field:30s} {stats['unique_values']:4d}/{stats['total']:4d} unique ({stats['variation_pct']:5.1f}%) | {stats['null_count']:4d} null ({stats['null_pct']:5.1f}%)")
        
        print("\nFields with LEAST variation (likely same across duplicates):")
        for field, stats in sorted_fields[-10:]:
            print(f"  {field:30s} {stats['unique_values']:4d}/{stats['total']:4d} unique ({stats['variation_pct']:5.1f}%) | {stats['null_count']:4d} null ({stats['null_pct']:5.1f}%)")
        
        # Find potential duplicate groups (excluding id, created_at, updated_at)
        print(f"\n{'='*80}")
        print("POTENTIAL DUPLICATE ANALYSIS")
        print(f"{'='*80}")
        
        exclude_cols = ['id', 'created_at', 'updated_at']
        comparison_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Find duplicates excluding only id, created_at, updated_at
        duplicates_basic = df.duplicated(subset=comparison_cols, keep=False)
        num_duplicates_basic = duplicates_basic.sum()
        
        print(f"\nDuplicates (excluding only id, created_at, updated_at): {num_duplicates_basic}")
        
        # Try excluding more fields
        exclude_more = exclude_cols + ['job_id', 'job_number', 'created_at_utc', 'booked_at_utc', 'is_duplicate']
        comparison_cols_more = [col for col in df.columns if col not in exclude_more]
        
        duplicates_more = df.duplicated(subset=comparison_cols_more, keep=False)
        num_duplicates_more = duplicates_more.sum()
        
        print(f"Duplicates (excluding id, created_at, updated_at, job_id, job_number, timestamps, is_duplicate): {num_duplicates_more}")
        
        if num_duplicates_more > 0:
            print(f"\nFound {num_duplicates_more} potential duplicates!")
            duplicate_groups_df = df[duplicates_more].copy()
            duplicate_groups_df['duplicate_group'] = duplicate_groups_df.groupby(comparison_cols_more).ngroup()
            
            num_groups = duplicate_groups_df['duplicate_group'].nunique()
            print(f"\nDuplicate groups: {num_groups}")
            
            if num_groups > 0:
                print("\nSample duplicate groups:")
                for group_id in sorted(duplicate_groups_df['duplicate_group'].unique())[:5]:
                    group = duplicate_groups_df[duplicate_groups_df['duplicate_group'] == group_id]
                    print(f"\n  Group {group_id} ({len(group)} jobs):")
                    for _, row in group.head(3).iterrows():
                        print(f"    - {row.get('job_id') or row.get('job_number')}: {row.get('customer_name')} - {row.get('job_date')}")
        
        # Export analysis
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "test_location_jobs_analysis.csv"
        df.to_csv(output_file, index=False)
        print(f"\n{'='*80}")
        print(f"Full analysis exported to: {output_file}")
        print(f"{'='*80}")
        
    finally:
        conn.close()
        logger.info("Analysis complete")


if __name__ == '__main__':
    main()

