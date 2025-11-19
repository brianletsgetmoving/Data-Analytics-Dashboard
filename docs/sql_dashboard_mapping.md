# SQL Dashboard Mapping

This document maps SQL query files to their corresponding dashboard features and TypeScript interfaces.

## Overview Dashboard

### Revenue Trends
**Component:** `OverviewDashboard.tsx` - Revenue trend line chart  
**TypeScript Interface:** `RevenueMetrics`  
**SQL Query:** `sql/queries/revenue_trends.sql`

**Description:** Displays revenue trends by period (monthly, quarterly, yearly) with period-over-period change percentages.

**Output Columns:**
- `period_type` (text: 'monthly'|'quarterly'|'yearly')
- `period` (timestamp)
- `job_count` (integer)
- `revenue` (numeric, nullable)
- `booked_revenue` (numeric, nullable)
- `closed_revenue` (numeric, nullable)
- `previous_period_revenue` (numeric, nullable)
- `period_over_period_change_percent` (numeric, nullable)

**Filter Support:** Filtered by `period_type` query parameter in API endpoint.

---

### Monthly Metrics Summary
**Component:** `OverviewDashboard.tsx` - KPI cards  
**TypeScript Interface:** `MonthlyMetrics`  
**SQL Query:** `sql/queries/monthly_metrics_summary.sql`

**Description:** Monthly KPI summary cards showing total jobs, revenue, booking rates, and active entities.

**Output Columns:**
- `month` (timestamp)
- `year` (integer)
- `month_number` (integer)
- `total_jobs` (integer)
- `quoted_jobs` (integer)
- `booked_jobs` (integer)
- `closed_jobs` (integer)
- `lost_jobs` (integer)
- `cancelled_jobs` (integer)
- `total_revenue` (numeric, nullable)
- `avg_job_value` (numeric, nullable)
- `unique_customers` (integer)
- `active_branches` (integer)
- `active_sales_people` (integer)
- `booking_rate_percent` (numeric, nullable)

**Filter Support:** Optional date range filters (`dateFrom`, `dateTo`).

---

### Average Job Value
**Component:** `OverviewDashboard.tsx` - Average job value metric  
**SQL Query:** `sql/queries/average_job_value.sql`

**Description:** Average job value overall and by various dimensions (branch, sales person, job type).

**Output Columns:**
- `dimension` (text: 'overall'|'branch'|'sales_person'|'job_type')
- `dimension_value` (text, nullable)
- `job_count` (integer)
- `avg_job_value` (numeric)
- `median_job_value` (numeric)

**Note:** This query is not yet mapped to a TypeScript interface in `shared/types.ts`. May need to be added if used in frontend.

---

## Activity Heatmap Dashboard

### Branch-Month Activity Heatmap
**Component:** `ActivityHeatmap.tsx`  
**TypeScript Interface:** `ActivityHeatmap`  
**SQL Query:** `sql/queries/analytics/heatmap_revenue_by_branch_month.sql`

**Description:** Temporal activity visualization showing branch-month revenue/job matrix.

**Output Columns:**
- `branch_name` (text)
- `month` (text format 'YYYY-MM')
- `value` (numeric, nullable - revenue or job count)

**Filter Support:** 
- Dynamic filter injection point marked with `-- Filters are injected here dynamically`
- Supports: `branchId`, `dateFrom`, `dateTo`
- FilterBuilder utility injects filters safely at the marked location

**Special Notes:**
- Query has a filter injection point that requires special handling in QueryService
- The `value` column can represent either revenue or job count depending on the dimension parameter

---

## Performance Radar Chart Dashboard

### Customer Segmentation Radar
**Component:** `PerformanceRadar.tsx`  
**TypeScript Interface:** `SalesRadar`  
**SQL Query:** `sql/queries/analytics/customer_segmentation_radar.sql`

**Description:** Multi-dimensional customer metrics for radar chart visualization.

**Output Columns:**
- `subject` (text: 'Lifetime Value'|'Job Frequency'|'Avg Job Value'|'Customer Lifespan')
- `value` (numeric, nullable)
- `full_mark` (numeric, nullable - maximum value for scaling)

**Filter Support:**
- Dynamic filter injection point
- Supports: `dateFrom`, `dateTo`, `customer_id`
- FilterBuilder utility injects filters safely

**Special Notes:**
- The `subject` column determines the axis label on the radar chart
- The `full_mark` column is used to scale the radar chart axes
- Query aggregates customer metrics into radar chart format

---

### Sales Person Performance (for Radar)
**Component:** `PerformanceRadar.tsx` (when dimension='salesperson')  
**TypeScript Interface:** `SalesRadar` (transformed)  
**SQL Query:** `sql/queries/revenue_by_sales_person.sql`

**Description:** Sales person performance metrics aggregated into radar chart format.

**Base Query Output Columns:**
- `sales_person_name` (text, nullable)
- `total_jobs` (integer)
- `total_revenue` (numeric, nullable)
- `avg_job_value` (numeric, nullable)
- `booked_revenue` (numeric, nullable)
- `closed_revenue` (numeric, nullable)
- `booked_jobs` (integer)
- `closed_jobs` (integer)
- `avg_booked_value` (numeric, nullable)
- `branches_worked` (integer)
- `unique_customers` (integer)

**Note:** This query output must be transformed into `SalesRadar[]` format by the backend API. The transformation logic should map sales person metrics to radar chart dimensions.

---

### Branch Performance (for Radar)
**Component:** `PerformanceRadar.tsx` (when dimension='branch')  
**TypeScript Interface:** `SalesRadar` (transformed)  
**SQL Query:** `sql/queries/revenue_by_branch.sql`

**Description:** Branch performance metrics aggregated into radar chart format.

**Base Query Output Columns:**
- `branch_name` (text, nullable)
- `total_jobs` (integer)
- `total_revenue` (numeric, nullable)
- `avg_job_value` (numeric, nullable)
- `booked_revenue` (numeric, nullable)
- `closed_revenue` (numeric, nullable)
- `booked_jobs` (integer)
- `closed_jobs` (integer)
- `avg_booked_value` (numeric, nullable)
- `avg_closed_value` (numeric, nullable)

**Note:** This query output must be transformed into `SalesRadar[]` format by the backend API. The transformation logic should map branch metrics to radar chart dimensions.

---

## Sales Person Performance Dashboard

### Sales Person Performance Table
**Component:** `SalesPersonPerformanceTable.tsx` (to be created)  
**TypeScript Interface:** `SalesPersonPerformance`  
**SQL Query:** `sql/queries/revenue_by_sales_person.sql`

**Description:** Sales person performance metrics table/list view.

**Output Columns:**
- `sales_person_name` (text, nullable)
- `total_jobs` (integer)
- `total_revenue` (numeric, nullable)
- `avg_job_value` (numeric, nullable)
- `booked_revenue` (numeric, nullable)
- `closed_revenue` (numeric, nullable)
- `booked_jobs` (integer)
- `closed_jobs` (integer)
- `avg_booked_value` (numeric, nullable)
- `branches_worked` (integer)
- `unique_customers` (integer)

**Filter Support:** Optional filters: `dateFrom`, `dateTo`, `salesPersonId`

---

## Branch Performance Dashboard

### Branch Performance Table
**Component:** `BranchPerformanceTable.tsx` (to be created)  
**TypeScript Interface:** `BranchPerformance`  
**SQL Query:** `sql/queries/revenue_by_branch.sql`

**Description:** Branch performance metrics table/list view.

**Output Columns:**
- `branch_name` (text, nullable)
- `total_jobs` (integer)
- `total_revenue` (numeric, nullable)
- `avg_job_value` (numeric, nullable)
- `booked_revenue` (numeric, nullable)
- `closed_revenue` (numeric, nullable)
- `booked_jobs` (integer)
- `closed_jobs` (integer)
- `avg_booked_value` (numeric, nullable)
- `avg_closed_value` (numeric, nullable)

**Filter Support:** Optional filters: `dateFrom`, `dateTo`, `branchId`

---

## Query Filter Injection Points

Some SQL queries have dynamic filter injection points that require special handling:

### Queries with Filter Injection Points:
1. **`analytics/heatmap_revenue_by_branch_month.sql`**
   - Injection point: `-- Filters are injected here dynamically` (line 18)
   - Supported filters: `branchId`, `dateFrom`, `dateTo`

2. **`analytics/customer_segmentation_radar.sql`**
   - Injection point: `-- Filters are injected here dynamically` (line 25)
   - Supported filters: `dateFrom`, `dateTo`, `customer_id`

### FilterBuilder Utility Requirements:
- The backend `FilterBuilder` utility must:
  - Read SQL files and locate filter injection points
  - Safely inject WHERE clause conditions using parameterized queries
  - Prevent SQL injection by using parameterized queries only
  - Handle NULL values correctly (use `IS NULL` checks)

---

## Type Safety Requirements

All SQL queries must match their TypeScript interfaces exactly:

1. **Column Names:** SQL column names must match TypeScript interface property names exactly (case-sensitive)
2. **Data Types:** 
   - PostgreSQL `numeric` → TypeScript `number | null`
   - PostgreSQL `text` → TypeScript `string | null` (if nullable) or `string`
   - PostgreSQL `timestamp` → TypeScript `Date | string`
   - PostgreSQL `integer` → TypeScript `number`
3. **Nullable Fields:** All nullable SQL columns must use `| null` union types in TypeScript
4. **No Application-Level Mapping:** The SQL output must match the interface shape exactly - no transformation should be required

---

## Implementation Status

| Dashboard Feature | SQL Query | TypeScript Interface | Backend Endpoint | Frontend Component | Status |
|------------------|-----------|---------------------|------------------|-------------------|--------|
| Revenue Trends | `revenue_trends.sql` | `RevenueMetrics` | Not implemented | Not implemented | Pending |
| Monthly Metrics | `monthly_metrics_summary.sql` | `MonthlyMetrics` | Not implemented | Not implemented | Pending |
| Activity Heatmap | `analytics/heatmap_revenue_by_branch_month.sql` | `ActivityHeatmap` | Not implemented | Not implemented | Pending |
| Customer Radar | `analytics/customer_segmentation_radar.sql` | `SalesRadar` | Not implemented | Not implemented | Pending |
| Sales Person Performance | `revenue_by_sales_person.sql` | `SalesPersonPerformance` | Not implemented | Not implemented | Pending |
| Branch Performance | `revenue_by_branch.sql` | `BranchPerformance` | Not implemented | Not implemented | Pending |

---

## Notes for Backend Implementation

1. **Filter Injection:** Queries with filter injection points require the `FilterBuilder` utility to safely inject WHERE clause conditions.

2. **Radar Chart Transformation:** The `revenue_by_sales_person.sql` and `revenue_by_branch.sql` queries need to be transformed into `SalesRadar[]` format when used for radar charts. This transformation should happen in the backend API endpoint.

3. **Period Type Filtering:** The `revenue_trends.sql` query returns all period types (monthly, quarterly, yearly) in a single result set. The backend must filter by `period_type` based on the query parameter.

4. **NULL Handling:** All SQL queries use `COALESCE` to handle NULL values safely. The backend must ensure NULL values are preserved (not converted to 0) to match TypeScript interfaces.

---

## Notes for Frontend Implementation

1. **Date Formatting:** PostgreSQL timestamps are returned as strings. Frontend should parse them as `Date` objects or use string formatting utilities.

2. **Loading States:** All dashboard components should show `SkeletonLoader` components while data is loading.

3. **Error Handling:** All API calls should handle errors gracefully and display user-friendly error messages.

4. **Type Safety:** All components must use the exact TypeScript interfaces from `shared/types.ts` - no custom types or transformations.

