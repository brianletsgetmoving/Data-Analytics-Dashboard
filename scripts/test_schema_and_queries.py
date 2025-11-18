#!/usr/bin/env python3
"""
Comprehensive test suite for schema changes and SQL queries.
Tests migrations, validates schema, and runs all SQL queries.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time
import logging
import subprocess
import psycopg2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing import get_db_connection
from src.utils.progress_monitor import ProgressMonitor, log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import time module if not already imported
import time


def check_database_connection():
    """Check if database is accessible."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        log_success(f"Database connection successful: {version.split(',')[0]}")
        return True
    except Exception as e:
        log_error(f"Database connection failed: {e}")
        return False


def check_docker_running():
    """Check if Docker container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres_data_analytics", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "postgres_data_analytics" in result.stdout:
            log_success("PostgreSQL container is running")
            return True
        else:
            log_step("Docker", "Container check skipped (Docker not available or container not running)")
            return True  # Don't fail if Docker check fails
    except Exception as e:
        log_step("Docker", f"Container check skipped: {e}")
        return True  # Don't fail if Docker check fails


def test_schema_tables(conn):
    """Test that all expected tables exist."""
    log_step("Schema Validation", "Checking table existence")
    
    expected_tables = [
        'customers',
        'jobs',
        'bad_leads',
        'booked_opportunities',
        'lead_status',
        'lost_leads',
        'user_performance',
        'sales_performance',
        'customer_deduplication_logs',
        'sales_persons'  # New table
    ]
    
    cursor = conn.cursor()
    cursor.execute("""
        select table_name
        from information_schema.tables
        where table_schema = 'public'
        and table_type = 'BASE TABLE'
        order by table_name;
    """)
    
    existing_tables = {row[0] for row in cursor.fetchall()}
    cursor.close()
    
    missing_tables = []
    for table in expected_tables:
        if table not in existing_tables:
            missing_tables.append(table)
            log_error(f"Missing table: {table}")
        else:
            log_success(f"Table exists: {table}")
    
    return len(missing_tables) == 0


def test_schema_columns(conn):
    """Test that all expected columns exist in modified tables."""
    log_step("Schema Validation", "Checking column existence")
    
    expected_columns = {
        'jobs': ['sales_person_id'],
        'booked_opportunities': ['sales_person_id'],
        'lead_status': ['booked_opportunity_id', 'sales_person_id'],
        'lost_leads': ['booked_opportunity_id'],
        'user_performance': ['sales_person_id'],
        'sales_performance': ['sales_person_id'],
        'sales_persons': ['id', 'name', 'normalized_name']
    }
    
    cursor = conn.cursor()
    all_passed = True
    
    for table, columns in expected_columns.items():
        cursor.execute("""
            select column_name
            from information_schema.columns
            where table_schema = 'public'
            and table_name = %s;
        """, (table,))
        
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        for column in columns:
            if column not in existing_columns:
                log_error(f"Missing column: {table}.{column}")
                all_passed = False
            else:
                log_success(f"Column exists: {table}.{column}")
    
    cursor.close()
    return all_passed


def test_foreign_keys(conn):
    """Test that foreign key constraints exist."""
    log_step("Schema Validation", "Checking foreign key constraints")
    
    expected_fks = [
        ('lead_status', 'booked_opportunity_id', 'booked_opportunities', 'id'),
        ('lost_leads', 'booked_opportunity_id', 'booked_opportunities', 'id'),
        ('jobs', 'sales_person_id', 'sales_persons', 'id'),
        ('booked_opportunities', 'sales_person_id', 'sales_persons', 'id'),
        ('lead_status', 'sales_person_id', 'sales_persons', 'id'),
        ('user_performance', 'sales_person_id', 'sales_persons', 'id'),
        ('sales_performance', 'sales_person_id', 'sales_persons', 'id'),
    ]
    
    cursor = conn.cursor()
    cursor.execute("""
        select
            tc.table_name,
            kcu.column_name,
            ccu.table_name as foreign_table_name,
            ccu.column_name as foreign_column_name
        from information_schema.table_constraints as tc
        join information_schema.key_column_usage as kcu
            on tc.constraint_name = kcu.constraint_name
            and tc.table_schema = kcu.table_schema
        join information_schema.constraint_column_usage as ccu
            on ccu.constraint_name = tc.constraint_name
            and ccu.table_schema = tc.table_schema
        where tc.constraint_type = 'FOREIGN KEY'
        and tc.table_schema = 'public';
    """)
    
    existing_fks = {
        (row[0], row[1], row[2], row[3])
        for row in cursor.fetchall()
    }
    
    all_passed = True
    for fk in expected_fks:
        if fk not in existing_fks:
            log_error(f"Missing foreign key: {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
            all_passed = False
        else:
            log_success(f"Foreign key exists: {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
    
    cursor.close()
    return all_passed


def test_indexes(conn):
    """Test that indexes exist on foreign key columns."""
    log_step("Schema Validation", "Checking indexes")
    
    expected_indexes = [
        ('jobs', 'sales_person_id'),
        ('booked_opportunities', 'sales_person_id'),
        ('lead_status', 'booked_opportunity_id'),
        ('lead_status', 'sales_person_id'),
        ('lost_leads', 'booked_opportunity_id'),
        ('user_performance', 'sales_person_id'),
        ('sales_performance', 'sales_person_id'),
        ('sales_persons', 'normalized_name'),
    ]
    
    cursor = conn.cursor()
    cursor.execute("""
        select
            tablename,
            indexname,
            indexdef
        from pg_indexes
        where schemaname = 'public';
    """)
    
    # Extract column names from index definitions
    existing_indexes = set()
    for row in cursor.fetchall():
        tablename, indexname, indexdef = row
        # Parse index definition to find column names
        if 'sales_person_id' in indexdef:
            existing_indexes.add((tablename, 'sales_person_id'))
        if 'booked_opportunity_id' in indexdef:
            existing_indexes.add((tablename, 'booked_opportunity_id'))
        if 'normalized_name' in indexdef:
            existing_indexes.add((tablename, 'normalized_name'))
    
    all_passed = True
    for idx in expected_indexes:
        if idx not in existing_indexes:
            log_error(f"Missing index: {idx[0]}.{idx[1]}")
            all_passed = False
        else:
            log_success(f"Index exists: {idx[0]}.{idx[1]}")
    
    cursor.close()
    return all_passed


def test_data_integrity(conn):
    """Test data integrity after schema changes."""
    log_step("Data Integrity", "Validating data relationships")
    
    cursor = conn.cursor()
    issues = []
    
    # Test 1: Check quote_number links between lead_status and booked_opportunities
    cursor.execute("""
        select count(*) as total,
               count(ls.booked_opportunity_id) as linked
        from lead_status ls
        left join booked_opportunities bo on ls.quote_number = bo.quote_number;
    """)
    row = cursor.fetchone()
    if row[0] > 0:
        link_rate = (row[1] / row[0]) * 100 if row[0] > 0 else 0
        log_step("Quote Number Links", f"{row[1]}/{row[0]} lead_status records linked ({link_rate:.1f}%)")
    
    # Test 2: Check sales_person links
    cursor.execute("""
        select count(*) as total,
               count(sp.id) as linked
        from jobs j
        left join sales_persons sp on j.sales_person_id = sp.id
        where j.sales_person_name is not null;
    """)
    row = cursor.fetchone()
    if row[0] > 0:
        link_rate = (row[1] / row[0]) * 100 if row[0] > 0 else 0
        log_step("Sales Person Links", f"{row[1]}/{row[0]} jobs linked to sales_persons ({link_rate:.1f}%)")
    
    # Test 3: Check for orphaned foreign keys
    cursor.execute("""
        select count(*) 
        from lead_status ls
        where ls.booked_opportunity_id is not null
        and not exists (
            select 1 from booked_opportunities bo 
            where bo.id = ls.booked_opportunity_id
        );
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues.append(f"Found {orphaned} orphaned lead_status.booked_opportunity_id references")
        log_error(f"Data integrity issue: {orphaned} orphaned references")
    else:
        log_success("No orphaned foreign key references found")
    
    cursor.close()
    return len(issues) == 0


def test_new_queries(conn):
    """Test all new relationship queries."""
    log_step("Query Testing", "Testing new relationship queries")
    
    new_queries = [
        'customer_relationship_summary.sql',
        'customer_lead_journey.sql',
        'customer_bad_lead_analysis.sql',
        'quote_number_linkage.sql',
        'lead_status_to_customer.sql',
        'lost_lead_to_customer.sql',
        'sales_person_cross_module.sql',
        'user_performance_cross_module.sql',
        'sales_person_customer_analysis.sql',
        'module_relationship_matrix.sql',
        'customer_complete_profile.sql',
        'lead_to_customer_traceability.sql',
    ]
    
    queries_dir = Path("sql/queries")
    cursor = conn.cursor()
    results = []
    
    for query_file in new_queries:
        query_path = queries_dir / query_file
        if not query_path.exists():
            log_error(f"Query file not found: {query_file}")
            results.append({'file': query_file, 'status': 'error', 'error': 'File not found'})
            continue
        
        try:
            query_text = query_path.read_text()
            start_time = time.time()
            cursor.execute(query_text)
            execution_time = (time.time() - start_time) * 1000
            
            # Try to fetch results
            try:
                rows = cursor.fetchall()
                row_count = len(rows)
                log_success(f"{query_file}: {row_count} rows in {execution_time:.0f}ms")
                results.append({
                    'file': query_file,
                    'status': 'success',
                    'row_count': row_count,
                    'execution_time_ms': execution_time
                })
            except psycopg2.ProgrammingError:
                # No results to fetch
                log_success(f"{query_file}: Executed successfully (no result set)")
                results.append({
                    'file': query_file,
                    'status': 'success',
                    'row_count': 0,
                    'execution_time_ms': execution_time
                })
            
            conn.rollback()  # Rollback to avoid any side effects
            
        except Exception as e:
            log_error(f"{query_file}: {str(e)}")
            results.append({
                'file': query_file,
                'status': 'error',
                'error': str(e)
            })
            conn.rollback()
    
    cursor.close()
    
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = sum(1 for r in results if r.get('status') == 'error')
    
    log_step("Query Test Summary", f"{successful} successful, {failed} failed")
    
    return results


def main():
    """Main test function."""
    print("="*80)
    print("SCHEMA AND QUERY VALIDATION TEST SUITE")
    print("="*80)
    print()
    
    # Step 1: Check Docker
    if not check_docker_running():
        return 1
    
    # Step 2: Check database connection
    if not check_database_connection():
        log_error("Cannot proceed without database connection")
        return 1
    
    # Step 3: Connect and test schema
    try:
        conn = get_db_connection()
        
        # Test schema tables
        if not test_schema_tables(conn):
            log_error("Schema table validation failed")
            conn.close()
            return 1
        
        # Test schema columns
        if not test_schema_columns(conn):
            log_error("Schema column validation failed")
            conn.close()
            return 1
        
        # Test foreign keys
        if not test_foreign_keys(conn):
            log_error("Foreign key validation failed")
            conn.close()
            return 1
        
        # Test indexes
        if not test_indexes(conn):
            log_error("Index validation failed")
            conn.close()
            return 1
        
        # Test data integrity
        if not test_data_integrity(conn):
            log_error("Data integrity validation failed")
            conn.close()
            return 1
        
        # Test new queries
        query_results = test_new_queries(conn)
        
        conn.close()
        
        # Print summary
        print()
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        successful_queries = sum(1 for r in query_results if r.get('status') == 'success')
        failed_queries = sum(1 for r in query_results if r.get('status') == 'error')
        
        print(f"Schema Validation: ✅ PASSED")
        print(f"Query Tests: {successful_queries} successful, {failed_queries} failed")
        
        if failed_queries > 0:
            print("\nFailed Queries:")
            for result in query_results:
                if result.get('status') == 'error':
                    print(f"  ❌ {result.get('file')}: {result.get('error', 'Unknown error')}")
        
        print("="*80)
        
        return 0 if failed_queries == 0 else 1
        
    except Exception as e:
        log_error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

