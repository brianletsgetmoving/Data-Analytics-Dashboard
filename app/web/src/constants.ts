import { ChartDataPoint, KPIProps } from '@/shared/types';

export const CHART_COLORS = [
  '#725BFF', // Primary Purple
  '#4CC9F0', // Cyan
  '#FF80B5', // Pink
  '#1CD6B1', // Teal
  '#FFB74A', // Orange
  '#28A9FF', // Blue
];

// Additional color palettes for different chart types
export const REVENUE_COLORS = {
  total: '#725BFF',
  booked: '#1CD6B1',
  closed: '#4CC9F0',
  target: '#FFB74A',
};

export const STATUS_COLORS = {
  booked: '#14B8A6',
  quoted: '#4CC9F0',
  pending: '#FACC15',
  lost: '#F87171',
  cancelled: '#94A3B8',
  closed: '#8B5CF6',
};

// View configuration
export const VIEW_CONFIG = {
  'Overview': {
    icon: 'LayoutDashboard',
    category: 'core',
    description: 'Welcome back, here\'s what\'s happening today.',
  },
  'Revenue': {
    icon: 'DollarSign',
    category: 'core',
    description: 'Track your financial performance and growth.',
  },
  'Customers': {
    icon: 'Users',
    category: 'core',
    description: 'Analyze customer demographics and behavior.',
  },
  'Jobs': {
    icon: 'Briefcase',
    category: 'core',
    description: 'Monitor job volume, status, and operational efficiency.',
  },
  'Sales Performance': {
    icon: 'TrendingUp',
    category: 'core',
    description: 'Evaluate agent performance and sales rankings.',
  },
  'Leads': {
    icon: 'Target',
    category: 'advanced',
    description: 'Track lead conversion and response times.',
  },
  'Operational': {
    icon: 'Settings',
    category: 'advanced',
    description: 'Monitor operational efficiency and resource utilization.',
  },
  'Geographic': {
    icon: 'MapPin',
    category: 'advanced',
    description: 'Analyze geographic patterns and coverage.',
  },
  'Profitability': {
    icon: 'PiggyBank',
    category: 'strategic',
    description: 'Evaluate profitability and ROI metrics.',
  },
  'Forecasting': {
    icon: 'TrendingUp',
    category: 'strategic',
    description: 'View revenue and growth forecasts.',
  },
  'Benchmarking': {
    icon: 'BarChart3',
    category: 'strategic',
    description: 'Compare performance against benchmarks.',
  },
} as const;

