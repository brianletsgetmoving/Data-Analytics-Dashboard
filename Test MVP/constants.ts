import { ChartDataPoint, KPIProps } from './types';

export const CHART_COLORS = [
  '#725BFF', // Primary Purple
  '#4CC9F0', // Cyan
  '#FF80B5', // Pink
  '#1CD6B1', // Teal
  '#FFB74A', // Orange
  '#28A9FF', // Blue
];

export const MOCK_REVENUE_DATA: ChartDataPoint[] = [
  { name: 'Jan', value: 4000, value2: 2400 },
  { name: 'Feb', value: 3000, value2: 1398 },
  { name: 'Mar', value: 9800, value2: 2000 },
  { name: 'Apr', value: 6000, value2: 3908 },
  { name: 'May', value: 4890, value2: 4800 },
  { name: 'Jun', value: 8390, value2: 3800 },
  { name: 'Jul', value: 12490, value2: 4300 },
  { name: 'Aug', value: 10000, value2: 6400 },
  { name: 'Sep', value: 11500, value2: 7800 },
  { name: 'Oct', value: 9000, value2: 5900 },
  { name: 'Nov', value: 14000, value2: 9000 },
  { name: 'Dec', value: 16000, value2: 11000 },
];

export const MOCK_SOURCE_DATA: ChartDataPoint[] = [
  { name: 'Referral', value: 45 },
  { name: 'Google Ads', value: 25 },
  { name: 'Direct', value: 20 },
  { name: 'Social', value: 10 },
];

export const MOCK_SALES_PERFORMANCE: ChartDataPoint[] = [
  { name: 'M. Thompson', value: 120000 },
  { name: 'S. Rodriguez', value: 98000 },
  { name: 'K. Chen', value: 86000 },
  { name: 'J. Smith', value: 75000 },
  { name: 'A. Patel', value: 65000 },
];

export const KPI_DATA: KPIProps[] = [
  { label: "Total Revenue", value: "$1.2M", change: 12.5, trend: "up" },
  { label: "Active Leads", value: "342", change: -2.4, trend: "down" },
  { label: "Booking Rate", value: "24.8%", change: 5.2, trend: "up", statusBadge: "new" },
  { label: "Avg. Job Value", value: "$1,850", change: 0.8, trend: "up" },
];
