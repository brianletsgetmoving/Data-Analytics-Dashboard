#!/usr/bin/env python3
"""
Comprehensive SQL Query Testing Script
Tests all SQL queries recursively including subdirectories.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time
import logging
import psycopg2
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.testing.database_connection import get_db_connection
except ImportError:
    # Fallback if src module not available
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_sql_query(conn, query_path: Path, query_text: str, timeout: int = 30) -> Dict[str, Any]:
    """Test a single SQL query."""
    result = {
        'file': str(query_path.relative_to(Path('sql/queries'))),
        'status': 'unknown',
        'error': None,
        'row_count': 0,
        'execution_time_ms': 0,
        'columns': []
    }
    
    try:
        cursor = conn.cursor()
        start_time = time.time()
        
        # Execute query
        cursor.execute(query_text)
        
        # Fetch results if it's a SELECT query
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result['columns'] = columns
            result['row_count'] = len(rows)
        else:
            # For non-SELECT queries, commit the transaction
            conn.commit()
            result['row_count'] = cursor.rowcount
        
        execution_time = (time.time() - start_time) * 1000
        result['execution_time_ms'] = round(execution_time, 2)
        result['status'] = 'success'
        
        cursor.close()
        
    except psycopg2.Error as e:
        result['status'] = 'error'
        result['error'] = str(e)
        result['error_code'] = e.pgcode
        conn.rollback()
        cursor.close()
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        conn.rollback()
        if 'cursor' in locals():
            cursor.close()
    
    return result


def find_all_sql_files(queries_dir: Path) -> List[Path]:
    """Find all SQL files recursively."""
    sql_files = sorted(queries_dir.rglob("*.sql"))
    return sql_files


def main():
    """Main test function."""
    print("="*80)
    print("COMPREHENSIVE SQL QUERY TEST SUITE")
    print("="*80)
    print()
    
    queries_dir = Path("sql/queries")
    if not queries_dir.exists():
        print(f"ERROR: Queries directory not found: {queries_dir}")
        return 1
    
    # Find all SQL files recursively
    sql_files = find_all_sql_files(queries_dir)
    
    if len(sql_files) == 0:
        print("ERROR: No SQL files found")
        return 1
    
    print(f"Found {len(sql_files)} SQL query files")
    print()
    
    # Connect to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        print(f"✓ Database connected: {version.split(',')[0]}")
        print()
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        return 1
    
    # Test all queries
    results = []
    start_time = time.time()
    
    print("Testing queries...")
    print("-" * 80)
    
    for i, sql_file in enumerate(sql_files, 1):
        relative_path = sql_file.relative_to(queries_dir)
        print(f"[{i}/{len(sql_files)}] Testing: {relative_path}")
        
        try:
            query_text = sql_file.read_text()
            
            if not query_text.strip():
                print(f"  ⚠ Skipping empty file")
                results.append({
                    'file': str(relative_path),
                    'status': 'skipped',
                    'error': 'Empty file'
                })
                continue
            
            result = test_sql_query(conn, sql_file, query_text, timeout=30)
            results.append(result)
            
            if result['status'] == 'success':
                print(f"  ✓ Success: {result['row_count']} rows in {result['execution_time_ms']}ms")
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')[:100]}")
        
        except Exception as e:
            print(f"  ✗ Error reading file: {e}")
            results.append({
                'file': str(relative_path),
                'status': 'error',
                'error': f'File read error: {str(e)}'
            })
    
    conn.close()
    
    # Print summary
    end_time = time.time()
    test_duration = end_time - start_time
    
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = sum(1 for r in results if r.get('status') == 'error')
    skipped = sum(1 for r in results if r.get('status') == 'skipped')
    success_rate = round(successful / (successful + failed) * 100, 2) if (successful + failed) > 0 else 0
    
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Queries: {len(results)}")
    print(f"Successful: {successful} ({success_rate}%)")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Duration: {test_duration:.2f} seconds")
    print("="*80)
    
    if failed > 0:
        print("\nFAILED QUERIES:")
        print("-" * 80)
        for result in results:
            if result.get('status') == 'error':
                print(f"\n✗ {result.get('file', 'unknown')}")
                error_msg = result.get('error', 'Unknown error')
                # Truncate long error messages
                if len(error_msg) > 200:
                    error_msg = error_msg[:200] + "..."
                print(f"  Error: {error_msg}")
        
        return 1
    
    print("\n✓ All queries passed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())

