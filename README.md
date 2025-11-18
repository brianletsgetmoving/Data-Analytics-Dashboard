# PostgreSQL Data Engineering Pipeline

Production-grade PostgreSQL database with data import, cleaning, probabilistic entity resolution (Splink), customer unification, and continuous monitoring for SmartMoving CRM data consolidation.

## Architecture Overview

**Data Flow**: CSV Files → Data Cleaning (Pydantic + Pandas) → Great Expectations Validation → Splink Entity Resolution → Customer Unification → PostgreSQL Import → SmartMoving API Sync → Continuous Monitoring

## Technology Stack

- Database: PostgreSQL 16 (Docker)
- Schema Management: Prisma (Python client)
- Data Processing: Python 3.11+ with Pandas, Pydantic v2
- Entity Resolution: Splink (probabilistic matching)
- Data Quality: Great Expectations
- API Integration: SmartMoving External API

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 16 (via Docker)

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Database credentials
# - API keys (SmartMoving)
# - Alert email/Slack webhook
```

### 3. Database Setup

```bash
# Start PostgreSQL container
docker-compose up -d

# Initialize Prisma
cd prisma
prisma migrate dev --name init
prisma generate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Phase-by-Phase Execution Guide

### Phase 1: Infrastructure Setup

```bash
# Start database
docker-compose up -d

# Initialize Prisma schema
prisma migrate dev --name init
```

### Phase 2: Data Cleaning

```bash
# Run cleaning pipeline
python -m src.cleaning.pipeline data/raw data/processed
```

### Phase 2B: Entity Resolution (Splink)

```bash
# Run Splink matching
python -m src.entity_resolution.match_predictions
```

### Phase 3: Data Import

```bash
# Import cleaned data to PostgreSQL
python -m src.import.import_to_postgresql data/processed
```

### Phase 4: Analytics

```bash
# Run duplicate detection
python -m src.analytics.job_duplicate_detection

# Calculate rolling window job counts
python -m src.analytics.rolling_window_jobs

# Determine customer gender
python -m src.analytics.gender_batch_processor
```

## Expected Runtimes

- **Phase 2 (Cleaning)**: ~30-60 minutes for 500K+ records
- **Phase 2B (Splink)**: ~2-4 hours for 50K customers
- **Phase 3 (Import)**: ~1-2 hours for full dataset
- **Phase 4 (Analytics)**: ~30-60 minutes

## Expected Metrics

- **After Phase 2B**: 95%+ duplicate accuracy, <1% false positive rate
- **After Phase 3**: 100% customer unification, <1% duplicate rate
- **After Phase 4**: Complete analytics pipeline operational
- **Ongoing**: >95% data quality compliance, <1% duplicate rate maintained

## Data Quality SLAs

- **Completeness**: Email, phone, address ≥95% non-null
- **Accuracy**: Email format 100%, phone format 100%
- **Consistency**: Branch standardization 100%, state abbreviations 100%
- **Timeliness**: Most recent record ≤30 days old
- **Uniqueness**: Duplicate rate <1%

## Project Structure

```
.
├── data/
│   ├── raw/          # Input CSV files
│   └── processed/    # Cleaned parquet files
├── prisma/
│   └── schema.prisma # Database schema
├── src/
│   ├── cleaning/     # Data cleaning modules
│   ├── validation/   # Pydantic schemas
│   ├── quality/      # Great Expectations
│   ├── entity_resolution/  # Splink matching
│   ├── monitoring/   # Data quality monitoring
│   ├── import/       # PostgreSQL import
│   ├── unification/  # Customer unification
│   ├── api/          # SmartMoving API
│   └── analytics/    # Advanced analytics
├── sql/
│   └── queries/      # SQL queries
└── scripts/          # Utility scripts
```

## Error Handling & Retry Strategies

- **API calls**: Exponential backoff (1s, 2s, 4s, 8s)
- **Database operations**: Connection pooling, transaction rollback
- **File I/O**: Retry with exponential backoff
- **Splink**: Checkpoint/resume for large datasets

## Monitoring & Alerts

- Post-import validation runs automatically
- SLA violations trigger email/Slack alerts
- Weekly quality reports generated
- PostgreSQL audit triggers log all Customer table changes

## License

Proprietary - Internal Use Only

# Data-Analytics-Dashboard
