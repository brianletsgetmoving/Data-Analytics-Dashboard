#!/bin/bash
# Run migration scripts with timeouts to prevent hanging

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Timeout values (in seconds)
TIMEOUT_ANALYSIS=300      # 5 minutes
TIMEOUT_LINKING=600       # 10 minutes
TIMEOUT_POPULATION=1800   # 30 minutes
TIMEOUT_INTEGRITY=120     # 2 minutes

echo "=========================================="
echo "Running Database Migrations with Timeouts"
echo "=========================================="
echo ""

# 1. Analyze orphaned records
echo "1. Analyzing orphaned records (timeout: ${TIMEOUT_ANALYSIS}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_ANALYSIS} scripts/analyze_orphaned_performance_records.py || {
    echo "WARNING: Analysis timed out or failed, continuing..."
}
echo ""

# 2. Link orphaned performance records
echo "2. Linking orphaned performance records (timeout: ${TIMEOUT_LINKING}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_LINKING} scripts/link_orphaned_performance_records.py --execute || {
    echo "WARNING: Linking timed out or failed, continuing..."
}
echo ""

# 3. Complete quote linkage
echo "3. Completing quote linkage (timeout: ${TIMEOUT_LINKING}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_LINKING} scripts/complete_quote_linkage.py --execute || {
    echo "WARNING: Quote linkage timed out or failed, continuing..."
}
echo ""

# 4. Link BadLead to LeadStatus
echo "4. Linking BadLead to LeadStatus (timeout: ${TIMEOUT_LINKING}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_LINKING} scripts/link_badlead_to_leadstatus.py --execute || {
    echo "WARNING: BadLead linkage timed out or failed, continuing..."
}
echo ""

# 5. Populate lead sources
echo "5. Populating lead sources (timeout: ${TIMEOUT_POPULATION}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_POPULATION} scripts/populate_lead_sources.py --execute || {
    echo "WARNING: Lead sources population timed out or failed, continuing..."
}
echo ""

# 6. Populate branches
echo "6. Populating branches (timeout: ${TIMEOUT_POPULATION}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_POPULATION} scripts/populate_branches.py --execute || {
    echo "WARNING: Branches population timed out or failed, continuing..."
}
echo ""

# 7. Populate customer timeline
echo "7. Populating customer timeline (timeout: ${TIMEOUT_LINKING}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_LINKING} scripts/populate_customer_timeline_fields.py --execute || {
    echo "WARNING: Customer timeline population timed out or failed, continuing..."
}
echo ""

# 8. Setup integrity monitoring
echo "8. Setting up integrity monitoring (timeout: ${TIMEOUT_INTEGRITY}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_INTEGRITY} scripts/setup_integrity_monitoring.py --setup --execute || {
    echo "WARNING: Integrity monitoring setup timed out or failed, continuing..."
}
echo ""

# 9. Run integrity check
echo "9. Running integrity check (timeout: ${TIMEOUT_INTEGRITY}s)..."
python3 scripts/run_with_timeout.py ${TIMEOUT_INTEGRITY} scripts/setup_integrity_monitoring.py --execute || {
    echo "WARNING: Integrity check timed out or failed, continuing..."
}
echo ""

echo "=========================================="
echo "Migration Scripts Complete"
echo "=========================================="

