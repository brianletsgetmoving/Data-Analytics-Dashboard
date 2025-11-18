#!/usr/bin/env python3
"""
Validate 1:1 relationships between SalesPerson, SalesPerformance, and UserPerformance.
Ensures all records can be tracked across all 3 modules.
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


def validate_user_performance_relationships(conn):
    """Validate that every UserPerformance has SalesPerson and SalesPerformance."""
    cursor = conn.cursor()
    
    # Check UserPerformance records
    cursor.execute("""
        SELECT 
            COUNT(*) as total_user_performance,
            COUNT(up.sales_person_id) as with_sales_person,
            COUNT(spf.id) as with_sales_performance,
            COUNT(*) - COUNT(spf.id) as missing_sales_performance
        FROM user_performance up
        LEFT JOIN sales_persons sp ON up.sales_person_id = sp.id
        LEFT JOIN sales_performance spf ON sp.id = spf.sales_person_id
    """)
    result = cursor.fetchone()
    
    cursor.close()
    
    return {
        'total_user_performance': result[0],
        'with_sales_person': result[1],
        'with_sales_performance': result[2],
        'missing_sales_performance': result[3],
        'all_have_sales_person': result[0] == result[1],
        'all_have_sales_performance': result[0] == result[2],
        'all_valid': result[0] == result[1] == result[2]
    }


def validate_sales_person_relationships(conn):
    """Validate SalesPerson relationships."""
    cursor = conn.cursor()
    
    # Check SalesPerson records
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sales_persons,
            COUNT(spf.id) as with_sales_performance,
            COUNT(up.id) as with_user_performance,
            COUNT(CASE WHEN spf.id IS NOT NULL AND up.id IS NOT NULL THEN 1 END) as with_both
        FROM sales_persons sp
        LEFT JOIN sales_performance spf ON sp.id = spf.sales_person_id
        LEFT JOIN user_performance up ON sp.id = up.sales_person_id
    """)
    result = cursor.fetchone()
    
    cursor.close()
    
    return {
        'total_sales_persons': result[0],
        'with_sales_performance': result[1],
        'with_user_performance': result[2],
        'with_both': result[3]
    }


def validate_sales_performance_relationships(conn):
    """Validate SalesPerformance relationships."""
    cursor = conn.cursor()
    
    # Check SalesPerformance records
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sales_performance,
            COUNT(spf.sales_person_id) as with_sales_person,
            COUNT(up.id) as with_user_performance,
            COUNT(CASE WHEN spf.sales_person_id IS NOT NULL AND up.id IS NOT NULL THEN 1 END) as with_both
        FROM sales_performance spf
        LEFT JOIN sales_persons sp ON spf.sales_person_id = sp.id
        LEFT JOIN user_performance up ON sp.id = up.sales_person_id
    """)
    result = cursor.fetchone()
    
    cursor.close()
    
    return {
        'total_sales_performance': result[0],
        'with_sales_person': result[1],
        'with_user_performance': result[2],
        'with_both': result[3]
    }


def find_relationship_issues(conn):
    """Find any relationship issues."""
    cursor = conn.cursor()
    
    # UserPerformance without SalesPerson
    cursor.execute("""
        SELECT id, name
        FROM user_performance
        WHERE sales_person_id IS NULL
    """)
    up_no_sp = cursor.fetchall()
    
    # UserPerformance where SalesPerson has no SalesPerformance
    cursor.execute("""
        SELECT up.id, up.name, sp.name as sales_person_name
        FROM user_performance up
        JOIN sales_persons sp ON up.sales_person_id = sp.id
        LEFT JOIN sales_performance spf ON sp.id = spf.sales_person_id
        WHERE spf.id IS NULL
    """)
    up_no_spf = cursor.fetchall()
    
    # SalesPerson with multiple UserPerformance
    cursor.execute("""
        SELECT sp.id, sp.name, COUNT(up.id) as user_performance_count
        FROM sales_persons sp
        JOIN user_performance up ON sp.id = up.sales_person_id
        GROUP BY sp.id, sp.name
        HAVING COUNT(up.id) > 1
    """)
    sp_multiple_up = cursor.fetchall()
    
    # SalesPerson with multiple SalesPerformance
    cursor.execute("""
        SELECT sp.id, sp.name, COUNT(spf.id) as sales_performance_count
        FROM sales_persons sp
        JOIN sales_performance spf ON sp.id = spf.sales_person_id
        GROUP BY sp.id, sp.name
        HAVING COUNT(spf.id) > 1
    """)
    sp_multiple_spf = cursor.fetchall()
    
    cursor.close()
    
    return {
        'user_performance_no_sales_person': pd.DataFrame(up_no_sp, columns=['id', 'name']),
        'user_performance_no_sales_performance': pd.DataFrame(up_no_spf, columns=['id', 'name', 'sales_person_name']),
        'sales_person_multiple_user_performance': pd.DataFrame(sp_multiple_up, columns=['id', 'name', 'user_performance_count']),
        'sales_person_multiple_sales_performance': pd.DataFrame(sp_multiple_spf, columns=['id', 'name', 'sales_performance_count'])
    }


def generate_validation_report(up_validation, sp_validation, spf_validation, issues):
    """Generate validation report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path("reports") / f"relationship_validation_{timestamp}"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Save validation results
    validation_results = {
        'user_performance': up_validation,
        'sales_person': sp_validation,
        'sales_performance': spf_validation
    }
    
    import json
    with open(reports_dir / "validation_results.json", 'w') as f:
        json.dump(validation_results, f, indent=2, default=str)
    
    # Save issues
    for issue_name, issue_df in issues.items():
        if len(issue_df) > 0:
            issue_df.to_csv(reports_dir / f"{issue_name}.csv", index=False)
    
    return reports_dir


def main():
    """Main validation function."""
    logger.info("Starting 1:1 relationship validation")
    conn = get_db_connection()
    
    try:
        log_step("Validation", "Validating UserPerformance relationships")
        up_validation = validate_user_performance_relationships(conn)
        
        log_step("Validation", "Validating SalesPerson relationships")
        sp_validation = validate_sales_person_relationships(conn)
        
        log_step("Validation", "Validating SalesPerformance relationships")
        spf_validation = validate_sales_performance_relationships(conn)
        
        log_step("Validation", "Finding relationship issues")
        issues = find_relationship_issues(conn)
        
        # Generate report
        reports_dir = generate_validation_report(up_validation, sp_validation, spf_validation, issues)
        logger.info(f"Reports saved to: {reports_dir}")
        
        # Print summary
        print("\n" + "="*80)
        print("1:1 RELATIONSHIP VALIDATION REPORT")
        print("="*80)
        
        print(f"\nUserPerformance Validation:")
        print(f"  Total records: {up_validation['total_user_performance']}")
        print(f"  With SalesPerson: {up_validation['with_sales_person']} {'✓' if up_validation['all_have_sales_person'] else '✗'}")
        print(f"  With SalesPerformance: {up_validation['with_sales_performance']} {'✓' if up_validation['all_have_sales_performance'] else '✗'}")
        print(f"  All valid: {'✓ PASS' if up_validation['all_valid'] else '✗ FAIL'}")
        
        print(f"\nSalesPerson Validation:")
        print(f"  Total records: {sp_validation['total_sales_persons']}")
        print(f"  With SalesPerformance: {sp_validation['with_sales_performance']}")
        print(f"  With UserPerformance: {sp_validation['with_user_performance']}")
        print(f"  With both: {sp_validation['with_both']}")
        
        print(f"\nSalesPerformance Validation:")
        print(f"  Total records: {spf_validation['total_sales_performance']}")
        print(f"  With SalesPerson: {spf_validation['with_sales_person']}")
        print(f"  With UserPerformance: {spf_validation['with_user_performance']}")
        print(f"  With both: {spf_validation['with_both']}")
        
        # Check for issues
        total_issues = (
            len(issues['user_performance_no_sales_person']) +
            len(issues['user_performance_no_sales_performance']) +
            len(issues['sales_person_multiple_user_performance']) +
            len(issues['sales_person_multiple_sales_performance'])
        )
        
        if total_issues > 0:
            print(f"\n⚠ Issues Found: {total_issues}")
            if len(issues['user_performance_no_sales_person']) > 0:
                print(f"  - UserPerformance without SalesPerson: {len(issues['user_performance_no_sales_person'])}")
            if len(issues['user_performance_no_sales_performance']) > 0:
                print(f"  - UserPerformance without SalesPerformance: {len(issues['user_performance_no_sales_performance'])}")
            if len(issues['sales_person_multiple_user_performance']) > 0:
                print(f"  - SalesPerson with multiple UserPerformance: {len(issues['sales_person_multiple_user_performance'])}")
            if len(issues['sales_person_multiple_sales_performance']) > 0:
                print(f"  - SalesPerson with multiple SalesPerformance: {len(issues['sales_person_multiple_sales_performance'])}")
        else:
            print(f"\n✓ No issues found - all relationships are valid")
        
        # Final status
        all_valid = (
            up_validation['all_valid'] and
            total_issues == 0
        )
        
        print(f"\n{'='*80}")
        if all_valid:
            log_success("All 1:1 relationships are valid - all records can be tracked across all 3 modules")
        else:
            log_error("Some relationship issues found - see details above")
        print(f"{'='*80}\n")
        
        return 0 if all_valid else 1
        
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

