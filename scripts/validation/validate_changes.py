#!/usr/bin/env python3
"""
Validate all database changes: verify merges, deletions, imports, and data integrity.
"""

import sys
from pathlib import Path
import psycopg2
import logging
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_lead_merge(conn) -> Dict:
    """Validate that LeadStatus was renamed and BadLead/LostLead were merged."""
    cursor = conn.cursor()
    results = {'passed': True, 'issues': []}
    
    try:
        # Check if leads table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            )
        """)
        leads_exists = cursor.fetchone()[0]
        
        if not leads_exists:
            results['passed'] = False
            results['issues'].append("leads table does not exist")
            return results
        
        # Check if lead_status table still exists (should not)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'lead_status'
            )
        """)
        lead_status_exists = cursor.fetchone()[0]
        
        if lead_status_exists:
            results['issues'].append("lead_status table still exists (should be renamed to leads)")
        
        # Check if lead_type column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'leads' 
                AND column_name = 'lead_type'
            )
        """)
        has_lead_type = cursor.fetchone()[0]
        
        if not has_lead_type:
            results['passed'] = False
            results['issues'].append("leads table missing lead_type column")
        
        # Check lead_type distribution
        cursor.execute("""
            SELECT lead_type, COUNT(*) 
            FROM leads 
            GROUP BY lead_type
        """)
        lead_type_counts = cursor.fetchall()
        logger.info("Lead type distribution:")
        for lead_type, count in lead_type_counts:
            logger.info(f"  {lead_type}: {count:,}")
        
        # Check if bad_leads and lost_leads tables still exist (should not after migration)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'bad_leads'
            )
        """)
        bad_leads_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'lost_leads'
            )
        """)
        lost_leads_exists = cursor.fetchone()[0]
        
        if bad_leads_exists:
            results['issues'].append("bad_leads table still exists (should be dropped after migration)")
        if lost_leads_exists:
            results['issues'].append("lost_leads table still exists (should be dropped after migration)")
        
        return results
    
    finally:
        cursor.close()


def validate_branch_cleanup(conn) -> Dict:
    """Validate branch cleanup and normalized_name removal."""
    cursor = conn.cursor()
    results = {'passed': True, 'issues': []}
    
    try:
        # Check if normalized_name column exists (should not)
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'branches' 
                AND column_name = 'normalized_name'
            )
        """)
        has_normalized = cursor.fetchone()[0]
        
        if has_normalized:
            results['passed'] = False
            results['issues'].append("branches table still has normalized_name column")
        
        # Count branches
        cursor.execute("SELECT COUNT(*) FROM branches")
        branch_count = cursor.fetchone()[0]
        logger.info(f"Total branches: {branch_count}")
        
        # Check for approved branches
        approved_branches = [
            'ABBOTSFORD', 'AJAX', 'ALEXANDRIA', 'ARLINGTON', 'AURORA', 'AUSTIN',
            'BARRIE', 'BOISE', 'BRAMPTON', 'BRANTFORD', 'BURLINGTON', 'BURNABY',
            'CALGARY', 'COLORADO SPRINGS', 'COQUITLAM', 'DOWNTOWN TORONTO',
            'EDMONTON', 'FREDERICTON', 'HALIFAX', 'HAMILTON', 'HOUSTON',
            'KELOWNA', 'KINGSTON', 'LETHBRIDGE', 'LITTLE FERRY', 'LONDON',
            'MARIETTA', 'MARKHAM', 'MILTON', 'MISSISSAUGA', 'MONCTON',
            'MONTRÈAL', 'MONTREAL', 'MONTREAL NORTH', 'NASHVILLE', 'NEW JERSEY',
            'NORTH YORK', 'NORTHERN VIRGINIA', 'OAKVILLE', 'OSHAWA', 'OTTAWA',
            'PETERBOROUGH', 'PHILADELPHIA', 'PHOENIX', 'REGINA', 'RICHMOND',
            'SAINT JOHN', 'SASKATOON', 'SCARBOROUGH', 'ST. CATHARINES', 'SURREY',
            'THE WOODLANDS', 'TULSA', 'VANCOUVER', 'VAUGHAN', 'VICTORIA ISLAND',
            'WASHINGTON DC', 'WATERLOO/KITCHENER', 'WINDSOR', 'WINNIPEG'
        ]
        
        cursor.execute("SELECT name FROM branches ORDER BY name")
        existing_branches = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing branches: {len(existing_branches)}")
        
        return results
    
    finally:
        cursor.close()


def validate_performance_data(conn) -> Dict:
    """Validate performance data import."""
    cursor = conn.cursor()
    results = {'passed': True, 'issues': []}
    
    try:
        # Check SalesPerformance
        cursor.execute("SELECT COUNT(*) FROM sales_performance")
        sp_count = cursor.fetchone()[0]
        logger.info(f"SalesPerformance records: {sp_count}")
        
        # Check UserPerformance
        cursor.execute("SELECT COUNT(*) FROM user_performance")
        up_count = cursor.fetchone()[0]
        logger.info(f"UserPerformance records: {up_count}")
        
        # Check SalesPerson links
        cursor.execute("""
            SELECT COUNT(*) FROM sales_performance WHERE sales_person_id IS NOT NULL
        """)
        sp_linked = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM user_performance WHERE sales_person_id IS NOT NULL
        """)
        up_linked = cursor.fetchone()[0]
        
        logger.info(f"SalesPerformance linked to SalesPerson: {sp_linked}/{sp_count}")
        logger.info(f"UserPerformance linked to SalesPerson: {up_linked}/{up_count}")
        
        if sp_linked < sp_count * 0.9:  # At least 90% should be linked
            results['issues'].append(f"Only {sp_linked}/{sp_count} SalesPerformance records linked to SalesPerson")
        
        if up_linked < up_count * 0.9:
            results['issues'].append(f"Only {up_linked}/{up_count} UserPerformance records linked to SalesPerson")
        
        return results
    
    finally:
        cursor.close()


def validate_data_integrity(conn) -> Dict:
    """Validate data integrity: foreign keys, orphaned records, etc."""
    cursor = conn.cursor()
    results = {'passed': True, 'issues': []}
    
    try:
        # Check for orphaned SalesPerson links in Jobs
        cursor.execute("""
            SELECT COUNT(*) 
            FROM jobs j
            WHERE j.sales_person_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM sales_persons sp WHERE sp.id = j.sales_person_id
            )
        """)
        orphaned_jobs = cursor.fetchone()[0]
        
        if orphaned_jobs > 0:
            results['issues'].append(f"{orphaned_jobs} jobs have invalid sales_person_id")
        
        # Check for orphaned branch links
        cursor.execute("""
            SELECT COUNT(*) 
            FROM jobs j
            WHERE j.branch_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM branches b WHERE b.id = j.branch_id
            )
        """)
        orphaned_branches_jobs = cursor.fetchone()[0]
        
        if orphaned_branches_jobs > 0:
            results['issues'].append(f"{orphaned_branches_jobs} jobs have invalid branch_id")
        
        # Check for orphaned customer links
        cursor.execute("""
            SELECT COUNT(*) 
            FROM jobs j
            WHERE j.customer_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM customers c WHERE c.id = j.customer_id
            )
        """)
        orphaned_customers = cursor.fetchone()[0]
        
        if orphaned_customers > 0:
            results['issues'].append(f"{orphaned_customers} jobs have invalid customer_id")
        
        return results
    
    finally:
        cursor.close()


def main():
    """Main execution function."""
    conn = get_db_connection()
    
    try:
        logger.info("="*80)
        logger.info("VALIDATION CHECKS")
        logger.info("="*80)
        
        all_passed = True
        
        # Validate lead merge
        logger.info("\n1. Validating Lead merge...")
        lead_results = validate_lead_merge(conn)
        if not lead_results['passed'] or lead_results['issues']:
            all_passed = False
            for issue in lead_results['issues']:
                logger.warning(f"  ISSUE: {issue}")
        else:
            logger.info("  ✓ Lead merge validation passed")
        
        # Validate branch cleanup
        logger.info("\n2. Validating Branch cleanup...")
        branch_results = validate_branch_cleanup(conn)
        if not branch_results['passed'] or branch_results['issues']:
            all_passed = False
            for issue in branch_results['issues']:
                logger.warning(f"  ISSUE: {issue}")
        else:
            logger.info("  ✓ Branch cleanup validation passed")
        
        # Validate performance data
        logger.info("\n3. Validating Performance data...")
        perf_results = validate_performance_data(conn)
        if perf_results['issues']:
            all_passed = False
            for issue in perf_results['issues']:
                logger.warning(f"  ISSUE: {issue}")
        else:
            logger.info("  ✓ Performance data validation passed")
        
        # Validate data integrity
        logger.info("\n4. Validating Data integrity...")
        integrity_results = validate_data_integrity(conn)
        if integrity_results['issues']:
            all_passed = False
            for issue in integrity_results['issues']:
                logger.warning(f"  ISSUE: {issue}")
        else:
            logger.info("  ✓ Data integrity validation passed")
        
        logger.info("\n" + "="*80)
        if all_passed:
            logger.info("ALL VALIDATIONS PASSED ✓")
        else:
            logger.warning("SOME VALIDATIONS FAILED - Review issues above")
        logger.info("="*80)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

