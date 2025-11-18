#!/usr/bin/env python3
"""
Test Next.js frontend to ensure it's accessible and serving pages.
"""

import sys
from pathlib import Path
import requests
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

FRONTEND_URL = "http://localhost:3000"
TIMEOUT = 10  # 10 second timeout


def test_frontend_page(path: str, description: str) -> bool:
    """Test a frontend page."""
    url = f"{FRONTEND_URL}{path}"
    try:
        print(f"Testing {description}...", end=" ")
        response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code == 200:
            print(f"✓ OK (status: {response.status_code})")
            return True
        else:
            print(f"✗ FAILED (status: {response.status_code})")
            return False
    except requests.exceptions.Timeout:
        print(f"✗ TIMEOUT (>{TIMEOUT}s)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION ERROR (is frontend running?)")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def main():
    """Test frontend pages."""
    print("="*80)
    print("Next.js Frontend Testing")
    print("="*80)
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Timeout: {TIMEOUT}s per request")
    print("="*80)
    print()
    
    pages = [
        ("/", "Home (redirects to /overview)"),
        ("/overview", "Overview Dashboard"),
        ("/customers", "Customers Page"),
        ("/jobs", "Jobs Page"),
        ("/revenue", "Revenue Page"),
        ("/leads", "Leads Page"),
        ("/sales", "Sales Page"),
    ]
    
    results = []
    for path, desc in pages:
        results.append(test_frontend_page(path, desc))
        time.sleep(0.5)  # Small delay between requests
    
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print("="*80)
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        print("\nNote: Frontend may need to be built first:")
        print("  cd frontend && npm run build && npm start")
        return 1


if __name__ == '__main__':
    sys.exit(main())

