import { useState } from 'react';
import { useRevenueTrendsQuery, useMonthlyMetricsQuery } from '@/hooks/useAnalytics';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import type { RevenueMetrics, MonthlyMetrics } from '@/shared/types';

function OverviewDashboard() {
  const [periodType, setPeriodType] = useState<'monthly' | 'quarterly' | 'yearly'>('monthly');
  
  const { data: revenueData, isLoading: revenueLoading, error: revenueError } = useRevenueTrendsQuery(periodType);
  const { data: metricsData, isLoading: metricsLoading, error: metricsError } = useMonthlyMetricsQuery();

  const formatCurrency = (value: number | null): string => {
    if (value === null) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (date: Date | string): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    if (periodType === 'monthly') {
      return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    } else if (periodType === 'quarterly') {
      const quarter = Math.floor(d.getMonth() / 3) + 1;
      return `Q${quarter} ${d.getFullYear()}`;
    } else {
      return d.getFullYear().toString();
    }
  };

  if (revenueError || metricsError) {
    return (
      <div className="neo-card">
        <p className="text-red-500">Error loading dashboard data</p>
      </div>
    );
  }

  const revenueChartData = revenueData?.data?.map((item: RevenueMetrics) => ({
    period: formatDate(item.period),
    revenue: item.revenue ?? 0,
    bookedRevenue: item.booked_revenue ?? 0,
    closedRevenue: item.closed_revenue ?? 0,
    changePercent: item.period_over_period_change_percent ?? 0,
  })) || [];

  const latestMetrics = metricsData?.data?.[metricsData.data.length - 1] as MonthlyMetrics | undefined;

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="neo-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold neo-text-primary">Revenue Trends</h2>
          <div className="flex gap-2">
            {(['monthly', 'quarterly', 'yearly'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setPeriodType(type)}
                className={`neo-button ${
                  periodType === type ? 'neo-button-primary' : ''
                }`}
                style={{ padding: '8px 16px', fontSize: '14px' }}
                aria-label={`Select ${type} period`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Revenue Chart */}
        {revenueLoading ? (
          <SkeletonLoader height={300} variant="card" />
        ) : (
          <div className="neo-glass" style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={revenueChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
                <XAxis 
                  dataKey="period" 
                  stroke="#4a4a4a"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#4a4a4a"
                  style={{ fontSize: '12px' }}
                  tickFormatter={(value) => `$${value / 1000}k`}
                />
                <Tooltip 
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid rgba(0,0,0,0.1)',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#6366f1" 
                  strokeWidth={2}
                  name="Total Revenue"
                />
                <Line 
                  type="monotone" 
                  dataKey="bookedRevenue" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  name="Booked Revenue"
                />
                <Line 
                  type="monotone" 
                  dataKey="closedRevenue" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  name="Closed Revenue"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricsLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <SkeletonLoader key={i} height={120} variant="card" />
          ))
        ) : (
          <>
            <div className="neo-card neo-card-hover">
              <h3 className="text-sm font-medium neo-text-secondary mb-2">Total Jobs</h3>
              <p className="text-2xl font-bold neo-text-primary">
                {latestMetrics?.total_jobs.toLocaleString() ?? '0'}
              </p>
            </div>
            <div className="neo-card neo-card-hover">
              <h3 className="text-sm font-medium neo-text-secondary mb-2">Total Revenue</h3>
              <p className="text-2xl font-bold neo-text-primary">
                {formatCurrency(latestMetrics?.total_revenue ?? null)}
              </p>
            </div>
            <div className="neo-card neo-card-hover">
              <h3 className="text-sm font-medium neo-text-secondary mb-2">Booking Rate</h3>
              <p className="text-2xl font-bold neo-text-primary">
                {latestMetrics?.booking_rate_percent?.toFixed(1) ?? '0'}%
              </p>
            </div>
            <div className="neo-card neo-card-hover">
              <h3 className="text-sm font-medium neo-text-secondary mb-2">Avg Job Value</h3>
              <p className="text-2xl font-bold neo-text-primary">
                {formatCurrency(latestMetrics?.avg_job_value ?? null)}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default OverviewDashboard;

