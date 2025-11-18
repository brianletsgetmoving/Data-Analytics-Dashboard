# Analytics Dashboard Backend

FastAPI backend for the analytics dashboard.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://buyer@localhost:5432/data_analytics"

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Analytics Overview
- `GET /api/v1/analytics/overview` - Overview KPIs
- `GET /api/v1/analytics/kpis` - Detailed KPIs
- `GET /api/v1/analytics/trends` - Trend data

### Customer Analytics
- `GET /api/v1/customers/demographics`
- `GET /api/v1/customers/segmentation`
- `GET /api/v1/customers/gender-breakdown`
- `GET /api/v1/customers/lifetime-value`
- `GET /api/v1/customers/retention`
- `GET /api/v1/customers/geographic-distribution`

### Job Analytics
- `GET /api/v1/jobs/metrics`
- `GET /api/v1/jobs/volume-trends`
- `GET /api/v1/jobs/status-distribution`
- `GET /api/v1/jobs/type-distribution`
- `GET /api/v1/jobs/seasonal-patterns`
- `GET /api/v1/jobs/crew-utilization`

### Revenue Analytics
- `GET /api/v1/revenue/trends`
- `GET /api/v1/revenue/by-branch`
- `GET /api/v1/revenue/by-region`
- `GET /api/v1/revenue/by-source`
- `GET /api/v1/revenue/forecasts`
- `GET /api/v1/revenue/by-segment`

### Lead Analytics
- `GET /api/v1/leads/demographics`
- `GET /api/v1/leads/conversion-funnel`
- `GET /api/v1/leads/response-time`
- `GET /api/v1/leads/source-performance`
- `GET /api/v1/leads/status-distribution`

### Sales Performance
- `GET /api/v1/sales/performance`
- `GET /api/v1/sales/rankings`
- `GET /api/v1/sales/trends`
- `GET /api/v1/sales/comparison`
- `GET /api/v1/sales/efficiency`

## Universal Filters

All endpoints support universal filtering via query parameters:

- `branch_id` - Filter by branch ID
- `branch_name` - Filter by branch name
- `date_from` - Start date (ISO format)
- `date_to` - End date (ISO format)
- `sales_person_id` - Filter by sales person ID
- `sales_person_name` - Filter by sales person name
- `job_status` - Comma-separated job statuses
- `aggregation_period` - daily, weekly, monthly, quarterly, yearly
- `limit` - Results limit (1-1000)
- `offset` - Results offset

Example:
```
GET /api/v1/analytics/overview?branch_name=NORTH%20YORK&date_from=2024-01-01&aggregation_period=monthly
```

