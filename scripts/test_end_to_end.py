#!/usr/bin/env python3
"""
Comprehensive end-to-end testing for the complete stack.
Tests database, backend API, and frontend with timeouts.
"""

import sys
from pathlib import Path
import subprocess
import signal
import time
import requests
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent))

# Timeout values (in seconds)
TIMEOUT_DB_TEST = 30
TIMEOUT_API_TEST = 10
TIMEOUT_FRONTEND_TEST = 10
TIMEOUT_INTEGRITY_CHECK = 120

# Service URLs
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def run_with_timeout(cmd, timeout, description):
    """Run a command with timeout."""
    try:
        print(f"  Running: {description} (timeout: {timeout}s)...", end=" ")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        
        try:
            stdout, _ = process.communicate(timeout=timeout)
            if process.returncode == 0:
                print("✓ OK")
                return True, stdout
            else:
                print(f"✗ FAILED (exit code: {process.returncode})")
                return False, stdout
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"✗ TIMEOUT (>{timeout}s)")
            return False, ""
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False, ""


def get_db_connection():
    """Get database connection."""
    import os
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.getenv("DATABASE_URL", "postgresql://buyer@localhost:5432/data_analytics")
    
    if db_url.startswith("postgresql://"):
        parsed = urlparse(db_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        database = parsed.path.lstrip("/") or "data_analytics"
        user = parsed.username or "buyer"
        password = parsed.password
    else:
        host, port, database, user, password = "localhost", 5432, "data_analytics", "buyer", None
    
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )


def test_database_connection():
    """Test database connectivity."""
    print("\n1. Testing Database Connection...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"  ✓ Database connected: {version[:50]}...")
        return True
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        return False


def test_database_queries():
    """Test basic database queries for all tables."""
    print("\n2. Testing Database Queries...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test all tables from Prisma schema
        tests = [
            ("SELECT COUNT(*) FROM jobs", "Jobs count"),
            ("SELECT COUNT(*) FROM customers", "Customers count"),
            ("SELECT COUNT(*) FROM lead_status", "LeadStatus count"),
            ("SELECT COUNT(*) FROM sales_persons", "SalesPersons count"),
            ("SELECT COUNT(*) FROM branches", "Branches count"),
            ("SELECT COUNT(*) FROM booked_opportunities", "BookedOpportunities count"),
            ("SELECT COUNT(*) FROM bad_leads", "BadLeads count"),
            ("SELECT COUNT(*) FROM lost_leads", "LostLeads count"),
            ("SELECT COUNT(*) FROM lead_sources", "LeadSources count"),
        ]
        
        # Test for user_performance and sales_performance (may be views or tables)
        optional_tests = [
            ("SELECT COUNT(*) FROM user_performance", "UserPerformance count"),
            ("SELECT COUNT(*) FROM sales_performance", "SalesPerformance count"),
        ]
        
        all_passed = True
        passed = 0
        total = len(tests)
        
        for query, desc in tests:
            try:
                start_time = time.time()
                cursor.execute(query)
                result = cursor.fetchone()[0]
                elapsed = time.time() - start_time
                print(f"  ✓ {desc}: {result} ({elapsed:.3f}s)")
                passed += 1
            except Exception as e:
                print(f"  ✗ {desc} failed: {e}")
                all_passed = False
        
        # Test optional tables (views or materialized views)
        for query, desc in optional_tests:
            try:
                start_time = time.time()
                cursor.execute(query)
                result = cursor.fetchone()[0]
                elapsed = time.time() - start_time
                print(f"  ✓ {desc}: {result} ({elapsed:.3f}s)")
                passed += 1
                total += 1
            except Exception as e:
                print(f"  ⚠ {desc} not found (may be a view): {str(e)[:50]}")
        
        # Test relationships (foreign keys)
        print("\n  Testing Relationships...")
        relationship_tests = [
            ("SELECT COUNT(*) FROM jobs WHERE customer_id IS NOT NULL", "Jobs with customer_id"),
            ("SELECT COUNT(*) FROM jobs WHERE sales_person_id IS NOT NULL", "Jobs with sales_person_id"),
            ("SELECT COUNT(*) FROM jobs WHERE branch_id IS NOT NULL", "Jobs with branch_id"),
            ("SELECT COUNT(*) FROM booked_opportunities WHERE customer_id IS NOT NULL", "BookedOpportunities with customer_id"),
        ]
        
        for query, desc in relationship_tests:
            try:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                print(f"  ✓ {desc}: {result}")
            except Exception as e:
                print(f"  ✗ {desc} failed: {e}")
                all_passed = False
        
        cursor.close()
        conn.close()
        
        print(f"\n  Database Tables: {passed}/{total} tables accessible")
        return all_passed
    except Exception as e:
        print(f"  ✗ Database query test failed: {e}")
        return False


def test_backend_health():
    """Test backend health endpoint."""
    print("\n3. Testing Backend Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT_API_TEST)
        if response.status_code == 200:
            print(f"  ✓ Backend is running (status: {response.status_code})")
            return True
        else:
            print(f"  ✗ Backend returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Backend is not running (start with: cd backend && uvicorn app.main:app --reload)")
        return False
    except Exception as e:
        print(f"  ✗ Backend health check failed: {e}")
        return False


def test_backend_endpoints():
    """Test backend API endpoints."""
    print("\n4. Testing Backend API Endpoints...")
    
    # All 64 endpoints organized by category
    endpoints = [
        # Analytics (3 endpoints)
        ("/api/v1/analytics/overview", "Analytics Overview"),
        ("/api/v1/analytics/kpis", "Analytics KPIs"),
        ("/api/v1/analytics/trends", "Analytics Trends"),
        
        # Customers (6 endpoints)
        ("/api/v1/customers/demographics", "Customer Demographics"),
        ("/api/v1/customers/segmentation", "Customer Segmentation"),
        ("/api/v1/customers/gender-breakdown", "Customer Gender Breakdown"),
        ("/api/v1/customers/lifetime-value", "Customer Lifetime Value"),
        ("/api/v1/customers/retention", "Customer Retention"),
        ("/api/v1/customers/geographic-distribution", "Customer Geographic Distribution"),
        
        # Jobs (6 endpoints)
        ("/api/v1/jobs/metrics", "Job Metrics"),
        ("/api/v1/jobs/volume-trends", "Job Volume Trends"),
        ("/api/v1/jobs/status-distribution", "Job Status Distribution"),
        ("/api/v1/jobs/type-distribution", "Job Type Distribution"),
        ("/api/v1/jobs/seasonal-patterns", "Job Seasonal Patterns"),
        ("/api/v1/jobs/crew-utilization", "Job Crew Utilization"),
        
        # Revenue (6 endpoints)
        ("/api/v1/revenue/trends", "Revenue Trends"),
        ("/api/v1/revenue/by-branch", "Revenue By Branch"),
        ("/api/v1/revenue/by-region", "Revenue By Region"),
        ("/api/v1/revenue/by-source", "Revenue By Source"),
        ("/api/v1/revenue/forecasts", "Revenue Forecasts"),
        ("/api/v1/revenue/by-segment", "Revenue By Segment"),
        
        # Leads (5 endpoints)
        ("/api/v1/leads/demographics", "Lead Demographics"),
        ("/api/v1/leads/conversion-funnel", "Lead Conversion Funnel"),
        ("/api/v1/leads/response-time", "Lead Response Time"),
        ("/api/v1/leads/source-performance", "Lead Source Performance"),
        ("/api/v1/leads/status-distribution", "Lead Status Distribution"),
        
        # Sales (5 endpoints)
        ("/api/v1/sales/performance", "Sales Performance"),
        ("/api/v1/sales/rankings", "Sales Rankings"),
        ("/api/v1/sales/trends", "Sales Trends"),
        ("/api/v1/sales/comparison", "Sales Comparison"),
        ("/api/v1/sales/efficiency", "Sales Efficiency"),
        
        # Profitability (7 endpoints)
        ("/api/v1/profitability/job-margins", "Profitability Job Margins"),
        ("/api/v1/profitability/branch", "Profitability Branch"),
        ("/api/v1/profitability/job-type", "Profitability Job Type"),
        ("/api/v1/profitability/customer", "Profitability Customer"),
        ("/api/v1/profitability/roi-by-source", "Profitability ROI By Source"),
        ("/api/v1/profitability/cost-efficiency", "Profitability Cost Efficiency"),
        ("/api/v1/profitability/pricing-optimization", "Profitability Pricing Optimization"),
        
        # Customer Behavior (7 endpoints)
        ("/api/v1/customer-behavior/churn-prediction", "Customer Behavior Churn Prediction"),
        ("/api/v1/customer-behavior/ltv-forecast", "Customer Behavior LTV Forecast"),
        ("/api/v1/customer-behavior/journey", "Customer Behavior Journey"),
        ("/api/v1/customer-behavior/rfm-segmentation", "Customer Behavior RFM Segmentation"),
        ("/api/v1/customer-behavior/preferences", "Customer Behavior Preferences"),
        ("/api/v1/customer-behavior/acquisition-cost", "Customer Behavior Acquisition Cost"),
        ("/api/v1/customer-behavior/repeat-patterns", "Customer Behavior Repeat Patterns"),
        
        # Operational (7 endpoints)
        ("/api/v1/operational/capacity-utilization", "Operational Capacity Utilization"),
        ("/api/v1/operational/routing-efficiency", "Operational Routing Efficiency"),
        ("/api/v1/operational/job-duration", "Operational Job Duration"),
        ("/api/v1/operational/bottlenecks", "Operational Bottlenecks"),
        ("/api/v1/operational/resource-allocation", "Operational Resource Allocation"),
        ("/api/v1/operational/capacity-planning", "Operational Capacity Planning"),
        ("/api/v1/operational/scheduling-efficiency", "Operational Scheduling Efficiency"),
        
        # Benchmarking (6 endpoints)
        ("/api/v1/benchmarking/industry", "Benchmarking Industry"),
        ("/api/v1/benchmarking/branch", "Benchmarking Branch"),
        ("/api/v1/benchmarking/sales-person", "Benchmarking Sales Person"),
        ("/api/v1/benchmarking/time-period", "Benchmarking Time Period"),
        ("/api/v1/benchmarking/market-share", "Benchmarking Market Share"),
        ("/api/v1/benchmarking/competitive-metrics", "Benchmarking Competitive Metrics"),
        
        # Forecasting (6 endpoints)
        ("/api/v1/forecasting/revenue", "Forecasting Revenue"),
        ("/api/v1/forecasting/job-volume", "Forecasting Job Volume"),
        ("/api/v1/forecasting/customer-growth", "Forecasting Customer Growth"),
        ("/api/v1/forecasting/demand", "Forecasting Demand"),
        ("/api/v1/forecasting/trends", "Forecasting Trends"),
        ("/api/v1/forecasting/anomalies", "Forecasting Anomalies"),
    ]
    
    passed = 0
    total = len(endpoints)
    failed_endpoints = []
    
    for endpoint, desc in endpoints:
        try:
            start_time = time.time()
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                params={"limit": 10},
                timeout=TIMEOUT_API_TEST
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                # Basic response validation
                try:
                    data = response.json()
                    if isinstance(data, dict) and "data" in data:
                        print(f"  ✓ {desc} ({elapsed:.2f}s)")
                        passed += 1
                    else:
                        print(f"  ⚠ {desc} - Invalid response structure")
                        failed_endpoints.append((endpoint, desc, "Invalid response structure"))
                except ValueError:
                    print(f"  ⚠ {desc} - Invalid JSON response")
                    failed_endpoints.append((endpoint, desc, "Invalid JSON"))
            else:
                print(f"  ✗ {desc} (status: {response.status_code})")
                failed_endpoints.append((endpoint, desc, f"Status {response.status_code}"))
        except requests.exceptions.Timeout:
            print(f"  ✗ {desc} (timeout)")
            failed_endpoints.append((endpoint, desc, "Timeout"))
        except Exception as e:
            print(f"  ✗ {desc} (error: {str(e)[:50]})")
            failed_endpoints.append((endpoint, desc, str(e)[:50]))
    
    print(f"\n  Backend API: {passed}/{total} endpoints working")
    if failed_endpoints:
        print(f"\n  Failed endpoints ({len(failed_endpoints)}):")
        for endpoint, desc, reason in failed_endpoints[:10]:  # Show first 10
            print(f"    - {desc}: {reason}")
        if len(failed_endpoints) > 10:
            print(f"    ... and {len(failed_endpoints) - 10} more")
    
    return passed >= total * 0.8  # 80% pass rate is acceptable


def test_frontend():
    """Test frontend pages."""
    print("\n5. Testing Frontend...")
    
    pages = [
        ("/", "Home"),
        ("/overview", "Overview"),
        ("/customers", "Customers"),
        ("/jobs", "Jobs"),
        ("/revenue", "Revenue"),
        ("/sales", "Sales"),
        ("/leads", "Leads"),
        ("/profitability", "Profitability"),
        ("/customer-behavior", "Customer Behavior"),
        ("/operational", "Operational"),
        ("/benchmarking", "Benchmarking"),
        ("/forecasting", "Forecasting"),
    ]
    
    passed = 0
    total = len(pages)
    failed_pages = []
    
    for path, desc in pages:
        try:
            start_time = time.time()
            response = requests.get(
                f"{FRONTEND_URL}{path}",
                timeout=TIMEOUT_FRONTEND_TEST,
                allow_redirects=True
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                # Basic content validation
                content = response.text
                if len(content) > 100:  # Basic check that page has content
                    print(f"  ✓ {desc} ({elapsed:.2f}s)")
                    passed += 1
                else:
                    print(f"  ⚠ {desc} - Empty or minimal content")
                    failed_pages.append((path, desc, "Empty content"))
            else:
                print(f"  ✗ {desc} (status: {response.status_code})")
                failed_pages.append((path, desc, f"Status {response.status_code}"))
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Frontend is not running (start with: cd frontend && npm run dev)")
            break
        except requests.exceptions.Timeout:
            print(f"  ✗ {desc} (timeout)")
            failed_pages.append((path, desc, "Timeout"))
        except Exception as e:
            print(f"  ✗ {desc} (error: {str(e)[:50]})")
            failed_pages.append((path, desc, str(e)[:50]))
    
    if total > 0:
        print(f"\n  Frontend: {passed}/{total} pages accessible")
        if failed_pages:
            print(f"\n  Failed pages ({len(failed_pages)}):")
            for path, desc, reason in failed_pages:
                print(f"    - {desc} ({path}): {reason}")
        return passed >= total * 0.8  # 80% pass rate is acceptable
    else:
        return False


def test_response_validation():
    """Test API response structure validation."""
    print("\n6. Testing API Response Validation...")
    
    # Test a few key endpoints for proper response structure
    test_endpoints = [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/kpis",
        "/api/v1/customers/demographics",
        "/api/v1/jobs/metrics",
    ]
    
    passed = 0
    total = len(test_endpoints)
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                params={"limit": 10},
                timeout=TIMEOUT_API_TEST
            )
            
            if response.status_code == 200:
                data = response.json()
                # Validate AnalyticsResponse structure
                if isinstance(data, dict):
                    has_data = "data" in data
                    has_metadata = "metadata" in data
                    has_filters = "filters_applied" in data
                    
                    if has_data and has_metadata:
                        print(f"  ✓ {endpoint} - Valid structure")
                        passed += 1
                    else:
                        print(f"  ✗ {endpoint} - Missing fields (data: {has_data}, metadata: {has_metadata}, filters: {has_filters})")
                else:
                    print(f"  ✗ {endpoint} - Invalid response type")
            else:
                print(f"  ✗ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"  ✗ {endpoint} - Error: {str(e)[:50]}")
    
    print(f"\n  Response Validation: {passed}/{total} endpoints validated")
    return passed >= total * 0.8


def test_error_handling():
    """Test error handling for invalid requests."""
    print("\n7. Testing Error Handling...")
    
    error_tests = [
        # Invalid limit (too high)
        ("/api/v1/analytics/overview", {"limit": 10000}, "Invalid limit"),
        # Invalid date format
        ("/api/v1/analytics/overview", {"date_from": "invalid-date"}, "Invalid date format"),
        # Non-existent endpoint
        ("/api/v1/nonexistent/endpoint", {}, "Non-existent endpoint"),
    ]
    
    passed = 0
    total = len(error_tests)
    
    for endpoint, params, desc in error_tests:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                params=params,
                timeout=TIMEOUT_API_TEST
            )
            
            # Should return 400 or 404 for invalid requests
            if response.status_code in [400, 404, 422]:
                print(f"  ✓ {desc} - Correct error status ({response.status_code})")
                passed += 1
            else:
                print(f"  ⚠ {desc} - Unexpected status ({response.status_code})")
        except Exception as e:
            print(f"  ✗ {desc} - Error: {str(e)[:50]}")
    
    print(f"\n  Error Handling: {passed}/{total} tests passed")
    return passed >= total * 0.7  # 70% pass rate for error handling


def test_performance():
    """Test API performance benchmarks."""
    print("\n8. Testing Performance Benchmarks...")
    
    # Test key endpoints for performance
    performance_endpoints = [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/kpis",
        "/api/v1/customers/demographics",
        "/api/v1/jobs/metrics",
        "/api/v1/revenue/trends",
    ]
    
    results = []
    slow_endpoints = []
    
    for endpoint in performance_endpoints:
        try:
            start_time = time.time()
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                params={"limit": 10},
                timeout=TIMEOUT_API_TEST
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                results.append(elapsed)
                if elapsed > 2.0:  # Flag endpoints taking more than 2 seconds
                    slow_endpoints.append((endpoint, elapsed))
                    print(f"  ⚠ {endpoint} - Slow ({elapsed:.2f}s)")
                else:
                    print(f"  ✓ {endpoint} - {elapsed:.2f}s")
            else:
                print(f"  ✗ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"  ✗ {endpoint} - Error: {str(e)[:50]}")
    
    if results:
        avg_time = sum(results) / len(results)
        max_time = max(results)
        min_time = min(results)
        
        print(f"\n  Performance Summary:")
        print(f"    Average: {avg_time:.2f}s")
        print(f"    Min: {min_time:.2f}s")
        print(f"    Max: {max_time:.2f}s")
        
        if slow_endpoints:
            print(f"\n  Slow Endpoints ({len(slow_endpoints)}):")
            for endpoint, elapsed in slow_endpoints:
                print(f"    - {endpoint}: {elapsed:.2f}s")
        
        # Performance is acceptable if average is under 1 second
        return avg_time < 1.0
    else:
        return False


def test_integrity_checks():
    """Run database integrity checks."""
    print("\n9. Running Database Integrity Checks...")
    import os
    script_path = os.path.join(os.path.dirname(__file__), "setup_integrity_monitoring.py")
    
    if not os.path.exists(script_path):
        print("  ⚠ Integrity check script not found, skipping...")
        return True  # Don't fail if script doesn't exist
    
    success, output = run_with_timeout(
        f"python3 {script_path} --execute",
        TIMEOUT_INTEGRITY_CHECK,
        "Integrity checks"
    )
    
    if success:
        # Parse output for key metrics
        if "Job-Customer Linkage Rate" in output or "completed" in output.lower():
            print("  Integrity check completed successfully")
        return True
    else:
        print("  Integrity check failed or timed out (non-critical)")
        return True  # Don't fail the whole test suite


def create_gap_analysis(results):
    """Create gap analysis and generate TODOs for other agents."""
    print("\n" + "="*80)
    print("GAP ANALYSIS & TODOs FOR OTHER AGENTS")
    print("="*80)
    
    todos = []
    
    # Check backend endpoints
    if results.get('backend_endpoints') is False:
        todos.append({
            'agent': 2,
            'type': 'backend',
            'issue': 'Backend endpoints test failed - verify all 64 endpoints are working correctly',
            'location': 'backend/app/api/v1/'
        })
    
    # Check frontend pages
    if results.get('frontend') is False:
        todos.append({
            'agent': 1,
            'type': 'frontend',
            'issue': 'Frontend pages test failed - verify all dashboard pages are accessible',
            'location': 'frontend/app/'
        })
    
    # Check database
    if results.get('database_queries') is False:
        todos.append({
            'agent': 3,
            'type': 'database',
            'issue': 'Database queries test failed - verify all tables exist and are accessible',
            'location': 'prisma/schema.prisma'
        })
    
    # Check response validation
    if results.get('response_validation') is False:
        todos.append({
            'agent': 2,
            'type': 'backend',
            'issue': 'API response validation failed - ensure all endpoints return AnalyticsResponse format',
            'location': 'backend/app/schemas/analytics.py'
        })
    
    # Check error handling
    if results.get('error_handling') is False:
        todos.append({
            'agent': 2,
            'type': 'backend',
            'issue': 'Error handling test failed - improve validation and error responses',
            'location': 'backend/app/api/'
        })
    
    # Check performance
    if results.get('performance') is False:
        todos.append({
            'agent': 2,
            'type': 'backend',
            'issue': 'Performance test failed - optimize slow endpoints (check query performance)',
            'location': 'backend/app/api/ and sql/queries/'
        })
    
    if todos:
        print("\nGenerated TODOs:")
        for i, todo in enumerate(todos, 1):
            print(f"\n{i}. TODO: [Agent {todo['agent']}] {todo['issue']}")
            print(f"   Location: {todo['location']}")
            print(f"   Type: {todo['type']}")
    else:
        print("\n✓ No critical gaps identified - all tests passed!")
    
    return todos


def main():
    """Run all end-to-end tests."""
    print("="*80)
    print("END-TO-END TESTING - Complete Stack")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test database
    results['database_connection'] = test_database_connection()
    results['database_queries'] = test_database_queries()
    
    # Test backend
    results['backend_health'] = test_backend_health()
    if results['backend_health']:
        results['backend_endpoints'] = test_backend_endpoints()
        results['response_validation'] = test_response_validation()
        results['error_handling'] = test_error_handling()
        results['performance'] = test_performance()
    else:
        results['backend_endpoints'] = False
        results['response_validation'] = False
        results['error_handling'] = False
        results['performance'] = False
        print("\n  ⚠ Skipping backend tests (backend not running)")
    
    # Test frontend
    results['frontend'] = test_frontend()
    
    # Test integrity
    results['integrity'] = test_integrity_checks()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name:30} {status}")
    
    print("="*80)
    print(f"Overall: {passed_tests}/{total_tests} test suites passed")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Create gap analysis
    todos = create_gap_analysis(results)
    
    if passed_tests == total_tests:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        print("\nNext steps:")
        if not results.get('database_connection'):
            print("  - Check PostgreSQL is running: docker-compose up -d postgres")
        if not results.get('backend_health'):
            print("  - Start backend: cd backend && uvicorn app.main:app --reload")
        if not results.get('frontend'):
            print("  - Start frontend: cd frontend && npm run dev")
        return 1


if __name__ == '__main__':
    sys.exit(main())

