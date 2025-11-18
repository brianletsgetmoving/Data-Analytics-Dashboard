#!/bin/bash
# End-to-end testing of the complete stack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "=========================================="
echo "Complete Stack End-to-End Testing"
echo "=========================================="
echo ""

# Check if services are running
echo "1. Checking if services are running..."
echo ""

# Check PostgreSQL
echo "   Checking PostgreSQL..."
if pg_isready -h localhost -p 5432 -U buyer > /dev/null 2>&1; then
    echo "   ✓ PostgreSQL is running"
else
    echo "   ✗ PostgreSQL is not running"
    echo "   Start with: docker-compose up -d postgres"
    exit 1
fi

# Check Backend
echo "   Checking Backend API..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Backend API is running"
    BACKEND_RUNNING=true
else
    echo "   ✗ Backend API is not running"
    echo "   Start with: cd backend && uvicorn app.main:app --reload"
    BACKEND_RUNNING=false
fi

# Check Frontend
echo "   Checking Frontend..."
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✓ Frontend is running"
    FRONTEND_RUNNING=true
else
    echo "   ✗ Frontend is not running"
    echo "   Start with: cd frontend && npm run dev"
    FRONTEND_RUNNING=false
fi

echo ""

# Test Backend
if [ "$BACKEND_RUNNING" = true ]; then
    echo "2. Testing Backend API endpoints..."
    python3 scripts/test_backend_api.py
    echo ""
else
    echo "2. Skipping backend tests (backend not running)"
    echo ""
fi

# Test Frontend
if [ "$FRONTEND_RUNNING" = true ]; then
    echo "3. Testing Frontend pages..."
    python3 scripts/test_frontend.py
    echo ""
else
    echo "3. Skipping frontend tests (frontend not running)"
    echo ""
fi

# Run integrity checks
echo "4. Running database integrity checks..."
timeout 120 python3 scripts/setup_integrity_monitoring.py --execute 2>&1 | tail -20
echo ""

echo "=========================================="
echo "End-to-End Testing Complete"
echo "=========================================="

