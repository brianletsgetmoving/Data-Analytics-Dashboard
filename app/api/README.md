# Data Analytics API

Node.js/Express API for the Data Analytics Dashboard.

## Setup

### Prerequisites

- Node.js 20+
- PostgreSQL 16
- Python 3.11+ (for ETL script execution)

### Installation

```bash
cd app/api
npm install
```

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://buyer:postgres@postgres:5432/data_analytics
DIRECT_DATABASE_URL=postgresql://buyer:postgres@postgres:5432/data_analytics
NODE_ENV=development
PORT=3001
```

### Generate Prisma Client

```bash
npm run prisma:generate
```

## Development

```bash
npm run dev
```

The API will be available at `http://localhost:3001`

## API Endpoints

### Analytics

- `GET /api/v1/analytics/revenue?periodType=monthly|quarterly|yearly` - Revenue trends
- `GET /api/v1/analytics/metrics?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD` - Monthly metrics
- `GET /api/v1/analytics/heatmap?branchId=uuid&dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD` - Activity heatmap
- `GET /api/v1/analytics/radar?dimension=customer|salesperson|branch&dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD` - Performance radar
- `GET /api/v1/analytics/salesperson-performance?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD&salesPersonId=uuid` - Sales person performance
- `GET /api/v1/analytics/branch-performance?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD&branchId=uuid` - Branch performance

### Admin

- `GET /api/v1/admin/scripts` - List available ETL scripts
- `POST /api/v1/admin/scripts/execute` - Execute an ETL script
  ```json
  {
    "scriptPath": "relationships/complete_quote_linkage.py"
  }
  ```

### Health

- `GET /health` - Health check endpoint

## Architecture

### Services

- **QueryService**: Executes SQL files from `sql/queries/` directory and transforms results
- **ETLService**: Executes Python scripts from `scripts/` directory
- **FilterBuilder**: Safely injects filters into SQL queries using parameterized queries

### Type Safety

All API responses use TypeScript interfaces from `shared/types.ts`:
- `RevenueMetrics`
- `MonthlyMetrics`
- `ActivityHeatmap`
- `SalesRadar`
- `SalesPersonPerformance`
- `BranchPerformance`
- `AnalyticsResponse<T>`

## SQL Query Filter Injection

SQL queries with filter injection points are marked with:
```sql
-- Filters are injected here dynamically
```

The `QueryService` automatically injects filters at these points using the `FilterBuilder` utility, which prevents SQL injection by using parameterized queries.

## Error Handling

All endpoints return standardized `AnalyticsResponse<T>` format:
```typescript
{
  data: T;
  metadata?: {
    count?: number;
    filters_applied?: FilterParams;
    timestamp?: string;
  };
  error?: string;
}
```

## CORS

CORS is configured to allow requests from the frontend (default: `http://localhost:5173`). Configure via `FRONTEND_URL` environment variable.

