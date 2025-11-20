import type {
  RevenueMetrics,
  MonthlyMetrics,
  ActivityHeatmap,
  SalesRadar,
  SalesPersonPerformance,
  RevenueData,
  ChartDataPoint,
  HeatmapPoint,
  RadarMetric,
  SalesPerformer,
  JobMetric,
  KPIProps,
} from '@/shared/types';

/**
 * Field name normalization mappings
 * Maps SQL column names to frontend expected field names
 */
const FIELD_NAME_MAPPINGS: Record<string, string[]> = {
  lead_source_name: ['referral_source', 'affiliate_name', 'lead_source', 'source'],
  name: ['referral_source', 'affiliate_name', 'lead_source', 'sales_person_name', 'branch_name', 'city', 'origin_city'],
  city: ['origin_city', 'city', 'destination_city'],
  origin_city: ['origin_city', 'city'],
  count: ['total_leads', 'total_jobs', 'job_count', 'customer_count', 'count'],
  value: ['total_revenue', 'total_leads', 'total_jobs', 'revenue', 'value'],
  total_revenue: ['total_revenue', 'revenue', 'total_actual_cost', 'total_estimated_cost'],
};

/**
 * Normalize field names from SQL results to frontend expected names
 * @param data - Raw data object from API
 * @param fieldName - Expected field name in frontend
 * @param fallback - Fallback value if field is not found
 * @returns Normalized field value
 */
export function normalizeFieldName(
  data: Record<string, unknown>,
  fieldName: string,
  fallback: string | number = ''
): string | number {
  // Direct match first
  if (data[fieldName] !== undefined && data[fieldName] !== null) {
    return data[fieldName] as string | number;
  }

  // Check mapped alternatives
  const alternatives = FIELD_NAME_MAPPINGS[fieldName] || [];
  for (const alt of alternatives) {
    if (data[alt] !== undefined && data[alt] !== null) {
      if (import.meta.env.DEV) {
        console.warn(
          `[Field Normalization] Using alternative field "${alt}" for "${fieldName}"`,
          data
        );
      }
      return data[alt] as string | number;
    }
  }

  // Log warning in development if field is missing
  if (import.meta.env.DEV && fallback === '') {
    console.warn(
      `[Field Normalization] Field "${fieldName}" not found in data:`,
      Object.keys(data),
      data
    );
  }

  return fallback;
}

/**
 * Get normalized name field from data object
 * Handles common name field variations
 */
export function getNormalizedName(
  data: Record<string, unknown>,
  fallback: string = 'Unknown'
): string {
  const name = normalizeFieldName(data, 'name', fallback);
  return typeof name === 'string' ? name : String(name || fallback);
}

/**
 * Get normalized count/value field from data object
 * Handles common count/value field variations
 */
export function getNormalizedValue(
  data: Record<string, unknown>,
  fallback: number = 0
): number {
  const value = normalizeFieldName(data, 'value', fallback);
  return typeof value === 'number' ? value : Number(value || fallback);
}

/**
 * Transform RevenueMetrics to RevenueData format for charts
 */
export function transformRevenueMetricsToChartData(
  metrics: RevenueMetrics[],
  previousPeriodMetrics?: RevenueMetrics[]
): RevenueData[] {
  return metrics.map((metric, index) => {
    const previous = previousPeriodMetrics?.[index];
    return {
      period: typeof metric.period === 'string' 
        ? new Date(metric.period).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
        : metric.period.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
      revenue: metric.revenue ?? 0,
      previousRevenue: previous?.revenue ?? metric.previous_period_revenue ?? 0,
      target: 0, // Can be calculated or passed separately
    };
  });
}

/**
 * Transform SalesPersonPerformance to SalesPerformer format
 */
export function transformSalesPersonToPerformer(
  performance: SalesPersonPerformance[],
  startIndex: number = 0
): SalesPerformer[] {
  return performance.map((sp, index) => {
    const name = sp.sales_person_name || 'Unknown';
    
    // Log warning in development if name is missing
    if (import.meta.env.DEV && !sp.sales_person_name) {
      console.warn(
        `[SalesPerson Transform] Missing sales_person_name at index ${index}:`,
        sp
      );
    }
    
    return {
      id: `sp-${startIndex + index}`,
      name,
      revenue: sp.total_revenue ?? 0,
      deals: sp.total_jobs ?? 0,
      conversion: sp.booked_jobs && sp.booked_jobs > 0 
        ? Math.round((sp.closed_jobs / sp.booked_jobs) * 100)
        : 0,
    };
  });
}

/**
 * Transform ActivityHeatmap to HeatmapPoint format
 */
export function transformHeatmapToPoints(
  heatmap: ActivityHeatmap[],
  xAxisKey: 'branch_name' | 'month' = 'month',
  yAxisKey: 'month' | 'branch_name' = 'branch_name'
): HeatmapPoint[] {
  return heatmap.map((item) => ({
    x: item[xAxisKey] || '',
    y: item[yAxisKey] || '',
    value: item.value ?? 0,
  }));
}

/**
 * Transform SalesRadar to RadarMetric format
 */
export function transformRadarData(radar: SalesRadar[]): RadarMetric[] {
  return radar.map((item) => ({
    subject: item.subject,
    A: item.value ?? 0,
    B: item.full_mark ?? 100,
    fullMark: item.full_mark ?? 100,
  }));
}

/**
 * Calculate KPIs from MonthlyMetrics
 */
export function calculateKPIsFromMetrics(
  metrics: MonthlyMetrics[],
  previousMetrics?: MonthlyMetrics[]
): KPIProps[] {
  const latest = metrics[metrics.length - 1];
  const previous = previousMetrics?.[previousMetrics.length - 1];

  if (!latest) {
    return [
      { label: 'Total Revenue', value: '$0', change: 0, trend: 'neutral' },
      { label: 'Active Jobs', value: '0', change: 0, trend: 'neutral' },
      { label: 'Booking Rate', value: '0%', change: 0, trend: 'neutral' },
      { label: 'Avg. Job Value', value: '$0', change: 0, trend: 'neutral' },
    ];
  }

  const formatCurrency = (value: number | null): string => {
    if (value === null || value === 0) return '$0';
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}k`;
    return `$${value.toFixed(0)}`;
  };

  const calculateChange = (current: number | null, previous: number | null): number => {
    if (!current || !previous || previous === 0) return 0;
    return Math.round(((current - previous) / previous) * 100 * 10) / 10;
  };

  const getTrend = (change: number): 'up' | 'down' | 'neutral' => {
    if (change > 0) return 'up';
    if (change < 0) return 'down';
    return 'neutral';
  };

  const revenueChange = calculateChange(latest.total_revenue, previous?.total_revenue ?? null);
  const jobsChange = calculateChange(latest.total_jobs, previous?.total_jobs ?? 0);
  const bookingRateChange = calculateChange(
    latest.booking_rate_percent,
    previous?.booking_rate_percent ?? null
  );
  const avgJobValueChange = calculateChange(
    latest.avg_job_value,
    previous?.avg_job_value ?? null
  );

  return [
    {
      label: 'Total Revenue',
      value: formatCurrency(latest.total_revenue),
      change: Math.abs(revenueChange),
      trend: getTrend(revenueChange),
    },
    {
      label: 'Active Jobs',
      value: latest.total_jobs.toLocaleString(),
      change: Math.abs(jobsChange),
      trend: getTrend(jobsChange),
    },
    {
      label: 'Booking Rate',
      value: `${(latest.booking_rate_percent ?? 0).toFixed(1)}%`,
      change: Math.abs(bookingRateChange),
      trend: getTrend(bookingRateChange),
      statusBadge: bookingRateChange > 5 ? 'new' : null,
    },
    {
      label: 'Avg. Job Value',
      value: formatCurrency(latest.avg_job_value),
      change: Math.abs(avgJobValueChange),
      trend: getTrend(avgJobValueChange),
    },
  ];
}

/**
 * Transform data to ChartDataPoint format
 */
export function transformToChartDataPoint(
  data: Array<{ name: string; value: number; color?: string }>
): ChartDataPoint[] {
  return data.map((item) => ({
    name: item.name,
    value: item.value,
    color: item.color,
  }));
}

/**
 * Transform MonthlyMetrics to JobMetric format
 */
export function transformMetricsToJobMetrics(metrics: MonthlyMetrics[]): JobMetric[] {
  return metrics.map((metric) => ({
    period: typeof metric.month === 'string'
      ? new Date(metric.month).toLocaleDateString('en-US', { month: 'short' })
      : metric.month.toLocaleDateString('en-US', { month: 'short' }),
    total: metric.total_jobs,
    booked: metric.booked_jobs,
    closed: metric.closed_jobs,
  }));
}

/**
 * Format period for display based on period type
 */
export function formatPeriod(
  period: Date | string,
  periodType: 'monthly' | 'quarterly' | 'yearly'
): string {
  const date = typeof period === 'string' ? new Date(period) : period;
  
  if (periodType === 'monthly') {
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  } else if (periodType === 'quarterly') {
    const quarter = Math.floor(date.getMonth() / 3) + 1;
    return `Q${quarter} ${date.getFullYear()}`;
  } else {
    return date.getFullYear().toString();
  }
}

