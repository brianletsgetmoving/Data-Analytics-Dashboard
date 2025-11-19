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
    period: Date | string;
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
    month: Date | string;
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
    month: string;
    value: number | null;
}
/**
 * Sales radar chart data from analytics/customer_segmentation_radar.sql
 * Multi-dimensional customer metrics for radar chart visualization
 */
export interface SalesRadar {
    subject: string;
    value: number | null;
    full_mark: number | null;
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
    date_from?: string;
    date_to?: string;
    branch_id?: string;
    branch_name?: string;
    sales_person_id?: string;
    sales_person_name?: string;
    customer_id?: string;
    opportunity_status?: 'QUOTED' | 'BOOKED' | 'LOST' | 'CANCELLED' | 'CLOSED';
    lead_source_id?: string;
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
//# sourceMappingURL=types.d.ts.map