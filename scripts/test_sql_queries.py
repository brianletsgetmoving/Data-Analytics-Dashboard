#!/usr/bin/env python3
"""
SQL Query Testing CLI
Tests all SQL query files against the database and generates comprehensive reports.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import time
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing import QueryTester, get_db_connection, DatabaseConnectionManager
from src.testing.diagnostics import (
    SchemaValidator,
    ErrorAnalyzer,
    DependencyAnalyzer,
    FixRecommender
)
from src.testing.reports import JSONReporter, HTMLReporter, CSVReporter
from src.utils.progress_monitor import ProgressMonitor, log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_database_version(connection):
    """Get PostgreSQL version."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        return version.split(',')[0]  # Just the PostgreSQL version part
    except:
        return "Unknown"


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Test SQL queries against PostgreSQL database',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports/sql_test_results',
        help='Output directory for reports (default: reports/sql_test_results)'
    )
    parser.add_argument(
        '--format',
        type=str,
        default='json,html,csv',
        help='Report formats: json,html,csv (default: json,html,csv)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Query timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--parallel',
        type=int,
        default=1,
        help='Number of parallel queries (default: 1)'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Test specific query file (optional)'
    )
    parser.add_argument(
        '--generate-fixes',
        action='store_true',
        help='Generate SQL fix script'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup
    log_step("SQL Query Testing", "Starting test suite")
    
    queries_dir = Path("sql/queries")
    if not queries_dir.exists():
        log_error(f"Queries directory not found: {queries_dir}")
        return 1
    
    # Get SQL files
    if args.query:
        sql_files = [queries_dir / args.query]
        if not sql_files[0].exists():
            log_error(f"Query file not found: {sql_files[0]}")
            return 1
    else:
        sql_files = sorted(queries_dir.glob("*.sql"))
    
    if len(sql_files) == 0:
        log_error("No SQL files found to test")
        return 1
    
    log_step(f"Found {len(sql_files)} SQL query files")
    
    # Connect to database
    try:
        if args.parallel > 1:
            conn_manager = DatabaseConnectionManager(min_connections=2, max_connections=args.parallel + 2)
            connection = conn_manager.get_connection()
        else:
            connection = get_db_connection()
        
        db_version = get_database_version(connection)
        log_step("Database connection", f"Connected to {db_version}")
    except Exception as e:
        log_error(f"Failed to connect to database: {e}")
        return 1
    
    # Initialize components
    query_tester = QueryTester(connection, timeout_seconds=args.timeout)
    schema_validator = SchemaValidator(connection)
    error_analyzer = ErrorAnalyzer()
    dependency_analyzer = DependencyAnalyzer()
    fix_recommender = FixRecommender()
    
    # Test queries
    results = []
    start_time = time.time()
    
    log_step("Testing queries", f"Executing {len(sql_files)} queries...")
    
    for i, sql_file in enumerate(sql_files, 1):
        logger.info(f"[{i}/{len(sql_files)}] Testing: {sql_file.name}")
        
        try:
            query_text = sql_file.read_text()
            
            if not query_text.strip():
                logger.warning(f"Skipping empty file: {sql_file.name}")
                continue
            
            # Test query with validation
            result = query_tester.test_query_with_validation(
                sql_file,
                query_text,
                schema_validator=schema_validator,
                dependency_analyzer=dependency_analyzer
            )
            
            # Analyze errors
            if result['status'] == 'error':
                error_analysis = error_analyzer.analyze(
                    result.get('error', ''),
                    result.get('error_code')
                )
                result['error_analysis'] = error_analysis
                
                # Get recommendations
                schema_validation = result.get('schema_validation')
                dependencies = result.get('dependencies')
                recommendations = fix_recommender.recommend_fixes(
                    error_analysis,
                    schema_validation,
                    dependencies
                )
                result['recommendations'] = recommendations
            
            results.append(result)
            
            if result['status'] == 'success':
                logger.info(f"  ✅ Success: {result['row_count']} rows in {result['execution_time_ms']}ms")
            else:
                logger.error(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"  ❌ Error testing {sql_file.name}: {e}")
            results.append({
                'file': sql_file.name,
                'status': 'error',
                'error': f'File read error: {str(e)}',
                'diagnostics': ['Could not read or execute SQL file']
            })
    
    end_time = time.time()
    test_duration = end_time - start_time
    
    # Close connection
    if args.parallel > 1:
        conn_manager.return_connection(connection)
        conn_manager.close_all()
    else:
        connection.close()
    
    # Generate reports
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata = {
        'database_version': db_version,
        'test_duration_seconds': test_duration,
        'total_queries': len(sql_files)
    }
    
    formats = [f.strip() for f in args.format.split(',')]
    
    if 'json' in formats:
        log_step("Generating JSON report")
        json_reporter = JSONReporter()
        json_path = output_dir / f"sql_test_report_{timestamp}.json"
        json_reporter.generate(results, metadata, json_path)
        log_success(f"JSON report: {json_path}")
    
    if 'html' in formats:
        log_step("Generating HTML report")
        html_reporter = HTMLReporter()
        html_path = output_dir / f"sql_test_report_{timestamp}.html"
        html_reporter.generate(results, metadata, html_path)
        log_success(f"HTML report: {html_path}")
    
    if 'csv' in formats:
        log_step("Generating CSV report")
        csv_reporter = CSVReporter()
        csv_path = output_dir / f"sql_test_report_{timestamp}.csv"
        csv_reporter.generate(results, metadata, csv_path)
        log_success(f"CSV report: {csv_path}")
    
    # Generate fix script if requested
    if args.generate_fixes:
        log_step("Generating fix script")
        fix_script_path = output_dir / f"fixes_{timestamp}.sql"
        generate_fix_script(results, fix_script_path)
        log_success(f"Fix script: {fix_script_path}")
    
    # Print summary
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = sum(1 for r in results if r.get('status') == 'error')
    success_rate = round(successful / len(results) * 100, 2) if results else 0
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Queries: {len(results)}")
    print(f"Successful: {successful} ({success_rate}%)")
    print(f"Failed: {failed}")
    print(f"Duration: {test_duration:.2f} seconds")
    print("="*80)
    
    if failed > 0:
        print("\nFAILED QUERIES:")
        for result in results:
            if result.get('status') == 'error':
                print(f"\n❌ {result.get('file', 'unknown')}")
                print(f"   Error: {result.get('error', 'Unknown')}")
                if 'diagnostics' in result:
                    for diag in result['diagnostics']:
                        print(f"   - {diag}")
    
    return 0 if failed == 0 else 1


def generate_fix_script(results: list, output_path: Path):
    """Generate SQL script with fixes."""
    fixes = []
    
    for result in results:
        if 'recommendations' in result:
            for rec in result['recommendations']:
                if rec.get('sql'):
                    fixes.append(f"-- {rec.get('issue', 'Unknown issue')}")
                    fixes.append(f"-- Query: {result.get('file', 'unknown')}")
                    fixes.append(rec['sql'])
                    fixes.append("")
    
    if fixes:
        with open(output_path, 'w') as f:
            f.write("-- SQL Fix Script\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write("-- Review and execute fixes as needed\n\n")
            f.write("\n".join(fixes))
    else:
        with open(output_path, 'w') as f:
            f.write("-- No fixes needed\n")


if __name__ == '__main__':
    sys.exit(main())

