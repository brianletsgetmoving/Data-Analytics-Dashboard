#!/usr/bin/env python3
"""
Test FastAPI backend endpoints to ensure they're working correctly.
"""

import sys
from pathlib import Path
import requests
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE_URL = "http://localhost:8000"
TIMEOUT = 10  # 10 second timeout for each request


def test_endpoint(endpoint: str, description: str) -> bool:
    """Test a single API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        print(f"Testing {description}...", end=" ")
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ OK (status: {response.status_code})")
            return True
        else:
            print(f"✗ FAILED (status: {response.status_code})")
            return False
    except requests.exceptions.Timeout:
        print(f"✗ TIMEOUT (>{TIMEOUT}s)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION ERROR (is backend running?)")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def main():
    """Test all API endpoints."""
    print("="*80)
    print("FastAPI Backend Endpoint Testing")
    print("="*80)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Timeout: {TIMEOUT}s per request")
    print("="*80)
    print()
    
    # Test health endpoint first
    print("Health Check:")
    health_ok = test_endpoint("/health", "Health check")
    if not health_ok:
        print("\n❌ Backend is not running or not accessible!")
        print("   Start the backend with: cd backend && uvicorn app.main:app --reload")
        return 1
    print()
    
    # Test analytics endpoints
    print("Analytics Endpoints:")
    analytics_tests = [
        ("/api/v1/analytics/overview", "Overview"),
        ("/api/v1/analytics/kpis", "KPIs"),
        ("/api/v1/analytics/trends", "Trends"),
    ]
    
    analytics_results = []
    for endpoint, desc in analytics_tests:
        analytics_results.append(test_endpoint(endpoint, desc))
    print()
    
    # Test customer endpoints
    print("Customer Endpoints:")
    customer_tests = [
        ("/api/v1/customers/demographics", "Demographics"),
        ("/api/v1/customers/segmentation", "Segmentation"),
        ("/api/v1/customers/gender-breakdown", "Gender Breakdown"),
    ]
    
    customer_results = []
    for endpoint, desc in customer_tests:
        customer_results.append(test_endpoint(endpoint, desc))
    print()
    
    # Test job endpoints
    print("Job Endpoints:")
    job_tests = [
        ("/api/v1/jobs/metrics", "Metrics"),
        ("/api/v1/jobs/volume-trends", "Volume Trends"),
        ("/api/v1/jobs/status-distribution", "Status Distribution"),
    ]
    
    job_results = []
    for endpoint, desc in job_tests:
        job_results.append(test_endpoint(endpoint, desc))
    print()
    
    # Test revenue endpoints
    print("Revenue Endpoints:")
    revenue_tests = [
        ("/api/v1/revenue/trends", "Trends"),
        ("/api/v1/revenue/by-branch", "By Branch"),
    ]
    
    revenue_results = []
    for endpoint, desc in revenue_tests:
        revenue_results.append(test_endpoint(endpoint, desc))
    print()
    
    # Test lead endpoints
    print("Lead Endpoints:")
    lead_tests = [
        ("/api/v1/leads/conversion-funnel", "Conversion Funnel"),
        ("/api/v1/leads/source-performance", "Source Performance"),
    ]
    
    lead_results = []
    for endpoint, desc in lead_tests:
        lead_results.append(test_endpoint(endpoint, desc))
    print()
    
    # Test sales endpoints
    print("Sales Endpoints:")
    sales_tests = [
        ("/api/v1/sales/performance", "Performance"),
        ("/api/v1/sales/rankings", "Rankings"),
    ]
    
    sales_results = []
    for endpoint, desc in sales_tests:
        sales_results.append(test_endpoint(endpoint, desc))
    print()
    
    # Summary
    all_results = [health_ok] + analytics_results + customer_results + job_results + revenue_results + lead_results + sales_results
    passed = sum(all_results)
    total = len(all_results)
    
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print("="*80)
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

