"""
Comprehensive analysis of job-to-customer linkage gaps across the entire database.
Identifies missing linkages and potential matches to ensure database-level integrity.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import psycopg2
import os
import json
import logging
import re
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict

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


def analyze_job_customer_id_status(conn) -> Dict:
    """Analyze job customer_id status."""
    logger.info("Analyzing job customer_id status...")
    
    query = """
        SELECT 
            COUNT(*) as total_jobs,
            COUNT(customer_id) as jobs_with_customer_id,
            COUNT(*) - COUNT(customer_id) as jobs_without_customer_id,
            COUNT(CASE WHEN customer_name IS NOT NULL AND customer_name != '' THEN 1 END) as jobs_with_customer_name,
            COUNT(CASE WHEN customer_name IS NOT NULL AND customer_name != '' AND customer_id IS NULL THEN 1 END) as jobs_with_name_no_id
        FROM jobs
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    result = dict(zip(columns, cursor.fetchone()))
    cursor.close()
    
    if result['total_jobs'] > 0:
        result['linkage_percentage'] = (result['jobs_with_customer_id'] / result['total_jobs']) * 100
        result['name_without_id_percentage'] = (result['jobs_with_name_no_id'] / result['jobs_with_customer_name']) * 100 if result['jobs_with_customer_name'] > 0 else 0
    else:
        result['linkage_percentage'] = 0
        result['name_without_id_percentage'] = 0
    
    return result


def analyze_unique_customer_data_in_jobs(conn) -> Dict:
    """Analyze unique customer data in jobs."""
    logger.info("Analyzing unique customer data in jobs...")
    
    query = """
        SELECT 
            COUNT(DISTINCT customer_name) FILTER (WHERE customer_name IS NOT NULL AND customer_name != '') as unique_names,
            COUNT(DISTINCT customer_email) FILTER (WHERE customer_email IS NOT NULL AND customer_email != '') as unique_emails,
            COUNT(DISTINCT customer_phone) FILTER (WHERE customer_phone IS NOT NULL AND customer_phone != '') as unique_phones,
            COUNT(DISTINCT CONCAT(
                COALESCE(customer_name, ''),
                '|',
                COALESCE(customer_email, ''),
                '|',
                COALESCE(customer_phone, '')
            )) FILTER (WHERE customer_name IS NOT NULL AND customer_name != '') as unique_combinations
        FROM jobs
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    result = dict(zip(columns, cursor.fetchone()))
    cursor.close()
    
    return result


def analyze_customer_table(conn) -> Dict:
    """Analyze customer table."""
    logger.info("Analyzing customer table...")
    
    query = """
        SELECT 
            COUNT(*) as total_customers,
            COUNT(email) FILTER (WHERE email IS NOT NULL AND email != '') as customers_with_email,
            COUNT(phone) FILTER (WHERE phone IS NOT NULL AND phone != '') as customers_with_phone,
            COUNT(*) FILTER (WHERE email IS NOT NULL AND email != '' AND phone IS NOT NULL AND phone != '') as customers_with_both,
            COUNT(*) FILTER (WHERE (email IS NULL OR email = '') AND (phone IS NULL OR phone = '')) as customers_name_only
        FROM customers
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    result = dict(zip(columns, cursor.fetchone()))
    cursor.close()
    
    return result


def analyze_linkage_gaps(conn) -> pd.DataFrame:
    """Identify jobs that should be linked but aren't."""
    logger.info("Analyzing linkage gaps...")
    
    query = """
        SELECT 
            j.id,
            j.job_id,
            j.job_number,
            j.customer_name,
            j.customer_email,
            j.customer_phone,
            j.origin_city,
            j.destination_city,
            j.customer_id,
            j.job_date
        FROM jobs j
        WHERE j.customer_name IS NOT NULL 
        AND j.customer_name != ''
        AND j.customer_id IS NULL
        ORDER BY j.job_date DESC
    """
    
    df = pd.read_sql_query(query, conn)
    logger.info(f"Found {len(df)} jobs with customer data but no customer_id")
    
    return df


def analyze_matching_scenarios(conn) -> Dict:
    """Identify potential matches between jobs and customers."""
    logger.info("Analyzing matching scenarios...")
    
    results = {}
    
    # 1. Jobs with email that could match existing customers
    query1 = """
        SELECT COUNT(DISTINCT j.id) as count
        FROM jobs j
        INNER JOIN customers c ON j.customer_email = c.email
        WHERE j.customer_email IS NOT NULL 
        AND j.customer_email != ''
        AND j.customer_id IS NULL
        AND c.email IS NOT NULL
        AND c.email != ''
    """
    cursor = conn.cursor()
    cursor.execute(query1)
    results['jobs_with_email_matchable'] = cursor.fetchone()[0]
    
    # 2. Jobs with phone that could match existing customers
    query2 = """
        SELECT COUNT(DISTINCT j.id) as count
        FROM jobs j
        INNER JOIN customers c ON j.customer_phone = c.phone
        WHERE j.customer_phone IS NOT NULL 
        AND j.customer_phone != ''
        AND j.customer_id IS NULL
        AND c.phone IS NOT NULL
        AND c.phone != ''
    """
    cursor.execute(query2)
    results['jobs_with_phone_matchable'] = cursor.fetchone()[0]
    
    # 3. Jobs with name+email that could match
    query3 = """
        SELECT COUNT(DISTINCT j.id) as count
        FROM jobs j
        INNER JOIN customers c ON j.customer_email = c.email AND j.customer_name = c.name
        WHERE j.customer_email IS NOT NULL 
        AND j.customer_email != ''
        AND j.customer_name IS NOT NULL
        AND j.customer_name != ''
        AND j.customer_id IS NULL
        AND c.email IS NOT NULL
        AND c.email != ''
    """
    cursor.execute(query3)
    results['jobs_with_email_name_matchable'] = cursor.fetchone()[0]
    
    # 4. Jobs with name+phone that could match
    query4 = """
        SELECT COUNT(DISTINCT j.id) as count
        FROM jobs j
        INNER JOIN customers c ON j.customer_phone = c.phone AND j.customer_name = c.name
        WHERE j.customer_phone IS NOT NULL 
        AND j.customer_phone != ''
        AND j.customer_name IS NOT NULL
        AND j.customer_name != ''
        AND j.customer_id IS NULL
        AND c.phone IS NOT NULL
        AND c.phone != ''
    """
    cursor.execute(query4)
    results['jobs_with_phone_name_matchable'] = cursor.fetchone()[0]
    
    # 5. Jobs with name only that could match by name+location
    query5 = """
        SELECT COUNT(DISTINCT j.id) as count
        FROM jobs j
        INNER JOIN customers c ON j.customer_name = c.name
            AND (j.origin_city = c.origin_city OR (j.origin_city IS NULL AND c.origin_city IS NULL))
            AND (j.destination_city = c.destination_city OR (j.destination_city IS NULL AND c.destination_city IS NULL))
        WHERE j.customer_name IS NOT NULL
        AND j.customer_name != ''
        AND (j.customer_email IS NULL OR j.customer_email = '')
        AND (j.customer_phone IS NULL OR j.customer_phone = '')
        AND j.customer_id IS NULL
        AND (c.email IS NULL OR c.email = '')
        AND (c.phone IS NULL OR c.phone = '')
    """
    cursor.execute(query5)
    results['jobs_with_name_location_matchable'] = cursor.fetchone()[0]
    
    cursor.close()
    
    return results


def get_potential_matches(conn) -> pd.DataFrame:
    """Get detailed potential matches."""
    logger.info("Getting detailed potential matches...")
    
    query = """
        SELECT DISTINCT
            j.id as job_id,
            j.job_id,
            j.job_number,
            j.customer_name as job_customer_name,
            j.customer_email as job_customer_email,
            j.customer_phone as job_customer_phone,
            j.origin_city as job_origin_city,
            j.destination_city as job_destination_city,
            j.job_date,
            c.id as customer_id,
            c.name as customer_name,
            c.email as customer_email,
            c.phone as customer_phone,
            CASE
                WHEN j.customer_email = c.email AND j.customer_email IS NOT NULL THEN 'email'
                WHEN j.customer_phone = c.phone AND j.customer_phone IS NOT NULL THEN 'phone'
                WHEN j.customer_email = c.email AND j.customer_name = c.name THEN 'email_name'
                WHEN j.customer_phone = c.phone AND j.customer_name = c.name THEN 'phone_name'
                WHEN j.customer_name = c.name AND 
                     (j.origin_city = c.origin_city OR (j.origin_city IS NULL AND c.origin_city IS NULL)) AND
                     (j.destination_city = c.destination_city OR (j.destination_city IS NULL AND c.destination_city IS NULL)) THEN 'name_location'
                ELSE 'unknown'
            END as match_type
        FROM jobs j
        INNER JOIN customers c ON (
            (j.customer_email = c.email AND j.customer_email IS NOT NULL AND j.customer_email != '')
            OR (j.customer_phone = c.phone AND j.customer_phone IS NOT NULL AND j.customer_phone != '')
            OR (j.customer_email = c.email AND j.customer_name = c.name AND j.customer_email IS NOT NULL)
            OR (j.customer_phone = c.phone AND j.customer_name = c.name AND j.customer_phone IS NOT NULL)
            OR (j.customer_name = c.name AND 
                (j.origin_city = c.origin_city OR (j.origin_city IS NULL AND c.origin_city IS NULL)) AND
                (j.destination_city = c.destination_city OR (j.destination_city IS NULL AND c.destination_city IS NULL)) AND
                (j.customer_email IS NULL OR j.customer_email = '') AND (j.customer_phone IS NULL OR j.customer_phone = '') AND
                (c.email IS NULL OR c.email = '') AND (c.phone IS NULL OR c.phone = ''))
        )
        WHERE j.customer_name IS NOT NULL
        AND j.customer_name != ''
        AND j.customer_id IS NULL
        ORDER BY match_type, j.job_date DESC
    """
    
    df = pd.read_sql_query(query, conn)
    logger.info(f"Found {len(df)} potential matches")
    
    return df


def get_missing_customers(conn) -> pd.DataFrame:
    """Get unique customer combinations in jobs that don't exist in customers table."""
    logger.info("Identifying missing customers...")
    
    query = """
        WITH job_customers AS (
            SELECT DISTINCT
                customer_name,
                customer_email,
                customer_phone,
                origin_city,
                origin_state,
                origin_zip,
                origin_address,
                destination_city,
                destination_state,
                destination_zip,
                destination_address
            FROM jobs
            WHERE customer_name IS NOT NULL
            AND customer_name != ''
            AND customer_name NOT ILIKE '%test%'
            AND customer_name NOT ILIKE '%dummy%'
            AND customer_name NOT ILIKE '%placeholder%'
        )
        SELECT jc.*
        FROM job_customers jc
        WHERE NOT EXISTS (
            SELECT 1 FROM customers c
            WHERE (jc.customer_email IS NOT NULL AND jc.customer_email != '' AND c.email = jc.customer_email)
            OR (jc.customer_phone IS NOT NULL AND jc.customer_phone != '' AND c.phone = jc.customer_phone)
            OR (
                jc.customer_name = c.name
                AND (jc.customer_email IS NULL OR jc.customer_email = '')
                AND (jc.customer_phone IS NULL OR jc.customer_phone = '')
                AND (c.email IS NULL OR c.email = '')
                AND (c.phone IS NULL OR c.phone = '')
                AND (jc.origin_city = c.origin_city OR (jc.origin_city IS NULL AND c.origin_city IS NULL))
                AND (jc.destination_city = c.destination_city OR (jc.destination_city IS NULL AND c.destination_city IS NULL))
            )
        )
        ORDER BY customer_name
    """
    
    df = pd.read_sql_query(query, conn)
    logger.info(f"Found {len(df)} unique customer combinations missing from customers table")
    
    return df


def is_valid_email(email: str) -> bool:
    """Check if email is valid format."""
    if not email or email == '':
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Check if phone is valid format (basic check)."""
    if not phone or phone == '':
        return False
    # Remove common phone formatting characters
    cleaned = re.sub(r'[^\d]', '', phone)
    # Should have at least 10 digits
    return len(cleaned) >= 10


def analyze_data_quality(conn) -> Dict:
    """Analyze data quality issues affecting linkage."""
    logger.info("Analyzing data quality issues...")
    
    # Get jobs with customer data
    query = """
        SELECT 
            id,
            customer_name,
            customer_email,
            customer_phone
        FROM jobs
        WHERE customer_name IS NOT NULL
        AND customer_name != ''
    """
    
    df = pd.read_sql_query(query, conn)
    
    results = {
        'jobs_with_name_only': len(df[(df['customer_email'].isna() | (df['customer_email'] == '')) & 
                                      (df['customer_phone'].isna() | (df['customer_phone'] == ''))]),
        'jobs_with_invalid_email': 0,
        'jobs_with_invalid_phone': 0,
    }
    
    # Check email validity
    if 'customer_email' in df.columns:
        email_mask = df['customer_email'].notna() & (df['customer_email'] != '')
        if email_mask.any():
            results['jobs_with_invalid_email'] = (~df[email_mask]['customer_email'].apply(is_valid_email)).sum()
    
    # Check phone validity
    if 'customer_phone' in df.columns:
        phone_mask = df['customer_phone'].notna() & (df['customer_phone'] != '')
        if phone_mask.any():
            results['jobs_with_invalid_phone'] = (~df[phone_mask]['customer_phone'].apply(is_valid_phone)).sum()
    
    # Check for duplicate emails/phones in customers table (unique constraint violations)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, COUNT(*) as count
        FROM customers
        WHERE email IS NOT NULL AND email != ''
        GROUP BY email
        HAVING COUNT(*) > 1
    """)
    duplicate_emails = cursor.fetchall()
    results['customers_with_duplicate_emails'] = len(duplicate_emails)
    
    cursor.execute("""
        SELECT phone, COUNT(*) as count
        FROM customers
        WHERE phone IS NOT NULL AND phone != ''
        GROUP BY phone
        HAVING COUNT(*) > 1
    """)
    duplicate_phones = cursor.fetchall()
    results['customers_with_duplicate_phones'] = len(duplicate_phones)
    
    cursor.close()
    
    return results


def generate_comprehensive_report(results: Dict, output_dir: Path):
    """Generate comprehensive analysis report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = output_dir / f"job_customer_linkage_analysis_{timestamp}"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Export CSV files
    if 'linkage_gaps' in results and not results['linkage_gaps'].empty:
        results['linkage_gaps'].to_csv(report_dir / "linkage_gaps.csv", index=False)
        logger.info(f"Exported linkage gaps to {report_dir / 'linkage_gaps.csv'}")
    
    if 'potential_matches' in results and not results['potential_matches'].empty:
        results['potential_matches'].to_csv(report_dir / "potential_matches.csv", index=False)
        logger.info(f"Exported potential matches to {report_dir / 'potential_matches.csv'}")
    
    if 'missing_customers' in results and not results['missing_customers'].empty:
        results['missing_customers'].to_csv(report_dir / "missing_customers.csv", index=False)
        logger.info(f"Exported missing customers to {report_dir / 'missing_customers.csv'}")
    
    # Create summary JSON
    summary = {
        'analysis_timestamp': timestamp,
        'job_customer_id_status': results.get('job_status', {}),
        'unique_customer_data': results.get('unique_data', {}),
        'customer_table': results.get('customer_table', {}),
        'matching_scenarios': results.get('matching_scenarios', {}),
        'data_quality': results.get('data_quality', {}),
        'linkage_gaps_count': len(results.get('linkage_gaps', [])),
        'potential_matches_count': len(results.get('potential_matches', [])),
        'missing_customers_count': len(results.get('missing_customers', [])),
    }
    
    json_path = report_dir / "linkage_analysis_summary.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info(f"Exported summary to {json_path}")
    
    return report_dir, summary


def main():
    """Main function."""
    logger.info("="*80)
    logger.info("JOB-TO-CUSTOMER LINKAGE ANALYSIS")
    logger.info("="*80)
    
    conn = get_db_connection()
    
    try:
        # Run all analyses
        job_status = analyze_job_customer_id_status(conn)
        unique_data = analyze_unique_customer_data_in_jobs(conn)
        customer_table = analyze_customer_table(conn)
        linkage_gaps = analyze_linkage_gaps(conn)
        matching_scenarios = analyze_matching_scenarios(conn)
        potential_matches = get_potential_matches(conn)
        missing_customers = get_missing_customers(conn)
        data_quality = analyze_data_quality(conn)
        
        results = {
            'job_status': job_status,
            'unique_data': unique_data,
            'customer_table': customer_table,
            'linkage_gaps': linkage_gaps,
            'matching_scenarios': matching_scenarios,
            'potential_matches': potential_matches,
            'missing_customers': missing_customers,
            'data_quality': data_quality
        }
        
        # Generate reports
        output_dir = Path("reports")
        report_dir, summary = generate_comprehensive_report(results, output_dir)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("ANALYSIS SUMMARY")
        logger.info("="*80)
        logger.info(f"\n1. JOB CUSTOMER_ID STATUS:")
        logger.info(f"   Total jobs: {job_status['total_jobs']:,}")
        logger.info(f"   Jobs with customer_id: {job_status['jobs_with_customer_id']:,} ({job_status.get('linkage_percentage', 0):.1f}%)")
        logger.info(f"   Jobs without customer_id: {job_status['jobs_without_customer_id']:,}")
        logger.info(f"   Jobs with customer_name but no customer_id: {job_status['jobs_with_name_no_id']:,}")
        
        logger.info(f"\n2. UNIQUE CUSTOMER DATA IN JOBS:")
        logger.info(f"   Unique customer names: {unique_data['unique_names']:,}")
        logger.info(f"   Unique customer emails: {unique_data['unique_emails']:,}")
        logger.info(f"   Unique customer phones: {unique_data['unique_phones']:,}")
        logger.info(f"   Unique combinations: {unique_data['unique_combinations']:,}")
        
        logger.info(f"\n3. CUSTOMER TABLE:")
        logger.info(f"   Total customers: {customer_table['total_customers']:,}")
        logger.info(f"   Customers with email: {customer_table['customers_with_email']:,}")
        logger.info(f"   Customers with phone: {customer_table['customers_with_phone']:,}")
        logger.info(f"   Customers with both: {customer_table['customers_with_both']:,}")
        logger.info(f"   Customers with name only: {customer_table['customers_name_only']:,}")
        
        logger.info(f"\n4. LINKAGE GAPS:")
        logger.info(f"   Jobs with customer data but no customer_id: {len(linkage_gaps):,}")
        
        logger.info(f"\n5. MATCHING SCENARIOS:")
        logger.info(f"   Jobs matchable by email: {matching_scenarios['jobs_with_email_matchable']:,}")
        logger.info(f"   Jobs matchable by phone: {matching_scenarios['jobs_with_phone_matchable']:,}")
        logger.info(f"   Jobs matchable by email+name: {matching_scenarios['jobs_with_email_name_matchable']:,}")
        logger.info(f"   Jobs matchable by phone+name: {matching_scenarios['jobs_with_phone_name_matchable']:,}")
        logger.info(f"   Jobs matchable by name+location: {matching_scenarios['jobs_with_name_location_matchable']:,}")
        
        logger.info(f"\n6. MISSING CUSTOMERS:")
        logger.info(f"   Unique customer combinations missing from customers table: {len(missing_customers):,}")
        
        logger.info(f"\n7. DATA QUALITY ISSUES:")
        logger.info(f"   Jobs with name only (no email/phone): {data_quality['jobs_with_name_only']:,}")
        logger.info(f"   Jobs with invalid email: {data_quality['jobs_with_invalid_email']:,}")
        logger.info(f"   Jobs with invalid phone: {data_quality['jobs_with_invalid_phone']:,}")
        logger.info(f"   Customers with duplicate emails: {data_quality['customers_with_duplicate_emails']:,}")
        logger.info(f"   Customers with duplicate phones: {data_quality['customers_with_duplicate_phones']:,}")
        
        logger.info("="*80)
        logger.info(f"\nDetailed reports exported to: {report_dir}")
        logger.info(f"Summary JSON: {report_dir / 'linkage_analysis_summary.json'}")
        
    finally:
        conn.close()
        logger.info("Analysis complete")


if __name__ == '__main__':
    main()

