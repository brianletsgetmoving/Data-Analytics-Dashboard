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


def test_database_connection():
    """Test database connectivity."""
    print("\n1. Testing Database Connection...")
    try:
        from src.testing.database_connection import get_db_connection
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
    """Test basic database queries."""
    print("\n2. Testing Database Queries...")
    try:
        from src.testing.database_connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test queries
        tests = [
            ("SELECT COUNT(*) FROM jobs", "Jobs count"),
            ("SELECT COUNT(*) FROM customers", "Customers count"),
            ("SELECT COUNT(*) FROM lead_status", "LeadStatus count"),
            ("SELECT COUNT(*) FROM sales_persons", "SalesPersons count"),
        ]
        
        all_passed = True
        for query, desc in tests:
            try:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                print(f"  ✓ {desc}: {result}")
            except Exception as e:
                print(f"  ✗ {desc} failed: {e}")
                all_passed = False
        
        cursor.close()
        conn.close()
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
    
    endpoints = [
        ("/api/v1/analytics/overview", "Analytics Overview"),
        ("/api/v1/analytics/kpis", "Analytics KPIs"),
        ("/api/v1/customers/demographics", "Customer Demographics"),
        ("/api/v1/jobs/metrics", "Job Metrics"),
        ("/api/v1/revenue/trends", "Revenue Trends"),
        ("/api/v1/leads/conversion-funnel", "Lead Conversion Funnel"),
        ("/api/v1/sales/performance", "Sales Performance"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, desc in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                params={"limit": 10},
                timeout=TIMEOUT_API_TEST
            )
            if response.status_code == 200:
                print(f"  ✓ {desc}")
                passed += 1
            else:
                print(f"  ✗ {desc} (status: {response.status_code})")
        except requests.exceptions.Timeout:
            print(f"  ✗ {desc} (timeout)")
        except Exception as e:
            print(f"  ✗ {desc} (error: {e})")
    
    print(f"\n  Backend API: {passed}/{total} endpoints working")
    return passed == total


def test_frontend():
    """Test frontend pages."""
    print("\n5. Testing Frontend...")
    
    pages = [
        ("/", "Home"),
        ("/overview", "Overview"),
        ("/customers", "Customers"),
        ("/jobs", "Jobs"),
        ("/revenue", "Revenue"),
    ]
    
    passed = 0
    total = len(pages)
    
    for path, desc in pages:
        try:
            response = requests.get(
                f"{FRONTEND_URL}{path}",
                timeout=TIMEOUT_FRONTEND_TEST,
                allow_redirects=True
            )
            if response.status_code == 200:
                print(f"  ✓ {desc}")
                passed += 1
            else:
                print(f"  ✗ {desc} (status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Frontend is not running (start with: cd frontend && npm run dev)")
            break
        except requests.exceptions.Timeout:
            print(f"  ✗ {desc} (timeout)")
        except Exception as e:
            print(f"  ✗ {desc} (error: {e})")
    
    if total > 0:
        print(f"\n  Frontend: {passed}/{total} pages accessible")
        return passed == total
    else:
        return False


def test_integrity_checks():
    """Run database integrity checks."""
    print("\n6. Running Database Integrity Checks...")
    success, output = run_with_timeout(
        f"python3 scripts/setup_integrity_monitoring.py --execute",
        TIMEOUT_INTEGRITY_CHECK,
        "Integrity checks"
    )
    
    if success:
        # Parse output for key metrics
        if "Job-Customer Linkage Rate" in output:
            print("  Integrity check completed successfully")
        return True
    else:
        print("  Integrity check failed or timed out")
        return False


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
    else:
        results['backend_endpoints'] = False
        print("\n  ⚠ Skipping backend endpoint tests (backend not running)")
    
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

