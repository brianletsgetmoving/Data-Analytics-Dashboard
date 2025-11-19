# Shared Types Documentation

**File:** `shared/types.ts`  
**Purpose:** Single source of truth for TypeScript interfaces used across the entire application stack  
**Last Updated:** Current

---

## Overview

The `shared/types.ts` file defines all TypeScript interfaces that bridge the gap between:
- **Database Layer (SQL Queries)** → Returns raw database results
- **Backend Layer (Node.js API)** → Transforms and serves data
- **Frontend Layer (React)** → Consumes and displays data

All interfaces are designed to match SQL query outputs exactly, ensuring type safety across all layers.

---

## Type Definitions

### RevenueMetrics

**Purpose:** Period-based revenue trends by month, quarter, and year

**SQL Source:** `sql/queries/revenue_trends.sql`

**Interface:**
```typescript
export interface RevenueMetrics {
  period_type: 'monthly' | 'quarterly' | 'yearly';
  period: Date | string; // PostgreSQL timestamp
  job_count: number;
  revenue: number | null;
  booked_revenue: number | null;
  closed_revenue: number | null;
  previous_period_revenue: number | null;
  period_over_period_change_percent: number | null;
}
```

**Field Mappings:**
- `period_type` → SQL: `'monthly'|'quarterly'|'yearly'` (text)
- `period` → SQL: `date_trunc('month'|'quarter'|'year', job_date)` (timestamp)
- `job_count` → SQL: `count(*)` (integer)
- `revenue` → SQL: `sum(coalesce(total_actual_cost, total_estimated_cost, 0))` (numeric, nullable)
- `booked_revenue` → SQL: `sum(...) filter (where opportunity_status = 'BOOKED')` (numeric, nullable)
- `closed_revenue` → SQL: `sum(...) filter (where opportunity_status = 'CLOSED')` (numeric, nullable)
- `previous_period_revenue` → SQL: `lag(sum(...)) over (order by ...)` (numeric, nullable)
- `period_over_period_change_percent` → SQL: `round((revenue - previous_period_revenue)::numeric / nullif(previous_period_revenue, 0) * 100, 2)` (numeric, nullable)

**Usage:**
- **Backend:** `GET /api/v1/analytics/revenue?periodType=monthly`
- **Frontend:** Revenue trend line chart in `OverviewDashboard.tsx`

**Notes:**
- Query returns all period types in a single result set
- Backend filters by `period_type` based on query parameter
- Dates are returned as PostgreSQL timestamps, converted to ISO strings for JSON

---

### MonthlyMetrics

**Purpose:** Monthly summary of key business metrics (KPIs)

**SQL Source:** `sql/queries/monthly_metrics_summary.sql`

**Interface:**
```typescript
export interface MonthlyMetrics {
  month: Date | string; // PostgreSQL timestamp (date_trunc('month', job_date))
  year: number;
  month_number: number;
  total_jobs: number;
  quoted_jobs: number;
  booked_jobs: number;
  closed_jobs: number;
  lost_jobs: number;
  cancelled_jobs: number;
  total_revenue: number | null;
  avg_job_value: number | null;
  unique_customers: number;
  active_branches: number;
  active_sales_people: number;
  booking_rate_percent: number | null;
}
```

**Field Mappings:**
- `month` → SQL: `date_trunc('month', job_date)` (timestamp)
- `year` → SQL: `extract(year from job_date)` (integer)
- `month_number` → SQL: `extract(month from job_date)` (integer)
- `total_jobs` → SQL: `count(*)` (integer)
- `quoted_jobs` → SQL: `count(*) filter (where opportunity_status = 'QUOTED')` (integer)
- `booked_jobs` → SQL: `count(*) filter (where opportunity_status = 'BOOKED')` (integer)
- `closed_jobs` → SQL: `count(*) filter (where opportunity_status = 'CLOSED')` (integer)
- `lost_jobs` → SQL: `count(*) filter (where opportunity_status = 'LOST')` (integer)
- `cancelled_jobs` → SQL: `count(*) filter (where opportunity_status = 'CANCELLED')` (integer)
- `total_revenue` → SQL: `sum(coalesce(total_actual_cost, total_estimated_cost, 0))` (numeric, nullable)
- `avg_job_value` → SQL: `avg(coalesce(total_actual_cost, total_estimated_cost))` (numeric, nullable)
- `unique_customers` → SQL: `count(distinct customer_id)` (integer)
- `active_branches` → SQL: `count(distinct branch_name)` (integer)
- `active_sales_people` → SQL: `count(distinct sales_person_name)` (integer)
- `booking_rate_percent` → SQL: `round(count(*) filter (where opportunity_status = 'BOOKED')::numeric / nullif(count(*), 0) * 100, 2)` (numeric, nullable)

**Usage:**
- **Backend:** `GET /api/v1/analytics/metrics?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD`
- **Frontend:** KPI cards in `OverviewDashboard.tsx` (Total Jobs, Total Revenue, Booking Rate, Avg Job Value)

**Notes:**
- All aggregations happen in SQL (no calculations in backend or frontend)
- NULL values preserved (not converted to 0) to match TypeScript interface

---

### ActivityHeatmap

**Purpose:** Branch-month activity matrix for heatmap visualization

**SQL Source:** `sql/queries/analytics/heatmap_revenue_by_branch_month.sql`

**Interface:**
```typescript
export interface ActivityHeatmap {
  branch_name: string;
  month: string; // Format: 'YYYY-MM'
  value: number | null; // Revenue or job count
}
```

**Field Mappings:**
- `branch_name` → SQL: `coalesce(b.name, 'Unknown')` (text)
- `month` → SQL: `to_char(date_trunc('month', j.job_date), 'YYYY-MM')` (text)
- `value` → SQL: `sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0))` (numeric, nullable)

**Usage:**
- **Backend:** `GET /api/v1/analytics/heatmap?branchId=uuid&dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD`
- **Frontend:** Heatmap visualization in `ActivityHeatmap.tsx`

**Notes:**
- Query has filter injection point: `-- Filters are injected here dynamically`
- FilterBuilder utility injects WHERE clause conditions safely
- `value` can represent revenue or job count depending on dimension parameter
- Month format is always 'YYYY-MM' for consistent sorting

---

### SalesRadar

**Purpose:** Multi-dimensional performance metrics for radar chart visualization

**SQL Source:** `sql/queries/analytics/customer_segmentation_radar.sql` (for customer dimension)

**Interface:**
```typescript
export interface SalesRadar {
  subject: string; // 'Lifetime Value' | 'Job Frequency' | 'Avg Job Value' | 'Customer Lifespan'
  value: number | null;
  full_mark: number | null; // Maximum value for scaling
}
```

**Field Mappings:**
- `subject` → SQL: `'Lifetime Value'|'Job Frequency'|'Avg Job Value'|'Customer Lifespan'` (text)
- `value` → SQL: `coalesce(avg(lifetime_value|total_jobs|avg_job_value|customer_lifespan_days), 0)` (numeric, nullable)
- `full_mark` → SQL: `coalesce(max(lifetime_value|total_jobs|avg_job_value|customer_lifespan_days), 0)` (numeric, nullable)

**Usage:**
- **Backend:** `GET /api/v1/analytics/radar?dimension=customer|salesperson|branch&dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD`
- **Frontend:** Radar chart in `PerformanceRadar.tsx`

**Notes:**
- For `dimension=customer`: Uses `customer_segmentation_radar.sql` directly
- For `dimension=salesperson` or `branch`: Backend transforms `revenue_by_sales_person.sql` or `revenue_by_branch.sql` output
- `subject` determines the axis label on the radar chart
- `full_mark` is used to scale the radar chart axes
- Current implementation uses simplified transformation (needs improvement)

---

### SalesPersonPerformance

**Purpose:** Sales person performance metrics

**SQL Source:** `sql/queries/revenue_by_sales_person.sql`

**Interface:**
```typescript
export interface SalesPersonPerformance {
  sales_person_name: string | null;
  total_jobs: number;
  total_revenue: number | null;
  avg_job_value: number | null;
  booked_revenue: number | null;
  closed_revenue: number | null;
  booked_jobs: number;
  closed_jobs: number;
  avg_booked_value: number | null;
  branches_worked: number;
  unique_customers: number;
}
```

**Field Mappings:**
- `sales_person_name` → SQL: `sales_person_name` (text, nullable)
- `total_jobs` → SQL: `count(*)` (integer)
- `total_revenue` → SQL: `sum(coalesce(total_actual_cost, total_estimated_cost, 0))` (numeric, nullable)
- `avg_job_value` → SQL: `avg(coalesce(total_actual_cost, total_estimated_cost))` (numeric, nullable)
- `booked_revenue` → SQL: `sum(...) filter (where opportunity_status = 'BOOKED')` (numeric, nullable)
- `closed_revenue` → SQL: `sum(...) filter (where opportunity_status = 'CLOSED')` (numeric, nullable)
- `booked_jobs` → SQL: `count(*) filter (where opportunity_status = 'BOOKED')` (integer)
- `closed_jobs` → SQL: `count(*) filter (where opportunity_status = 'CLOSED')` (integer)
- `avg_booked_value` → SQL: `round(sum(...) filter (where ...)::numeric / nullif(count(*) filter (where ...), 0), 2)` (numeric, nullable)
- `branches_worked` → SQL: `count(distinct branch_name)` (integer)
- `unique_customers` → SQL: `count(distinct customer_id)` (integer)

**Usage:**
- **Backend:** `GET /api/v1/analytics/salesperson-performance?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD&salesPersonId=uuid`
- **Frontend:** Performance table in `SalesPersonPerformanceTable.tsx`

**Notes:**
- All aggregations happen in SQL
- NULL values preserved for nullable fields

---

### BranchPerformance

**Purpose:** Branch performance metrics

**SQL Source:** `sql/queries/revenue_by_branch.sql`

**Interface:**
```typescript
export interface BranchPerformance {
  branch_name: string | null;
  total_jobs: number;
  total_revenue: number | null;
  avg_job_value: number | null;
  booked_revenue: number | null;
  closed_revenue: number | null;
  booked_jobs: number;
  closed_jobs: number;
  avg_booked_value: number | null;
  avg_closed_value: number | null;
}
```

**Field Mappings:**
- `branch_name` → SQL: `branch_name` (text, nullable)
- `total_jobs` → SQL: `count(*)` (integer)
- `total_revenue` → SQL: `sum(coalesce(total_actual_cost, total_estimated_cost, 0))` (numeric, nullable)
- `avg_job_value` → SQL: `avg(coalesce(total_actual_cost, total_estimated_cost))` (numeric, nullable)
- `booked_revenue` → SQL: `sum(...) filter (where opportunity_status = 'BOOKED')` (numeric, nullable)
- `closed_revenue` → SQL: `sum(...) filter (where opportunity_status = 'CLOSED')` (numeric, nullable)
- `booked_jobs` → SQL: `count(*) filter (where opportunity_status = 'BOOKED')` (integer)
- `closed_jobs` → SQL: `count(*) filter (where opportunity_status = 'CLOSED')` (integer)
- `avg_booked_value` → SQL: `round(sum(...) filter (where ...)::numeric / nullif(count(*) filter (where ...), 0), 2)` (numeric, nullable)
- `avg_closed_value` → SQL: `round(sum(...) filter (where ...)::numeric / nullif(count(*) filter (where ...), 0), 2)` (numeric, nullable)

**Usage:**
- **Backend:** `GET /api/v1/analytics/branch-performance?dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD&branchId=uuid`
- **Frontend:** Performance table in `BranchPerformanceTable.tsx`

**Notes:**
- Similar structure to `SalesPersonPerformance`
- Includes `avg_closed_value` which is unique to branch performance

---

### FilterParams

**Purpose:** Query filter parameters for dynamic WHERE clause building

**SQL Source:** Used by FilterBuilder utility to inject filters into SQL queries

**Interface:**
```typescript
export interface FilterParams {
  date_from?: string; // ISO date string: 'YYYY-MM-DD'
  date_to?: string; // ISO date string: 'YYYY-MM-DD'
  branch_id?: string; // UUID
  branch_name?: string;
  sales_person_id?: string; // UUID
  sales_person_name?: string;
  customer_id?: string; // UUID
  opportunity_status?: 'QUOTED' | 'BOOKED' | 'LOST' | 'CANCELLED' | 'CLOSED';
  lead_source_id?: string; // UUID
  period_type?: 'monthly' | 'quarterly' | 'yearly';
}
```

**Field Usage:**
- `date_from` / `date_to` → FilterBuilder: `j.job_date >= $1 AND j.job_date <= $2`
- `branch_id` → FilterBuilder: `j.branch_id = $1`
- `branch_name` → FilterBuilder: `b.name = $1`
- `sales_person_id` → FilterBuilder: `j.sales_person_id = $1`
- `sales_person_name` → FilterBuilder: `sp.name = $1`
- `customer_id` → FilterBuilder: `j.customer_id = $1`
- `opportunity_status` → FilterBuilder: `j.opportunity_status = $1`
- `lead_source_id` → FilterBuilder: `ls.lead_source_id = $1`
- `period_type` → Used for filtering `RevenueMetrics` results (not injected into SQL)

**Usage:**
- **Backend:** All analytics endpoints accept FilterParams as query parameters
- **Frontend:** Filter controls pass FilterParams to API endpoints
- **FilterBuilder:** Converts FilterParams to safe SQL WHERE clauses

**Notes:**
- All filters are optional
- Date filters use ISO format: 'YYYY-MM-DD'
- UUID fields must be valid UUID strings
- FilterBuilder uses parameterized queries to prevent SQL injection

---

### ETLExecutionResult

**Purpose:** Python script execution result

**SQL Source:** N/A (returned by ETLService)

**Interface:**
```typescript
export interface ETLExecutionResult {
  success: boolean;
  exitCode: number;
  logs: string[];
  error?: string;
}
```

**Field Usage:**
- `success` → `true` if exit code is 0, `false` otherwise
- `exitCode` → Python script exit code (0 = success, 1 = failure)
- `logs` → Combined stdout and stderr output lines
- `error` → Error message if execution failed

**Usage:**
- **Backend:** `POST /api/v1/admin/scripts/execute` returns `ETLExecutionResult`
- **Frontend:** Admin panel displays execution status and logs

**Notes:**
- Exit code 0 = success, non-zero = failure
- Logs are filtered to remove empty lines
- Error field only present if `success` is `false`

---

### AnalyticsResponse<T>

**Purpose:** Standard API response wrapper for all analytics endpoints

**SQL Source:** N/A (wrapper type)

**Interface:**
```typescript
export interface AnalyticsResponse<T> {
  data: T;
  metadata?: {
    count?: number;
    filters_applied?: FilterParams;
    timestamp?: string;
  };
  error?: string;
}
```

**Field Usage:**
- `data` → The actual data array (e.g., `RevenueMetrics[]`, `MonthlyMetrics[]`)
- `metadata.count` → Number of records returned
- `metadata.filters_applied` → Filters that were applied to the query
- `metadata.timestamp` → ISO timestamp of when the response was generated
- `error` → Error message if request failed (only present on error)

**Usage:**
- **Backend:** All analytics endpoints return `AnalyticsResponse<T>`
- **Frontend:** TanStack Query hooks consume `AnalyticsResponse<T>`

**Examples:**
```typescript
// Success response
{
  data: RevenueMetrics[],
  metadata: {
    count: 12,
    filters_applied: { period_type: 'monthly' },
    timestamp: '2024-11-19T13:00:00.000Z'
  }
}

// Error response
{
  data: [] as RevenueMetrics[],
  error: 'Validation error: Invalid period type'
}
```

**Notes:**
- Generic type `T` allows type-safe responses for each endpoint
- Error responses still include `data` field (empty array) for consistency
- Metadata is optional but recommended for all responses

---

## Type Safety Rules

### 1. NULL Handling

**Rule:** All nullable SQL columns must use `| null` union types in TypeScript

**Examples:**
- ✅ `revenue: number | null` (SQL: `numeric` column, can be NULL)
- ✅ `sales_person_name: string | null` (SQL: `text` column, can be NULL)
- ❌ `total_jobs: number | null` (SQL: `count(*)` always returns integer, never NULL)

**Rationale:** Preserves database semantics and prevents type mismatches

### 2. Date Handling

**Rule:** PostgreSQL timestamps are typed as `Date | string`

**Examples:**
- ✅ `period: Date | string` (PostgreSQL `timestamp`)
- ✅ `month: Date | string` (PostgreSQL `timestamp`)

**Rationale:** 
- Prisma returns Date objects
- JSON serialization converts to ISO strings
- Frontend can parse strings or use Date objects

### 3. Numeric Types

**Rule:** PostgreSQL `numeric` → TypeScript `number | null`

**Examples:**
- ✅ `revenue: number | null` (SQL: `numeric`)
- ✅ `avg_job_value: number | null` (SQL: `numeric`)

**Rationale:** Prisma Decimal types are converted to numbers in QueryService

### 4. Enum Types

**Rule:** Use string literal unions for enums

**Examples:**
- ✅ `period_type: 'monthly' | 'quarterly' | 'yearly'`
- ✅ `opportunity_status?: 'QUOTED' | 'BOOKED' | 'LOST' | 'CANCELLED' | 'CLOSED'`

**Rationale:** Type-safe without requiring enum definitions

---

## SQL Query Mapping

### Direct Mappings (1:1)

These interfaces map directly to SQL query outputs:

| Interface | SQL Query | Mapping Type |
|-----------|----------|--------------|
| `RevenueMetrics` | `revenue_trends.sql` | Direct (filtered by period_type) |
| `MonthlyMetrics` | `monthly_metrics_summary.sql` | Direct |
| `ActivityHeatmap` | `analytics/heatmap_revenue_by_branch_month.sql` | Direct (with filter injection) |
| `SalesRadar` | `analytics/customer_segmentation_radar.sql` | Direct (for customer dimension) |
| `SalesPersonPerformance` | `revenue_by_sales_person.sql` | Direct |
| `BranchPerformance` | `revenue_by_branch.sql` | Direct |

### Transformed Mappings

These interfaces require transformation from SQL output:

| Interface | SQL Query | Transformation |
|-----------|----------|----------------|
| `SalesRadar` (salesperson) | `revenue_by_sales_person.sql` | Backend transforms to radar format |
| `SalesRadar` (branch) | `revenue_by_branch.sql` | Backend transforms to radar format |

**Note:** Current transformation is simplified and needs improvement.

---

## Import Usage

### Backend (Node.js/TypeScript)

```typescript
// Using path alias (recommended)
import { RevenueMetrics, FilterParams } from '@shared/types';

// Path alias configured in tsconfig.json:
// "@shared/*": ["shared/*"]
```

### Frontend (React/TypeScript)

```typescript
// Using path alias (recommended)
import { RevenueMetrics, AnalyticsResponse } from '@shared/types';

// Path alias should be configured in vite.config.ts or tsconfig.json
```

### Path Resolution

**From `app/api/src/`:**
- Path alias: `@shared/types` → resolves to `../../shared/types.ts`
- Relative path: `../../../shared/types` → also works but not recommended

**From `app/web/src/`:**
- Path alias: `@shared/types` → resolves to `../../shared/types.ts`
- Relative path: `../../../shared/types` → also works but not recommended

---

## Validation

### Backend Validation (Zod)

All FilterParams are validated using Zod schemas:

```typescript
const filterParamsSchema = z.object({
  date_from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  date_to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  branch_id: z.string().uuid().optional(),
  // ... etc
});
```

### Frontend Validation

Frontend should validate filter inputs before sending to API:
- Date strings must match ISO format: 'YYYY-MM-DD'
- UUID strings must be valid UUIDs
- Enum values must match allowed values

---

## Best Practices

### 1. Always Use Shared Types

**✅ DO:**
```typescript
import { RevenueMetrics } from '@shared/types';
const data: RevenueMetrics[] = await fetchRevenue();
```

**❌ DON'T:**
```typescript
// Don't create duplicate types
interface RevenueMetrics { ... } // ❌ Wrong - use shared types
```

### 2. Preserve NULL Values

**✅ DO:**
```typescript
// Preserve NULL from database
if (revenue === null) {
  // Handle NULL case
}
```

**❌ DON'T:**
```typescript
// Don't convert NULL to 0
const revenue = data.revenue || 0; // ❌ Wrong - loses NULL semantics
```

### 3. Handle Date Types

**✅ DO:**
```typescript
// Handle both Date and string
const date = typeof period === 'string' ? new Date(period) : period;
```

**❌ DON'T:**
```typescript
// Don't assume Date object
const date = period.toISOString(); // ❌ Wrong - period might be string
```

### 4. Type Assertions

**✅ DO:**
```typescript
// Use type assertions for Prisma query results
const result = await prisma.$queryRawUnsafe(sql) as RevenueMetrics[];
```

**❌ DON'T:**
```typescript
// Don't use 'any'
const result: any = await prisma.$queryRawUnsafe(sql); // ❌ Wrong
```

---

## Maintenance

### When to Update Shared Types

1. **SQL Query Changes:** If a SQL query output changes, update the corresponding interface
2. **New Features:** When adding new dashboard features, add new interfaces
3. **Filter Changes:** If FilterParams needs new filter options, add them here

### Update Process

1. Update `shared/types.ts` with new/changed interfaces
2. Update this documentation
3. Update `docs/sql_dashboard_mapping.md` if SQL queries change
4. Verify backend compilation: `cd app/api && npm run build`
5. Update frontend types (when frontend is implemented)

### Version Control

- All changes to `shared/types.ts` should be reviewed carefully
- Breaking changes require coordination across all agents
- Document breaking changes in this file

---

## Related Documentation

- **SQL Queries:** `docs/sql_dashboard_mapping.md` - Maps SQL queries to interfaces
- **Backend Implementation:** `docs/agent2-status-and-handoffs.md` - Backend usage
- **Frontend Implementation:** (To be created) - Frontend usage
- **Architecture:** `docs/architecture.md` - Overall system architecture

---

## Summary

The `shared/types.ts` file is the **single source of truth** for all data types in the application. It ensures:

1. **Type Safety:** All layers use the same type definitions
2. **Consistency:** SQL outputs match TypeScript interfaces exactly
3. **Maintainability:** Changes to data structures happen in one place
4. **Documentation:** Types are self-documenting with clear field mappings

**Key Principle:** The database (SQL) defines the data shape. TypeScript interfaces mirror that shape exactly. No transformations or mappings should be needed beyond NULL handling and date conversion.

