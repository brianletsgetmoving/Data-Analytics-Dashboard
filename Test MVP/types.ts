
export interface KPIProps {
  label: string;
  value: string | number;
  unit?: string;
  change?: number; // Percentage
  statusBadge?: "new" | "beta" | null;
  trend?: "up" | "down" | "neutral";
}

export interface ChartDataPoint {
  name: string;
  value: number;
  value2?: number; // Secondary metric
  value3?: number; // Tertiary metric
  [key: string]: any; // Allow flexible properties for generic charts
}

export type ViewType = 'Overview' | 'Customers' | 'Jobs' | 'Revenue' | 'Sales Performance';

export enum TimeRange {
  Daily = "Daily",
  Weekly = "Weekly",
  Monthly = "Monthly",
  Quarterly = "Quarterly",
  Yearly = "Yearly",
}

export type DateRangePreset = 'Today' | 'Last 7 Days' | 'Last 30 Days' | 'This Month' | 'Last Month' | 'Custom';

export interface FilterState {
  dateRange: string;
  branch: string;
  salesPerson: string;
}

// Domain Specific Types
export interface RevenueData {
  period: string;
  revenue: number;
  previousRevenue: number;
  target: number;
}

export interface CustomerSegment {
  segment: string;
  count: number;
  revenue: number;
}

export interface JobMetric {
  period: string;
  total: number;
  booked: number;
  closed: number;
}

export interface SalesPerformer {
  id: string;
  name: string;
  revenue: number;
  deals: number;
  conversion: number;
  avatar?: string;
}

// Advanced Viz Types
export interface HeatmapPoint {
  x: string; // e.g., "Mon", "Tue"
  y: string; // e.g., "9am", "10am"
  value: number; // intensity 0-100
}

export interface RadarMetric {
  subject: string;
  A: number; // Entity 1 (e.g., Agent)
  B: number; // Entity 2 (e.g., Team Avg)
  fullMark: number;
}
