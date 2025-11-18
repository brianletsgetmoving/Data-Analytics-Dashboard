#!/usr/bin/env python3
"""
Comprehensive analysis to identify all orphaned UserPerformance and SalesPerformance 
records without sales_person_id links.
"""

import sys
from pathlib import Path
import pandas as pd
import psycopg2
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_orphaned_user_performance(conn):
    """Analyze orphaned UserPerformance records."""
    cursor = conn.cursor()
    
    # Find all UserPerformance records without sales_person_id
    cursor.execute("""
        SELECT 
            up.id,
            up.name,
            up.sales_person_id,
            up.user_status,
            up.total_calls,
            up.avg_calls_per_day,
            up.inbound_count,
            up.outbound_count,
            up.missed_percent,
            up.avg_handle_time,
            up.created_at,
            up.updated_at
        FROM user_performance up
        WHERE up.sales_person_id IS NULL
        ORDER BY up.name
    """)
    
    columns = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns=columns)
    
    cursor.close()
    return df


def analyze_orphaned_sales_performance(conn):
    """Analyze orphaned SalesPerformance records."""
    cursor = conn.cursor()
    
    # Find all SalesPerformance records without sales_person_id
    cursor.execute("""
        SELECT 
            spf.id,
            spf.name,
            spf.sales_person_id,
            spf.leads_received,
            spf.bad,
            spf.percent_bad,
            spf.sent,
            spf.percent_sent,
            spf.pending,
            spf.percent_pending,
            spf.booked,
            spf.percent_booked,
            spf.lost,
            spf.percent_lost,
            spf.cancelled,
            spf.percent_cancelled,
            spf.booked_total,
            spf.average_booking,
            spf.created_at,
            spf.updated_at
        FROM sales_performance spf
        WHERE spf.sales_person_id IS NULL
        ORDER BY spf.name
    """)
    
    columns = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns=columns)
    
    cursor.close()
    return df


def find_potential_matches(conn, name: str):
    """Find potential SalesPerson matches for a given name."""
    cursor = conn.cursor()
    
    # Try exact match first
    cursor.execute("""
        SELECT id, name, normalized_name
        FROM sales_persons
        WHERE name = %s OR normalized_name = %s
    """, (name, name.lower().strip()))
    
    exact_match = cursor.fetchone()
    if exact_match:
        cursor.close()
        return [exact_match]
    
    # Try fuzzy matching (case-insensitive, partial)
    cursor.execute("""
        SELECT id, name, normalized_name
        FROM sales_persons
        WHERE LOWER(name) LIKE %s 
           OR LOWER(normalized_name) LIKE %s
           OR LOWER(name) LIKE %s
           OR LOWER(normalized_name) LIKE %s
        ORDER BY 
            CASE 
                WHEN LOWER(name) = LOWER(%s) THEN 1
                WHEN LOWER(normalized_name) = LOWER(%s) THEN 2
                WHEN LOWER(name) LIKE %s THEN 3
                ELSE 4
            END
        LIMIT 5
    """, (
        f"%{name.lower()}%",
        f"%{name.lower()}%",
        f"{name.lower()}%",
        f"{name.lower()}%",
        name.lower(),
        name.lower(),
        f"{name.lower()}%"
    ))
    
    matches = cursor.fetchall()
    cursor.close()
    return matches


def generate_analysis_report(conn):
    """Generate comprehensive analysis report."""
    logger.info("Analyzing orphaned UserPerformance records...")
    up_df = analyze_orphaned_user_performance(conn)
    
    logger.info("Analyzing orphaned SalesPerformance records...")
    spf_df = analyze_orphaned_sales_performance(conn)
    
    # Find potential matches for each orphaned record
    logger.info("Finding potential matches for orphaned records...")
    
    up_matches = []
    for _, row in up_df.iterrows():
        matches = find_potential_matches(conn, row['name'])
        up_matches.append({
            'user_performance_id': row['id'],
            'user_performance_name': row['name'],
            'potential_matches': len(matches),
            'match_details': matches
        })
    
    spf_matches = []
    for _, row in spf_df.iterrows():
        matches = find_potential_matches(conn, row['name'])
        spf_matches.append({
            'sales_performance_id': row['id'],
            'sales_performance_name': row['name'],
            'potential_matches': len(matches),
            'match_details': matches
        })
    
    # Generate summary
    summary = {
        'orphaned_user_performance_count': len(up_df),
        'orphaned_sales_performance_count': len(spf_df),
        'total_orphaned': len(up_df) + len(spf_df),
        'user_performance_with_matches': sum(1 for m in up_matches if m['potential_matches'] > 0),
        'sales_performance_with_matches': sum(1 for m in spf_matches if m['potential_matches'] > 0),
    }
    
    return {
        'summary': summary,
        'orphaned_user_performance': up_df,
        'orphaned_sales_performance': spf_df,
        'user_performance_matches': up_matches,
        'sales_performance_matches': spf_matches
    }


def save_report(report, output_dir: Path):
    """Save analysis report to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary
    summary_df = pd.DataFrame([report['summary']])
    summary_path = output_dir / f"orphaned_records_summary_{timestamp}.csv"
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"Saved summary to {summary_path}")
    
    # Save orphaned records
    if not report['orphaned_user_performance'].empty:
        up_path = output_dir / f"orphaned_user_performance_{timestamp}.csv"
        report['orphaned_user_performance'].to_csv(up_path, index=False)
        logger.info(f"Saved {len(report['orphaned_user_performance'])} orphaned UserPerformance records")
    
    if not report['orphaned_sales_performance'].empty:
        spf_path = output_dir / f"orphaned_sales_performance_{timestamp}.csv"
        report['orphaned_sales_performance'].to_csv(spf_path, index=False)
        logger.info(f"Saved {len(report['orphaned_sales_performance'])} orphaned SalesPerformance records")
    
    # Save match details
    up_matches_df = pd.DataFrame(report['user_performance_matches'])
    if not up_matches_df.empty:
        matches_path = output_dir / f"user_performance_potential_matches_{timestamp}.csv"
        up_matches_df.to_csv(matches_path, index=False)
        logger.info(f"Saved potential matches for UserPerformance records")
    
    spf_matches_df = pd.DataFrame(report['sales_performance_matches'])
    if not spf_matches_df.empty:
        matches_path = output_dir / f"sales_performance_potential_matches_{timestamp}.csv"
        spf_matches_df.to_csv(matches_path, index=False)
        logger.info(f"Saved potential matches for SalesPerformance records")
    
    return output_dir


def main():
    """Main analysis function."""
    logger.info("Starting comprehensive orphaned records analysis")
    
    conn = get_db_connection()
    try:
        report = generate_analysis_report(conn)
        
        # Print summary
        print("\n" + "="*80)
        print("ORPHANED RECORDS ANALYSIS SUMMARY")
        print("="*80)
        print(f"Orphaned UserPerformance records: {report['summary']['orphaned_user_performance_count']}")
        print(f"Orphaned SalesPerformance records: {report['summary']['orphaned_sales_performance_count']}")
        print(f"Total orphaned records: {report['summary']['total_orphaned']}")
        print(f"UserPerformance with potential matches: {report['summary']['user_performance_with_matches']}")
        print(f"SalesPerformance with potential matches: {report['summary']['sales_performance_with_matches']}")
        print("="*80 + "\n")
        
        # Save report
        output_dir = Path("reports/orphaned_performance_analysis")
        save_report(report, output_dir)
        
        logger.info("Analysis complete")
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        logger.exception(e)
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

