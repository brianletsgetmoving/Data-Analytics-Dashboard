"""
Analyze relationships between test location jobs and other database tables.
Comprehensive analysis to identify all connections before deletion.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import psycopg2
import os
import json
import logging
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


def get_test_location_jobs(conn) -> pd.DataFrame:
    """Get all test location jobs."""
    logger.info("Loading test location jobs...")
    
    query = """
        SELECT 
            id, job_id, job_number, opportunity_status, job_date,
            customer_name, customer_email, customer_phone,
            branch_name, sales_person_name, job_type,
            customer_id, is_duplicate
        FROM jobs
        WHERE branch_name LIKE '%Test Location%'
        ORDER BY branch_name, job_date
    """
    
    df = pd.read_sql_query(query, conn)
    logger.info(f"Found {len(df)} test location jobs")
    return df


def analyze_customer_relationships(conn, test_job_ids: List[str], test_customer_ids: Set[str]) -> Dict:
    """Analyze customer relationships for test jobs."""
    logger.info("Analyzing customer relationships...")
    
    if not test_customer_ids:
        return {
            'customers': [],
            'test_only_customers': [],
            'customers_with_other_jobs': []
        }
    
    # Get all customers linked to test jobs
    customer_ids_list = list(test_customer_ids)
    placeholders = ','.join(['%s'] * len(customer_ids_list))
    
    query = f"""
        SELECT 
            c.id,
            c.name,
            c.email,
            c.phone,
            COUNT(DISTINCT CASE WHEN j.branch_name LIKE '%Test Location%' THEN j.id END) as test_job_count,
            COUNT(DISTINCT CASE WHEN j.branch_name NOT LIKE '%Test Location%' OR j.branch_name IS NULL THEN j.id END) as non_test_job_count
        FROM customers c
        LEFT JOIN jobs j ON c.id = j.customer_id
        WHERE c.id IN ({placeholders})
        GROUP BY c.id, c.name, c.email, c.phone
    """
    
    cursor = conn.cursor()
    cursor.execute(query, customer_ids_list)
    columns = [desc[0] for desc in cursor.description]
    customers = []
    
    for row in cursor.fetchall():
        customer = dict(zip(columns, row))
        customers.append(customer)
    
    cursor.close()
    
    # Separate test-only customers from customers with other jobs
    test_only_customers = [c for c in customers if c['non_test_job_count'] == 0]
    customers_with_other_jobs = [c for c in customers if c['non_test_job_count'] > 0]
    
    logger.info(f"Found {len(customers)} customers linked to test jobs")
    logger.info(f"  - {len(test_only_customers)} customers with ONLY test jobs")
    logger.info(f"  - {len(customers_with_other_jobs)} customers with other jobs")
    
    return {
        'customers': customers,
        'test_only_customers': test_only_customers,
        'customers_with_other_jobs': customers_with_other_jobs
    }


def analyze_bad_lead_relationships(conn, test_customer_ids: Set[str]) -> List[Dict]:
    """Find BadLeads linked to test customers."""
    logger.info("Analyzing BadLead relationships...")
    
    if not test_customer_ids:
        return []
    
    customer_ids_list = list(test_customer_ids)
    placeholders = ','.join(['%s'] * len(customer_ids_list))
    
    query = f"""
        SELECT 
            bl.id,
            bl.customer_id,
            bl.customer_name,
            bl.customer_email,
            bl.customer_phone,
            bl.move_date,
            bl.date_lead_received,
            bl.lead_bad_reason,
            c.name as customer_name_linked
        FROM bad_leads bl
        LEFT JOIN customers c ON bl.customer_id = c.id
        WHERE bl.customer_id IN ({placeholders})
        ORDER BY bl.date_lead_received DESC
    """
    
    cursor = conn.cursor()
    cursor.execute(query, customer_ids_list)
    columns = [desc[0] for desc in cursor.description]
    bad_leads = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    logger.info(f"Found {len(bad_leads)} BadLeads linked to test customers")
    
    return bad_leads


def analyze_booked_opportunity_relationships(conn, test_customer_ids: Set[str]) -> List[Dict]:
    """Find BookedOpportunities linked to test customers."""
    logger.info("Analyzing BookedOpportunity relationships...")
    
    if not test_customer_ids:
        return []
    
    customer_ids_list = list(test_customer_ids)
    placeholders = ','.join(['%s'] * len(customer_ids_list))
    
    query = f"""
        SELECT 
            bo.id,
            bo.customer_id,
            bo.quote_number,
            bo.customer_name,
            bo.email,
            bo.phone_number,
            bo.branch_name,
            bo.service_date,
            bo.service_type,
            bo.booked_date,
            c.name as customer_name_linked
        FROM booked_opportunities bo
        LEFT JOIN customers c ON bo.customer_id = c.id
        WHERE bo.customer_id IN ({placeholders})
        ORDER BY bo.booked_date DESC
    """
    
    cursor = conn.cursor()
    cursor.execute(query, customer_ids_list)
    columns = [desc[0] for desc in cursor.description]
    booked_opportunities = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    logger.info(f"Found {len(booked_opportunities)} BookedOpportunities linked to test customers")
    
    return booked_opportunities


def analyze_lost_lead_matches(conn, test_job_numbers: List[str]) -> List[Dict]:
    """Check if LostLead records match test job numbers."""
    logger.info("Analyzing LostLead matches...")
    
    if not test_job_numbers:
        return []
    
    # Filter out None values
    test_job_numbers = [j for j in test_job_numbers if j is not None and pd.notna(j)]
    
    if not test_job_numbers:
        return []
    
    placeholders = ','.join(['%s'] * len(test_job_numbers))
    
    query = f"""
        SELECT 
            ll.id,
            ll.quote_number,
            ll.name,
            ll.lost_date,
            ll.move_date,
            ll.reason,
            ll.date_received
        FROM lost_leads ll
        WHERE ll.quote_number IN ({placeholders})
        ORDER BY ll.date_received DESC
    """
    
    cursor = conn.cursor()
    cursor.execute(query, test_job_numbers)
    columns = [desc[0] for desc in cursor.description]
    lost_leads = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    logger.info(f"Found {len(lost_leads)} LostLead records matching test job numbers")
    
    return lost_leads


def analyze_lead_status_matches(conn, test_job_numbers: List[str]) -> List[Dict]:
    """Check if LeadStatus records match test job numbers."""
    logger.info("Analyzing LeadStatus matches...")
    
    if not test_job_numbers:
        return []
    
    # Filter out None values
    test_job_numbers = [j for j in test_job_numbers if j is not None and pd.notna(j)]
    
    if not test_job_numbers:
        return []
    
    placeholders = ','.join(['%s'] * len(test_job_numbers))
    
    query = f"""
        SELECT 
            ls.id,
            ls.quote_number,
            ls.branch_name,
            ls.status,
            ls.sales_person,
            ls.time_to_contact,
            ls.referral_source
        FROM lead_status ls
        WHERE ls.quote_number IN ({placeholders})
        ORDER BY ls.created_at DESC
    """
    
    cursor = conn.cursor()
    cursor.execute(query, test_job_numbers)
    columns = [desc[0] for desc in cursor.description]
    lead_statuses = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    logger.info(f"Found {len(lead_statuses)} LeadStatus records matching test job numbers")
    
    return lead_statuses


def generate_relationship_report(results: Dict, output_dir: Path):
    """Generate comprehensive relationship report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate summary
    summary = {
        'analysis_timestamp': timestamp,
        'total_test_jobs': len(results['test_jobs']),
        'unique_branches': results['test_jobs']['branch_name'].nunique() if not results['test_jobs'].empty else 0,
        'unique_customers': len(results['customer_analysis']['customers']),
        'test_only_customers': len(results['customer_analysis']['test_only_customers']),
        'customers_with_other_jobs': len(results['customer_analysis']['customers_with_other_jobs']),
        'bad_leads_count': len(results['bad_leads']),
        'booked_opportunities_count': len(results['booked_opportunities']),
        'lost_lead_matches': len(results['lost_leads']),
        'lead_status_matches': len(results['lead_statuses'])
    }
    
    # Export CSV files
    csv_base = output_dir / f"test_location_relationships_{timestamp}"
    
    # Test jobs
    if not results['test_jobs'].empty:
        results['test_jobs'].to_csv(f"{csv_base}_test_jobs.csv", index=False)
        logger.info(f"Exported test jobs to {csv_base}_test_jobs.csv")
    
    # Customer analysis
    if results['customer_analysis']['customers']:
        customers_df = pd.DataFrame(results['customer_analysis']['customers'])
        customers_df['recommendation'] = customers_df.apply(
            lambda row: 'Remove' if row['non_test_job_count'] == 0 else 'Keep',
            axis=1
        )
        customers_df.to_csv(f"{csv_base}_customers.csv", index=False)
        logger.info(f"Exported customer analysis to {csv_base}_customers.csv")
    
    # Bad leads
    if results['bad_leads']:
        bad_leads_df = pd.DataFrame(results['bad_leads'])
        bad_leads_df.to_csv(f"{csv_base}_bad_leads.csv", index=False)
        logger.info(f"Exported BadLeads to {csv_base}_bad_leads.csv")
    
    # Booked opportunities
    if results['booked_opportunities']:
        booked_opps_df = pd.DataFrame(results['booked_opportunities'])
        booked_opps_df.to_csv(f"{csv_base}_booked_opportunities.csv", index=False)
        logger.info(f"Exported BookedOpportunities to {csv_base}_booked_opportunities.csv")
    
    # Lost leads
    if results['lost_leads']:
        lost_leads_df = pd.DataFrame(results['lost_leads'])
        lost_leads_df.to_csv(f"{csv_base}_lost_leads.csv", index=False)
        logger.info(f"Exported LostLeads to {csv_base}_lost_leads.csv")
    
    # Lead status
    if results['lead_statuses']:
        lead_statuses_df = pd.DataFrame(results['lead_statuses'])
        lead_statuses_df.to_csv(f"{csv_base}_lead_statuses.csv", index=False)
        logger.info(f"Exported LeadStatus to {csv_base}_lead_statuses.csv")
    
    # JSON summary
    json_path = output_dir / f"test_location_relationships_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info(f"Exported summary to {json_path}")
    
    return summary, csv_base


def main():
    """Main function."""
    logger.info("="*80)
    logger.info("TEST LOCATION RELATIONSHIPS ANALYSIS")
    logger.info("="*80)
    
    conn = get_db_connection()
    
    try:
        # Get test location jobs
        test_jobs_df = get_test_location_jobs(conn)
        
        if test_jobs_df.empty:
            logger.warning("No test location jobs found")
            return
        
        # Extract IDs and job numbers
        test_job_ids = test_jobs_df['id'].tolist()
        test_customer_ids = set(test_jobs_df['customer_id'].dropna().unique().tolist())
        test_job_numbers = test_jobs_df['job_number'].dropna().unique().tolist()
        
        logger.info(f"\nTest Location Jobs Summary:")
        logger.info(f"  Total jobs: {len(test_jobs_df)}")
        logger.info(f"  Unique branches: {test_jobs_df['branch_name'].nunique()}")
        logger.info(f"  Unique customers: {len(test_customer_ids)}")
        logger.info(f"  Jobs with customer_id: {test_jobs_df['customer_id'].notna().sum()}")
        
        # Analyze relationships
        customer_analysis = analyze_customer_relationships(conn, test_job_ids, test_customer_ids)
        bad_leads = analyze_bad_lead_relationships(conn, test_customer_ids)
        booked_opportunities = analyze_booked_opportunity_relationships(conn, test_customer_ids)
        lost_leads = analyze_lost_lead_matches(conn, test_job_numbers)
        lead_statuses = analyze_lead_status_matches(conn, test_job_numbers)
        
        # Compile results
        results = {
            'test_jobs': test_jobs_df,
            'customer_analysis': customer_analysis,
            'bad_leads': bad_leads,
            'booked_opportunities': booked_opportunities,
            'lost_leads': lost_leads,
            'lead_statuses': lead_statuses
        }
        
        # Generate reports
        output_dir = Path("reports")
        summary, csv_base = generate_relationship_report(results, output_dir)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("ANALYSIS SUMMARY")
        logger.info("="*80)
        logger.info(f"Total test jobs: {summary['total_test_jobs']}")
        logger.info(f"Unique branches: {summary['unique_branches']}")
        logger.info(f"Unique customers: {summary['unique_customers']}")
        logger.info(f"  - Customers with ONLY test jobs: {summary['test_only_customers']}")
        logger.info(f"  - Customers with other jobs: {summary['customers_with_other_jobs']}")
        logger.info(f"BadLeads linked to test customers: {summary['bad_leads_count']}")
        logger.info(f"BookedOpportunities linked to test customers: {summary['booked_opportunities_count']}")
        logger.info(f"LostLead records matching test jobs: {summary['lost_lead_matches']}")
        logger.info(f"LeadStatus records matching test jobs: {summary['lead_status_matches']}")
        logger.info("="*80)
        logger.info(f"\nDetailed reports exported to: {csv_base}_*.csv")
        logger.info(f"Summary JSON: reports/test_location_relationships_{summary['analysis_timestamp']}.json")
        
    finally:
        conn.close()
        logger.info("Analysis complete")


if __name__ == '__main__':
    main()

