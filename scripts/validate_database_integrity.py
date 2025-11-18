#!/usr/bin/env python3
"""
Validate database integrity after all fixes.
Generates comprehensive validation report.
"""

import sys
from pathlib import Path
import pandas as pd
import psycopg2
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection
from src.utils.progress_monitor import log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_ibrahim_k_swap(conn):
    """Verify all Ibrahim K references have been swapped to Brian K."""
    cursor = conn.cursor()
    
    # Check for any remaining Ibrahim K references
    cursor.execute("""
        SELECT COUNT(*) FROM sales_persons 
        WHERE name ILIKE '%ibrahim%' OR normalized_name ILIKE '%ibrahim%'
    """)
    ibrahim_sp = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM sales_performance 
        WHERE name ILIKE '%ibrahim%'
    """)
    ibrahim_spf = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM user_performance 
        WHERE name ILIKE '%ibrahim%'
    """)
    ibrahim_up = cursor.fetchone()[0]
    
    cursor.close()
    
    total_ibrahim = ibrahim_sp + ibrahim_spf + ibrahim_up
    
    return {
        'ibrahim_sales_persons': ibrahim_sp,
        'ibrahim_sales_performance': ibrahim_spf,
        'ibrahim_user_performance': ibrahim_up,
        'total_ibrahim_references': total_ibrahim,
        'swap_complete': total_ibrahim == 0
    }


def validate_sales_performance_coverage(conn):
    """Verify all SalesPersons have SalesPerformance records."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sales_persons,
            COUNT(spf.id) as with_sales_performance,
            COUNT(*) - COUNT(spf.id) as missing_sales_performance
        FROM sales_persons sp
        LEFT JOIN sales_performance spf ON sp.id = spf.sales_person_id
    """)
    result = cursor.fetchone()
    
    cursor.close()
    
    return {
        'total_sales_persons': result[0],
        'with_sales_performance': result[1],
        'missing_sales_performance': result[2],
        'coverage_percent': (result[1] / result[0] * 100) if result[0] > 0 else 0,
        'all_covered': result[2] == 0
    }


def validate_user_performance_coverage(conn):
    """Verify all SalesPersons have UserPerformance records."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sales_persons,
            COUNT(up.id) as with_user_performance,
            COUNT(*) - COUNT(up.id) as missing_user_performance
        FROM sales_persons sp
        LEFT JOIN user_performance up ON sp.id = up.sales_person_id
    """)
    result = cursor.fetchone()
    
    cursor.close()
    
    return {
        'total_sales_persons': result[0],
        'with_user_performance': result[1],
        'missing_user_performance': result[2],
        'coverage_percent': (result[1] / result[0] * 100) if result[0] > 0 else 0
    }


def validate_user_performance_links(conn):
    """Verify UserPerformance records are linked to SalesPersons."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_user_performance,
            COUNT(sales_person_id) as linked,
            COUNT(*) - COUNT(sales_person_id) as unlinked
        FROM user_performance
    """)
    result = cursor.fetchone()
    
    cursor.close()
    
    return {
        'total_user_performance': result[0],
        'linked': result[1],
        'unlinked': result[2],
        'linkage_percent': (result[1] / result[0] * 100) if result[0] > 0 else 0
    }


def validate_name_consistency(conn):
    """Verify name consistency across tables."""
    cursor = conn.cursor()
    
    # Check SalesPerson vs SalesPerformance name mismatches
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sales_persons sp
        JOIN sales_performance spf ON sp.id = spf.sales_person_id
        WHERE LOWER(TRIM(sp.name)) != LOWER(TRIM(spf.name))
    """)
    sp_spf_mismatches = cursor.fetchone()[0]
    
    # Check SalesPerson vs UserPerformance name mismatches
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sales_persons sp
        JOIN user_performance up ON sp.id = up.sales_person_id
        WHERE LOWER(TRIM(sp.name)) != LOWER(TRIM(up.name))
    """)
    sp_up_mismatches = cursor.fetchone()[0]
    
    cursor.close()
    
    return {
        'sales_person_sales_performance_mismatches': sp_spf_mismatches,
        'sales_person_user_performance_mismatches': sp_up_mismatches,
        'total_mismatches': sp_spf_mismatches + sp_up_mismatches,
        'all_consistent': (sp_spf_mismatches + sp_up_mismatches) == 0
    }


def validate_no_duplicate_sales_persons(conn):
    """Verify no duplicate SalesPerson names exist."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            LOWER(TRIM(name)) as normalized_name,
            COUNT(*) as count
        FROM sales_persons
        GROUP BY LOWER(TRIM(name))
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    cursor.close()
    
    return {
        'duplicate_count': len(duplicates),
        'duplicates': [{'name': d[0], 'count': d[1]} for d in duplicates],
        'no_duplicates': len(duplicates) == 0
    }


def validate_customer_deduplication_log_removed(conn):
    """Verify CustomerDeduplicationLog table has been removed."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'customer_deduplication_logs'
        )
    """)
    table_exists = cursor.fetchone()[0]
    
    cursor.close()
    
    return {
        'table_exists': table_exists,
        'removed': not table_exists
    }


def validate_foreign_key_integrity(conn):
    """Verify foreign key relationships are intact."""
    cursor = conn.cursor()
    
    # Check for broken foreign keys
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sales_performance spf
        WHERE spf.sales_person_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM sales_persons sp WHERE sp.id = spf.sales_person_id
        )
    """)
    broken_spf_fk = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_performance up
        WHERE up.sales_person_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM sales_persons sp WHERE sp.id = up.sales_person_id
        )
    """)
    broken_up_fk = cursor.fetchone()[0]
    
    cursor.close()
    
    return {
        'broken_sales_performance_fk': broken_spf_fk,
        'broken_user_performance_fk': broken_up_fk,
        'total_broken_fk': broken_spf_fk + broken_up_fk,
        'all_fk_valid': (broken_spf_fk + broken_up_fk) == 0
    }


def generate_summary_statistics(conn):
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
    """Main validation function."""
    logger.info("Starting database integrity validation")
    conn = get_db_connection()
    
    try:
        log_step("Validation", "Validating Ibrahim K swap")
        ibrahim_validation = validate_ibrahim_k_swap(conn)
        
        log_step("Validation", "Validating SalesPerformance coverage")
        spf_validation = validate_sales_performance_coverage(conn)
        
        log_step("Validation", "Validating UserPerformance coverage")
        up_validation = validate_user_performance_coverage(conn)
        
        log_step("Validation", "Validating UserPerformance links")
        up_links_validation = validate_user_performance_links(conn)
        
        log_step("Validation", "Validating name consistency")
        name_validation = validate_name_consistency(conn)
        
        log_step("Validation", "Validating no duplicate SalesPersons")
        duplicate_validation = validate_no_duplicate_sales_persons(conn)
        
        log_step("Validation", "Validating CustomerDeduplicationLog removal")
        dedup_validation = validate_customer_deduplication_log_removed(conn)
        
        log_step("Validation", "Validating foreign key integrity")
        fk_validation = validate_foreign_key_integrity(conn)
        
        log_step("Validation", "Generating summary statistics")
        summary = generate_summary_statistics(conn)
        
        # Save reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path("reports") / f"database_integrity_validation_{timestamp}"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Create validation report
        validation_report = {
            'ibrahim_k_swap': ibrahim_validation,
            'sales_performance_coverage': spf_validation,
            'user_performance_coverage': up_validation,
            'user_performance_links': up_links_validation,
            'name_consistency': name_validation,
            'duplicate_sales_persons': duplicate_validation,
            'customer_deduplication_log_removed': dedup_validation,
            'foreign_key_integrity': fk_validation,
        }
        
        import json
        with open(reports_dir / "validation_report.json", 'w') as f:
            json.dump(validation_report, f, indent=2, default=str)
        
        summary.to_csv(reports_dir / "summary_statistics.csv", index=False)
        
        # Print summary
        print("\n" + "="*80)
        print("DATABASE INTEGRITY VALIDATION REPORT")
        print("="*80)
        print(f"\nReports saved to: {reports_dir}")
        
        print(f"\nSummary Statistics:")
        print(summary.to_string(index=False))
        
        print(f"\nValidation Results:")
        print(f"  Ibrahim K Swap: {'✓ PASS' if ibrahim_validation['swap_complete'] else '✗ FAIL'} "
              f"({ibrahim_validation['total_ibrahim_references']} remaining references)")
        print(f"  SalesPerformance Coverage: {'✓ PASS' if spf_validation['all_covered'] else '✗ FAIL'} "
              f"({spf_validation['coverage_percent']:.1f}% - {spf_validation['missing_sales_performance']} missing)")
        print(f"  UserPerformance Links: {up_links_validation['linkage_percent']:.1f}% "
              f"({up_links_validation['linked']}/{up_links_validation['total_user_performance']} linked)")
        print(f"  Name Consistency: {'✓ PASS' if name_validation['all_consistent'] else '✗ FAIL'} "
              f"({name_validation['total_mismatches']} mismatches)")
        print(f"  No Duplicate SalesPersons: {'✓ PASS' if duplicate_validation['no_duplicates'] else '✗ FAIL'} "
              f"({duplicate_validation['duplicate_count']} duplicates)")
        print(f"  CustomerDeduplicationLog Removed: {'✓ PASS' if dedup_validation['removed'] else '✗ FAIL'}")
        print(f"  Foreign Key Integrity: {'✓ PASS' if fk_validation['all_fk_valid'] else '✗ FAIL'} "
              f"({fk_validation['total_broken_fk']} broken)")
        
        # Overall status
        all_passed = (
            ibrahim_validation['swap_complete'] and
            spf_validation['all_covered'] and
            name_validation['all_consistent'] and
            duplicate_validation['no_duplicates'] and
            dedup_validation['removed'] and
            fk_validation['all_fk_valid']
        )
        
        print(f"\n{'='*80}")
        if all_passed:
            log_success("All validations PASSED")
        else:
            log_error("Some validations FAILED - see details above")
        print(f"{'='*80}\n")
        
        logger.info("Validation complete")
        return 0 if all_passed else 1
        
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

