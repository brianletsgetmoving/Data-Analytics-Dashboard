#!/bin/bash

# End-to-end pipeline execution script
# Runs all phases in sequence

set -e  # Exit on error

echo "=========================================="
echo "Data Analytics Pipeline - Full Execution"
echo "=========================================="

# Configuration
DATA_RAW_DIR="${1:-data/raw}"
DATA_PROCESSED_DIR="${2:-data/processed}"

# Phase 1: Infrastructure
echo ""
echo "Phase 1: Infrastructure Setup"
echo "-------------------------------"
echo "Starting PostgreSQL container..."
docker-compose up -d

echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Phase 2: Data Cleaning
echo ""
echo "Phase 2: Data Cleaning"
echo "----------------------"
python -m src.cleaning.pipeline "$DATA_RAW_DIR" "$DATA_PROCESSED_DIR"

# Phase 2B: Entity Resolution (Splink)
echo ""
echo "Phase 2B: Entity Resolution (Splink)"
echo "------------------------------------"
echo "Note: This phase requires manual execution of Splink matching"
echo "Run: python -m src.entity_resolution.match_predictions"

# Phase 3: Data Import
echo ""
echo "Phase 3: Data Import"
echo "-------------------"
python -m src.import.import_to_postgresql "$DATA_PROCESSED_DIR"

# Phase 4: Analytics
echo ""
echo "Phase 4: Advanced Analytics"
echo "---------------------------"
echo "Running duplicate detection..."
python -m src.analytics.job_duplicate_detection

echo "Calculating rolling window job counts..."
python -m src.analytics.rolling_window_jobs

echo ""
echo "=========================================="
echo "Pipeline execution complete!"
echo "=========================================="

