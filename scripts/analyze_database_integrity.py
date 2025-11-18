#!/usr/bin/env python3
"""
Comprehensive database integrity analysis.
Identifies relationship gaps, missing records, and data inconsistencies.
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


def analyze_sales_person_relationships(conn):
    """Analyze SalesPerson relationships with other tables."""
    cursor = conn.cursor()
    
    # Get all SalesPersons
    cursor.execute("""
        SELECT id, name, normalized_name
        FROM sales_persons
        ORDER BY name
    """)
    sales_persons = cursor.fetchall()
    
    results = []
    
    for sp_id, sp_name, sp_normalized in sales_persons:
        # Check SalesPerformance
        cursor.execute("""
            SELECT COUNT(*) FROM sales_performance WHERE sales_person_id = %s
        """, (sp_id,))
        spf_count = cursor.fetchone()[0]
        
        # Check UserPerformance
        cursor.execute("""
            SELECT COUNT(*) FROM user_performance WHERE sales_person_id = %s
        """, (sp_id,))
        up_count = cursor.fetchone()[0]
        
        # Check Jobs
        cursor.execute("""
            SELECT COUNT(*) FROM jobs WHERE sales_person_id = %s
        """, (sp_id,))
        jobs_count = cursor.fetchone()[0]
        
        # Check BookedOpportunities
        cursor.execute("""
            SELECT COUNT(*) FROM booked_opportunities WHERE sales_person_id = %s
        """, (sp_id,))
        bo_count = cursor.fetchone()[0]
        
        # Check LeadStatus
        cursor.execute("""
            SELECT COUNT(*) FROM lead_status WHERE sales_person_id = %s
        """, (sp_id,))
        ls_count = cursor.fetchone()[0]
        
        results.append({
            'sales_person_id': sp_id,
            'sales_person_name': sp_name,
            'has_sales_performance': spf_count > 0,
            'has_user_performance': up_count > 0,
            'jobs_count': jobs_count,
            'booked_opportunities_count': bo_count,
            'lead_status_count': ls_count,
            'total_relationships': jobs_count + bo_count + ls_count
        })
    
    cursor.close()
    return pd.DataFrame(results)


def analyze_orphaned_records(conn):
    """Find orphaned records without proper relationships."""
    cursor = conn.cursor()
    
    # Orphaned UserPerformance
    cursor.execute("""
        SELECT id, name, user_status
        FROM user_performance
        WHERE sales_person_id IS NULL
        ORDER BY name
    """)
    orphaned_up = cursor.fetchall()
    
    # Orphaned SalesPerformance
    cursor.execute("""
        SELECT id, name
        FROM sales_performance
        WHERE sales_person_id IS NULL
        ORDER BY name
    """)
    orphaned_spf = cursor.fetchall()
    
    # SalesPerformance without matching SalesPerson
    cursor.execute("""
        SELECT spf.id, spf.name, spf.sales_person_id
        FROM sales_performance spf
        LEFT JOIN sales_persons sp ON spf.sales_person_id = sp.id
        WHERE spf.sales_person_id IS NOT NULL AND sp.id IS NULL
    """)
    spf_bad_fk = cursor.fetchall()
    
    # UserPerformance without matching SalesPerson
    cursor.execute("""
        SELECT up.id, up.name, up.sales_person_id
        FROM user_performance up
        LEFT JOIN sales_persons sp ON up.sales_person_id = sp.id
        WHERE up.sales_person_id IS NOT NULL AND sp.id IS NULL
    """)
    up_bad_fk = cursor.fetchall()
    
    cursor.close()
    
    return {
        'orphaned_user_performance': pd.DataFrame(orphaned_up, columns=['id', 'name', 'user_status']),
        'orphaned_sales_performance': pd.DataFrame(orphaned_spf, columns=['id', 'name']),
        'sales_performance_bad_fk': pd.DataFrame(spf_bad_fk, columns=['id', 'name', 'sales_person_id']),
        'user_performance_bad_fk': pd.DataFrame(up_bad_fk, columns=['id', 'name', 'sales_person_id'])
    }


def analyze_name_mismatches(conn):
    """Find name mismatches between tables."""
    cursor = conn.cursor()
    
    # SalesPerson vs SalesPerformance name mismatches
    cursor.execute("""
        SELECT 
            sp.id as sales_person_id,
            sp.name as sales_person_name,
            spf.id as sales_performance_id,
            spf.name as sales_performance_name,
            CASE WHEN LOWER(TRIM(sp.name)) = LOWER(TRIM(spf.name)) THEN 'Match' ELSE 'Mismatch' END as match_status
        FROM sales_persons sp
        JOIN sales_performance spf ON sp.id = spf.sales_person_id
        WHERE LOWER(TRIM(sp.name)) != LOWER(TRIM(spf.name))
        ORDER BY sp.name
    """)
    sp_spf_mismatches = cursor.fetchall()
    
    # SalesPerson vs UserPerformance name mismatches
    cursor.execute("""
        SELECT 
            sp.id as sales_person_id,
            sp.name as sales_person_name,
            up.id as user_performance_id,
            up.name as user_performance_name,
            CASE WHEN LOWER(TRIM(sp.name)) = LOWER(TRIM(up.name)) THEN 'Match' ELSE 'Mismatch' END as match_status
        FROM sales_persons sp
        JOIN user_performance up ON sp.id = up.sales_person_id
        WHERE LOWER(TRIM(sp.name)) != LOWER(TRIM(up.name))
        ORDER BY sp.name
    """)
    sp_up_mismatches = cursor.fetchall()
    
    cursor.close()
    
    return {
        'sales_person_sales_performance_mismatches': pd.DataFrame(
            sp_spf_mismatches,
            columns=['sales_person_id', 'sales_person_name', 'sales_performance_id', 'sales_performance_name', 'match_status']
        ),
        'sales_person_user_performance_mismatches': pd.DataFrame(
            sp_up_mismatches,
            columns=['sales_person_id', 'sales_person_name', 'user_performance_id', 'user_performance_name', 'match_status']
        )
    }


def find_ibrahim_k_references(conn):
    """Find all references to Ibrahim K."""
    cursor = conn.cursor()
    
    # Find Ibrahim K SalesPerson
    cursor.execute("""
        SELECT id, name FROM sales_persons WHERE name ILIKE '%ibrahim%' OR normalized_name ILIKE '%ibrahim%'
    """)
    ibrahim_sp = cursor.fetchall()
    
    # Find all foreign key references
    cursor.execute("""
        SELECT 'jobs' as table_name, COUNT(*) as count
        FROM jobs j
        JOIN sales_persons sp ON j.sales_person_id = sp.id
        WHERE sp.name ILIKE '%ibrahim%' OR sp.normalized_name ILIKE '%ibrahim%'
        UNION ALL
        SELECT 'booked_opportunities', COUNT(*)
        FROM booked_opportunities bo
        JOIN sales_persons sp ON bo.sales_person_id = sp.id
        WHERE sp.name ILIKE '%ibrahim%' OR sp.normalized_name ILIKE '%ibrahim%'
        UNION ALL
        SELECT 'lead_status', COUNT(*)
        FROM lead_status ls
        JOIN sales_persons sp ON ls.sales_person_id = sp.id
        WHERE sp.name ILIKE '%ibrahim%' OR sp.normalized_name ILIKE '%ibrahim%'
        UNION ALL
        SELECT 'user_performance', COUNT(*)
        FROM user_performance up
        JOIN sales_persons sp ON up.sales_person_id = sp.id
        WHERE sp.name ILIKE '%ibrahim%' OR sp.normalized_name ILIKE '%ibrahim%'
        UNION ALL
        SELECT 'sales_performance', COUNT(*)
        FROM sales_performance spf
        JOIN sales_persons sp ON spf.sales_person_id = sp.id
        WHERE sp.name ILIKE '%ibrahim%' OR sp.normalized_name ILIKE '%ibrahim%'
    """)
    ibrahim_refs = cursor.fetchall()
    
    # Find name references in SalesPerformance/UserPerformance
    cursor.execute("""
        SELECT 'sales_performance' as table_name, id, name
        FROM sales_performance
        WHERE name ILIKE '%ibrahim%'
        UNION ALL
        SELECT 'user_performance', id, name
        FROM user_performance
        WHERE name ILIKE '%ibrahim%'
    """)
    ibrahim_names = cursor.fetchall()
    
    cursor.close()
    
    return {
        'ibrahim_sales_persons': pd.DataFrame(ibrahim_sp, columns=['id', 'name']),
        'ibrahim_references': pd.DataFrame(ibrahim_refs, columns=['table_name', 'count']),
        'ibrahim_name_references': pd.DataFrame(ibrahim_names, columns=['table_name', 'id', 'name'])
    }


def generate_summary_report(conn):
    """Generate summary statistics."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            'sales_persons' as table_name,
            COUNT(*) as total_records
        FROM sales_persons
        UNION ALL
        SELECT 'sales_performance', COUNT(*)
        FROM sales_performance
        UNION ALL
        SELECT 'user_performance', COUNT(*)
        FROM user_performance
        UNION ALL
        SELECT 'jobs', COUNT(*)
        FROM jobs
        UNION ALL
        SELECT 'booked_opportunities', COUNT(*)
        FROM booked_opportunities
        UNION ALL
        SELECT 'lead_status', COUNT(*)
        FROM lead_status
    """)
    summary = cursor.fetchall()
    
    cursor.close()
    return pd.DataFrame(summary, columns=['table_name', 'total_records'])


def main():
    """Main analysis function."""
    logger.info("Starting database integrity analysis")
    
    conn = get_db_connection()
    
    try:
        # Generate reports
        logger.info("Analyzing SalesPerson relationships...")
        sp_relationships = analyze_sales_person_relationships(conn)
        
        logger.info("Finding orphaned records...")
        orphaned = analyze_orphaned_records(conn)
        
        logger.info("Analyzing name mismatches...")
        name_mismatches = analyze_name_mismatches(conn)
        
        logger.info("Finding Ibrahim K references...")
        ibrahim_refs = find_ibrahim_k_references(conn)
        
        logger.info("Generating summary...")
        summary = generate_summary_report(conn)
        
        # Save reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path("reports") / f"database_integrity_analysis_{timestamp}"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        sp_relationships.to_csv(reports_dir / "sales_person_relationships.csv", index=False)
        orphaned['orphaned_user_performance'].to_csv(reports_dir / "orphaned_user_performance.csv", index=False)
        orphaned['orphaned_sales_performance'].to_csv(reports_dir / "orphaned_sales_performance.csv", index=False)
        orphaned['sales_performance_bad_fk'].to_csv(reports_dir / "sales_performance_bad_fk.csv", index=False)
        orphaned['user_performance_bad_fk'].to_csv(reports_dir / "user_performance_bad_fk.csv", index=False)
        name_mismatches['sales_person_sales_performance_mismatches'].to_csv(
            reports_dir / "name_mismatches_sales_performance.csv", index=False
        )
        name_mismatches['sales_person_user_performance_mismatches'].to_csv(
            reports_dir / "name_mismatches_user_performance.csv", index=False
        )
        ibrahim_refs['ibrahim_sales_persons'].to_csv(reports_dir / "ibrahim_sales_persons.csv", index=False)
        ibrahim_refs['ibrahim_references'].to_csv(reports_dir / "ibrahim_references.csv", index=False)
        ibrahim_refs['ibrahim_name_references'].to_csv(reports_dir / "ibrahim_name_references.csv", index=False)
        summary.to_csv(reports_dir / "summary.csv", index=False)
        
        # Print summary
        print("\n" + "="*80)
        print("DATABASE INTEGRITY ANALYSIS SUMMARY")
        print("="*80)
        print(f"\nReports saved to: {reports_dir}")
        print(f"\nSummary Statistics:")
        print(summary.to_string(index=False))
        
        print(f"\nSalesPersons missing SalesPerformance: {len(sp_relationships[~sp_relationships['has_sales_performance']])}")
        print(f"SalesPersons missing UserPerformance: {len(sp_relationships[~sp_relationships['has_user_performance']])}")
        print(f"Orphaned UserPerformance records: {len(orphaned['orphaned_user_performance'])}")
        print(f"Orphaned SalesPerformance records: {len(orphaned['orphaned_sales_performance'])}")
        print(f"Ibrahim K SalesPersons found: {len(ibrahim_refs['ibrahim_sales_persons'])}")
        print(f"Total Ibrahim K references: {ibrahim_refs['ibrahim_references']['count'].sum()}")
        
        logger.info("Analysis complete")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()

