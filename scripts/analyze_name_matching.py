#!/usr/bin/env python3
"""
Analyze name matching issues between SalesPerson, SalesPerformance, and UserPerformance.
Identifies exact matches, partial matches, and no matches.
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


def normalize_name(name: str) -> str:
    """Normalize name for comparison."""
    if not name:
        return ""
    return name.strip().lower()


def analyze_sales_person_sales_performance_matching(conn):
    """Analyze name matching between SalesPerson and SalesPerformance."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            sp.id as sales_person_id,
            sp.name as sales_person_name,
            spf.id as sales_performance_id,
            spf.name as sales_performance_name,
            spf.sales_person_id
        FROM sales_persons sp
        LEFT JOIN sales_performance spf ON sp.id = spf.sales_person_id
        ORDER BY sp.name
    """)
    results = cursor.fetchall()
    
    matches = []
    for sp_id, sp_name, spf_id, spf_name, spf_sp_id in results:
        if spf_id is None:
            matches.append({
                'sales_person_id': sp_id,
                'sales_person_name': sp_name,
                'sales_performance_id': None,
                'sales_performance_name': None,
                'match_type': 'NO_SALES_PERFORMANCE',
                'exact_match': False,
                'normalized_match': False
            })
        else:
            sp_normalized = normalize_name(sp_name)
            spf_normalized = normalize_name(spf_name)
            exact = sp_normalized == spf_normalized
            normalized = sp_normalized == spf_normalized
            
            # Check for partial matches
            partial = False
            if not exact:
                # Check if one starts with the other
                if sp_normalized.startswith(spf_normalized) or spf_normalized.startswith(sp_normalized):
                    partial = True
                # Check for common variations
                elif sp_normalized.replace(' ', '') == spf_normalized.replace(' ', ''):
                    partial = True
            
            match_type = 'EXACT' if exact else ('PARTIAL' if partial else 'MISMATCH')
            
            matches.append({
                'sales_person_id': sp_id,
                'sales_person_name': sp_name,
                'sales_performance_id': spf_id,
                'sales_performance_name': spf_name,
                'match_type': match_type,
                'exact_match': exact,
                'normalized_match': normalized,
                'partial_match': partial
            })
    
    cursor.close()
    return pd.DataFrame(matches)


def analyze_sales_person_user_performance_matching(conn):
    """Analyze name matching between SalesPerson and UserPerformance."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            sp.id as sales_person_id,
            sp.name as sales_person_name,
            up.id as user_performance_id,
            up.name as user_performance_name,
            up.sales_person_id
        FROM sales_persons sp
        LEFT JOIN user_performance up ON sp.id = up.sales_person_id
        ORDER BY sp.name
    """)
    results = cursor.fetchall()
    
    matches = []
    for sp_id, sp_name, up_id, up_name, up_sp_id in results:
        if up_id is None:
            matches.append({
                'sales_person_id': sp_id,
                'sales_person_name': sp_name,
                'user_performance_id': None,
                'user_performance_name': None,
                'match_type': 'NO_USER_PERFORMANCE',
                'exact_match': False,
                'normalized_match': False
            })
        else:
            sp_normalized = normalize_name(sp_name)
            up_normalized = normalize_name(up_name)
            exact = sp_normalized == up_normalized
            normalized = sp_normalized == up_normalized
            
            # Check for partial matches
            partial = False
            if not exact:
                if sp_normalized.startswith(up_normalized) or up_normalized.startswith(sp_normalized):
                    partial = True
                elif sp_normalized.replace(' ', '') == up_normalized.replace(' ', ''):
                    partial = True
            
            match_type = 'EXACT' if exact else ('PARTIAL' if partial else 'MISMATCH')
            
            matches.append({
                'sales_person_id': sp_id,
                'sales_person_name': sp_name,
                'user_performance_id': up_id,
                'user_performance_name': up_name,
                'match_type': match_type,
                'exact_match': exact,
                'normalized_match': normalized,
                'partial_match': partial
            })
    
    cursor.close()
    return pd.DataFrame(matches)


def analyze_orphaned_name_matching(conn):
    """Find SalesPerformance/UserPerformance records that could match SalesPerson by name but aren't linked."""
    cursor = conn.cursor()
    
    # SalesPerformance without sales_person_id that might match
    cursor.execute("""
        SELECT 
            spf.id,
            spf.name,
            sp.id as potential_sales_person_id,
            sp.name as potential_sales_person_name,
            CASE 
                WHEN LOWER(TRIM(spf.name)) = LOWER(TRIM(sp.name)) THEN 'EXACT'
                WHEN LOWER(TRIM(spf.name)) LIKE LOWER(TRIM(sp.name)) || '%' THEN 'STARTS_WITH'
                WHEN LOWER(TRIM(sp.name)) LIKE LOWER(TRIM(spf.name)) || '%' THEN 'SP_STARTS_WITH'
                ELSE 'PARTIAL'
            END as match_type
        FROM sales_performance spf
        LEFT JOIN sales_persons sp ON LOWER(TRIM(spf.name)) = LOWER(TRIM(sp.name))
            OR LOWER(TRIM(spf.name)) LIKE LOWER(TRIM(sp.name)) || '%'
            OR LOWER(TRIM(sp.name)) LIKE LOWER(TRIM(spf.name)) || '%'
        WHERE spf.sales_person_id IS NULL
        ORDER BY spf.name
    """)
    orphaned_spf = cursor.fetchall()
    
    # UserPerformance without sales_person_id that might match
    cursor.execute("""
        SELECT 
            up.id,
            up.name,
            sp.id as potential_sales_person_id,
            sp.name as potential_sales_person_name,
            CASE 
                WHEN LOWER(TRIM(up.name)) = LOWER(TRIM(sp.name)) THEN 'EXACT'
                WHEN LOWER(TRIM(up.name)) LIKE LOWER(TRIM(sp.name)) || '%' THEN 'STARTS_WITH'
                WHEN LOWER(TRIM(sp.name)) LIKE LOWER(TRIM(up.name)) || '%' THEN 'SP_STARTS_WITH'
                ELSE 'PARTIAL'
            END as match_type
        FROM user_performance up
        LEFT JOIN sales_persons sp ON LOWER(TRIM(up.name)) = LOWER(TRIM(sp.name))
            OR LOWER(TRIM(up.name)) LIKE LOWER(TRIM(sp.name)) || '%'
            OR LOWER(TRIM(sp.name)) LIKE LOWER(TRIM(up.name)) || '%'
        WHERE up.sales_person_id IS NULL
        ORDER BY up.name
    """)
    orphaned_up = cursor.fetchall()
    
    cursor.close()
    
    return {
        'orphaned_sales_performance_matches': pd.DataFrame(
            orphaned_spf,
            columns=['sales_performance_id', 'sales_performance_name', 'potential_sales_person_id', 'potential_sales_person_name', 'match_type']
        ),
        'orphaned_user_performance_matches': pd.DataFrame(
            orphaned_up,
            columns=['user_performance_id', 'user_performance_name', 'potential_sales_person_id', 'potential_sales_person_name', 'match_type']
        )
    }


def identify_name_variations(conn):
    """Identify SalesPerson name variations that should be merged."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            LOWER(TRIM(name)) as normalized_name,
            COUNT(*) as count,
            array_agg(name ORDER BY name) as variations,
            array_agg(id ORDER BY name) as ids
        FROM sales_persons
        GROUP BY LOWER(TRIM(name))
        HAVING COUNT(*) > 1
        ORDER BY count DESC, normalized_name
    """)
    variations = cursor.fetchall()
    
    variation_list = []
    for norm_name, count, names, ids in variations:
        variation_list.append({
            'normalized_name': norm_name,
            'variation_count': count,
            'variations': ', '.join(names),
            'ids': ', '.join(ids)
        })
    
    cursor.close()
    return pd.DataFrame(variation_list)


def main():
    """Main analysis function."""
    logger.info("Starting name matching analysis")
    
    conn = get_db_connection()
    
    try:
        logger.info("Analyzing SalesPerson ↔ SalesPerformance matching...")
        sp_spf_matching = analyze_sales_person_sales_performance_matching(conn)
        
        logger.info("Analyzing SalesPerson ↔ UserPerformance matching...")
        sp_up_matching = analyze_sales_person_user_performance_matching(conn)
        
        logger.info("Finding orphaned records with potential matches...")
        orphaned_matches = analyze_orphaned_name_matching(conn)
        
        logger.info("Identifying name variations...")
        name_variations = identify_name_variations(conn)
        
        # Save reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path("reports") / f"name_matching_analysis_{timestamp}"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        sp_spf_matching.to_csv(reports_dir / "sales_person_sales_performance_matching.csv", index=False)
        sp_up_matching.to_csv(reports_dir / "sales_person_user_performance_matching.csv", index=False)
        orphaned_matches['orphaned_sales_performance_matches'].to_csv(
            reports_dir / "orphaned_sales_performance_potential_matches.csv", index=False
        )
        orphaned_matches['orphaned_user_performance_matches'].to_csv(
            reports_dir / "orphaned_user_performance_potential_matches.csv", index=False
        )
        name_variations.to_csv(reports_dir / "name_variations_to_merge.csv", index=False)
        
        # Print summary
        print("\n" + "="*80)
        print("NAME MATCHING ANALYSIS SUMMARY")
        print("="*80)
        print(f"\nReports saved to: {reports_dir}")
        
        exact_spf = len(sp_spf_matching[sp_spf_matching['exact_match'] == True])
        partial_spf = len(sp_spf_matching[sp_spf_matching['partial_match'] == True])
        mismatch_spf = len(sp_spf_matching[sp_spf_matching['match_type'] == 'MISMATCH'])
        no_spf = len(sp_spf_matching[sp_spf_matching['match_type'] == 'NO_SALES_PERFORMANCE'])
        
        exact_up = len(sp_up_matching[sp_up_matching['exact_match'] == True])
        partial_up = len(sp_up_matching[sp_up_matching['partial_match'] == True])
        mismatch_up = len(sp_up_matching[sp_up_matching['match_type'] == 'MISMATCH'])
        no_up = len(sp_up_matching[sp_up_matching['match_type'] == 'NO_USER_PERFORMANCE'])
        
        print(f"\nSalesPerson ↔ SalesPerformance:")
        print(f"  Exact matches: {exact_spf}")
        print(f"  Partial matches: {partial_spf}")
        print(f"  Mismatches: {mismatch_spf}")
        print(f"  Missing SalesPerformance: {no_spf}")
        
        print(f"\nSalesPerson ↔ UserPerformance:")
        print(f"  Exact matches: {exact_up}")
        print(f"  Partial matches: {partial_up}")
        print(f"  Mismatches: {mismatch_up}")
        print(f"  Missing UserPerformance: {no_up}")
        
        print(f"\nName variations to merge: {len(name_variations)}")
        if len(name_variations) > 0:
            print("\nVariations found:")
            for _, row in name_variations.iterrows():
                print(f"  {row['normalized_name']}: {row['variations']}")
        
        logger.info("Name matching analysis complete")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()

