/**
 * Shared TypeScript types for the Modular Monolith SaaS Dashboard
 * 
 * These types match the output of SQL queries in sql/queries/
 * All nullable fields use union types with null to ensure type safety
 */

/**
 * Revenue metrics from revenue_trends.sql
 * Period-based revenue trends by month, quarter, and year
 */
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

/**
 * Monthly metrics from monthly_metrics_summary.sql
 * Monthly summary of key business metrics
 */
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

/**
 * Activity heatmap data from analytics/heatmap_revenue_by_branch_month.sql
 * Branch-month activity matrix for heatmap visualization
 */
export interface ActivityHeatmap {
  branch_name: string;
  month: string; // Format: 'YYYY-MM'
  value: number | null; // Revenue or job count
}

/**
 * Sales radar chart data from analytics/customer_segmentation_radar.sql
 * Multi-dimensional customer metrics for radar chart visualization
 */
export interface SalesRadar {
  subject: string; // 'Lifetime Value' | 'Job Frequency' | 'Avg Job Value' | 'Customer Lifespan'
  value: number | null;
  full_mark: number | null; // Maximum value for scaling
}

/**
 * Sales person performance from revenue_by_sales_person.sql
 * Revenue and performance metrics per sales person
 */
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

/**
 * Branch performance from revenue_by_branch.sql
 * Revenue and performance metrics per branch
 */
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

/**
 * Query filter parameters for dynamic WHERE clause building
 * Used by FilterBuilder utility to safely inject filters into SQL queries
 */
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

/**
 * ETL script execution result
 * Returned by ETLService when executing Python scripts
 */
export interface ETLExecutionResult {
  success: boolean;
  exitCode: number;
  logs: string[];
  error?: string;
}

/**
 * API response wrapper for analytics endpoints
 * Standard response format for all analytics API endpoints
 */
export interface AnalyticsResponse<T> {
  data: T;
  metadata?: {
    count?: number;
    filters_applied?: FilterParams;
    timestamp?: string;
  };
  error?: string;
}

/**
 * KPI Card Props - For displaying key performance indicators
 */
export interface KPIProps {
  label: string;
  value: string | number;
  unit?: string;
  change?: number; // Percentage
  statusBadge?: "new" | "beta" | null;
  trend?: "up" | "down" | "neutral";
}

/**
 * Chart Data Point - Generic data point for charts
 */
export interface ChartDataPoint {
  name: string;
  value: number;
  value2?: number; // Secondary metric
  value3?: number; // Tertiary metric
  color?: string; // Optional color override
  [key: string]: any; // Allow flexible properties for generic charts
}

/**
 * View Type - All available views in the application
 */
export type ViewType = 
  | 'Overview' 
  | 'Revenue' 
  | 'Customers' 
  | 'Jobs' 
  | 'Sales Performance'
  | 'Leads'
  | 'Operational'
  | 'Geographic'
  | 'Profitability'
  | 'Forecasting'
  | 'Benchmarking';

/**
 * Time Range Enum
 */
export enum TimeRange {
  Daily = "Daily",
  Weekly = "Weekly",
  Monthly = "Monthly",
  Quarterly = "Quarterly",
  Yearly = "Yearly",
}

/**
 * Date Range Preset - Quick date range selections
 */
export type DateRangePreset = 'Today' | 'Last 7 Days' | 'Last 30 Days' | 'This Month' | 'Last Month' | 'Custom';

/**
 * Filter State - Client-side filter state
 */
export interface FilterState {
  dateRange: string;
  branch: string;
  salesPerson: string;
}

/**
 * Revenue Data - For revenue trend charts
 */
export interface RevenueData {
  period: string;
  revenue: number;
  previousRevenue: number;
  target?: number;
}

/**
 * Customer Segment - Customer segmentation data
 */
export interface CustomerSegment {
  segment: string;
  count: number;
  revenue: number;
}

/**
 * Job Metric - Job metrics over time
 */
export interface JobMetric {
  period: string;
  total: number;
  booked: number;
  closed: number;
}

/**
 * Sales Performer - Sales person performance data
 */
export interface SalesPerformer {
  id: string;
  name: string;
  revenue: number;
  deals: number;
  conversion: number;
  avatar?: string;
}

/**
 * Heatmap Point - For density heatmap visualizations
 */
export interface HeatmapPoint {
  x: string; // e.g., "Mon", "Tue"
  y: string; // e.g., "9am", "10am"
  value: number; // intensity 0-100
}

/**
 * Radar Metric - For radar chart visualizations
 */
export interface RadarMetric {
  subject: string;
  A: number; // Entity 1 (e.g., Agent)
  B: number; // Entity 2 (e.g., Team Avg)
  fullMark: number;
}

