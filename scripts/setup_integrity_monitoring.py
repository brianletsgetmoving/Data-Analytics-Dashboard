#!/usr/bin/env python3
"""
Set up automated daily integrity checks with alerts for orphaned records 
and linkage rate drops.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime, timedelta
import logging
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_orphaned_user_performance(conn):
    """Check for orphaned UserPerformance records."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as orphaned_count
        FROM user_performance
        WHERE sales_person_id IS NULL
    """)
    
    result = cursor.fetchone()
    orphaned_count = result[0] if result else 0
    
    cursor.close()
    return orphaned_count


def check_orphaned_sales_performance(conn):
    """Check for orphaned SalesPerformance records."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as orphaned_count
        FROM sales_performance
        WHERE sales_person_id IS NULL
    """)
    
    result = cursor.fetchone()
    orphaned_count = result[0] if result else 0
    
    cursor.close()
    return orphaned_count


def check_job_customer_linkage_rate(conn):
    """Check job to customer linkage rate."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_jobs,
            COUNT(customer_id) as linked_jobs,
            ROUND(COUNT(customer_id)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as linkage_rate
        FROM jobs
    """)
    
    result = cursor.fetchone()
    cursor.close()
    
    return {
        'total': result[0] if result else 0,
        'linked': result[1] if result else 0,
        'rate': float(result[2]) if result and result[2] else 0.0
    }


def check_lead_status_linkage_rate(conn):
    """Check LeadStatus to BookedOpportunity linkage rate."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_leads,
            COUNT(booked_opportunity_id) as linked_leads,
            ROUND(COUNT(booked_opportunity_id)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as linkage_rate
        FROM lead_status
    """)
    
    result = cursor.fetchone()
    cursor.close()
    
    return {
        'total': result[0] if result else 0,
        'linked': result[1] if result else 0,
        'rate': float(result[2]) if result and result[2] else 0.0
    }


def check_badlead_linkage_rate(conn):
    """Check BadLead to LeadStatus linkage rate."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_bad_leads,
            COUNT(lead_status_id) as linked_bad_leads,
            ROUND(COUNT(lead_status_id)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as linkage_rate
        FROM bad_leads
    """)
    
    result = cursor.fetchone()
    cursor.close()
    
    return {
        'total': result[0] if result else 0,
        'linked': result[1] if result else 0,
        'rate': float(result[2]) if result and result[2] else 0.0
    }


def run_integrity_checks(conn):
    """Run all integrity checks."""
    logger.info("Running integrity checks...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'orphaned_user_performance': check_orphaned_user_performance(conn),
        'orphaned_sales_performance': check_orphaned_sales_performance(conn),
        'job_customer_linkage': check_job_customer_linkage_rate(conn),
        'lead_status_linkage': check_lead_status_linkage_rate(conn),
        'badlead_linkage': check_badlead_linkage_rate(conn),
    }
    
    # Check for alerts
    alerts = []
    
    if results['orphaned_user_performance'] > 0:
        alerts.append({
            'type': 'orphaned_records',
            'severity': 'warning',
            'message': f"{results['orphaned_user_performance']} orphaned UserPerformance records found"
        })
    
    if results['orphaned_sales_performance'] > 0:
        alerts.append({
            'type': 'orphaned_records',
            'severity': 'warning',
            'message': f"{results['orphaned_sales_performance']} orphaned SalesPerformance records found"
        })
    
    if results['job_customer_linkage']['rate'] < 95.0:
        alerts.append({
            'type': 'linkage_rate',
            'severity': 'warning',
            'message': f"Job-Customer linkage rate is {results['job_customer_linkage']['rate']:.2f}% (threshold: 95%)"
        })
    
    if results['lead_status_linkage']['rate'] < 80.0:
        alerts.append({
            'type': 'linkage_rate',
            'severity': 'warning',
            'message': f"LeadStatus-BookedOpportunity linkage rate is {results['lead_status_linkage']['rate']:.2f}% (threshold: 80%)"
        })
    
    if results['badlead_linkage']['rate'] < 70.0:
        alerts.append({
            'type': 'linkage_rate',
            'severity': 'info',
            'message': f"BadLead-LeadStatus linkage rate is {results['badlead_linkage']['rate']:.2f}% (threshold: 70%)"
        })
    
    results['alerts'] = alerts
    
    return results


def save_integrity_report(results, output_dir: Path):
    """Save integrity check results to file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_path = output_dir / f"integrity_check_{timestamp}.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved integrity report to {report_path}")
    return report_path


def create_monitoring_table(conn, dry_run: bool = True):
    """Create table to store historical integrity check results."""
    cursor = conn.cursor()
    
    if not dry_run:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrity_check_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                check_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                orphaned_user_performance INTEGER DEFAULT 0,
                orphaned_sales_performance INTEGER DEFAULT 0,
                job_customer_linkage_rate DECIMAL(5, 2),
                lead_status_linkage_rate DECIMAL(5, 2),
                badlead_linkage_rate DECIMAL(5, 2),
                alerts JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS integrity_check_history_timestamp_idx 
            ON integrity_check_history(check_timestamp DESC)
        """)
        
        conn.commit()
        logger.info("Created integrity_check_history table")
    else:
        logger.info("[DRY RUN] Would create integrity_check_history table")
    
    cursor.close()


def insert_check_result(conn, results, dry_run: bool = True):
    """Insert integrity check result into history table."""
    cursor = conn.cursor()
    
    if not dry_run:
        cursor.execute("""
            INSERT INTO integrity_check_history (
                check_timestamp,
                orphaned_user_performance,
                orphaned_sales_performance,
                job_customer_linkage_rate,
                lead_status_linkage_rate,
                badlead_linkage_rate,
                alerts
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            results['timestamp'],
            results['orphaned_user_performance'],
            results['orphaned_sales_performance'],
            results['job_customer_linkage']['rate'],
            results['lead_status_linkage']['rate'],
            results['badlead_linkage']['rate'],
            json.dumps(results['alerts'])
        ))
        
        conn.commit()
        logger.info("Inserted integrity check result into history")
    else:
        logger.info("[DRY RUN] Would insert integrity check result")
    
    cursor.close()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run integrity checks and set up monitoring')
    parser.add_argument('--setup', action='store_true',
                       help='Set up monitoring table')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the updates (overrides dry-run)')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
        if args.setup:
            logger.info("Setting up monitoring table...")
            create_monitoring_table(conn, dry_run=dry_run)
        
        logger.info("Running integrity checks...")
        results = run_integrity_checks(conn)
        
        # Print results
        print("\n" + "="*80)
        print("INTEGRITY CHECK RESULTS")
        print("="*80)
        print(f"Orphaned UserPerformance: {results['orphaned_user_performance']}")
        print(f"Orphaned SalesPerformance: {results['orphaned_sales_performance']}")
        print(f"Job-Customer Linkage Rate: {results['job_customer_linkage']['rate']:.2f}%")
        print(f"LeadStatus Linkage Rate: {results['lead_status_linkage']['rate']:.2f}%")
        print(f"BadLead Linkage Rate: {results['badlead_linkage']['rate']:.2f}%")
        
        if results['alerts']:
            print("\nALERTS:")
            for alert in results['alerts']:
                print(f"  [{alert['severity'].upper()}] {alert['message']}")
        else:
            print("\nNo alerts - all checks passed!")
        
        print("="*80 + "\n")
        
        # Save report
        output_dir = Path("reports/integrity_checks")
        save_integrity_report(results, output_dir)
        
        # Insert into history (if table exists)
        if not dry_run:
            try:
                insert_check_result(conn, results, dry_run=False)
            except psycopg2.errors.UndefinedTable:
                logger.warning("integrity_check_history table does not exist. Run with --setup first.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Integrity check failed: {e}")
        logger.exception(e)
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

