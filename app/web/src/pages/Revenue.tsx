import React, { useState } from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { GradientAreaChart, MetricBarChart } from '@/components/charts';
import { useRevenueTrendsQuery, useMonthlyMetricsQuery, useBranchPerformanceQuery } from '@/hooks/useAnalytics';
import { CHART_COLORS } from '@/constants';
import { transformRevenueMetricsToChartData, calculateKPIsFromMetrics, transformToChartDataPoint } from '@/utils/dataTransform';
import { useFilterStore } from '@/store/filterStore';
import { EmptyState } from '@/components/ui/EmptyState';

export default function Revenue() {
  const [periodType, setPeriodType] = useState<'monthly' | 'quarterly' | 'yearly'>('monthly');
  const { filters } = useFilterStore();
  const { data: revenueData, isLoading: revenueLoading, error: revenueError } = useRevenueTrendsQuery(periodType, filters);
  const { data: metricsData, error: metricsError } = useMonthlyMetricsQuery(filters);
  const { data: branchData } = useBranchPerformanceQuery(filters);

  const kpis = calculateKPIsFromMetrics(metricsData?.data || [], []);
  const revenueChartData = transformRevenueMetricsToChartData(revenueData?.data || [], []);
  
  // Transform branch data for revenue by segment chart
  const revenueBySegment = (branchData?.data || []).slice(0, 5).map((branch: any) => ({
    name: branch.branch_name || 'Unknown',
    value: branch.total_revenue || 0,
  }));

  if (revenueError || metricsError) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading revenue data"
        message={revenueError?.message || metricsError?.message || 'Failed to load revenue data. Please try again.'}
      />
    );
  }

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard label="Total Revenue" value={kpis[0]?.value || '$0'} change={kpis[0]?.change} trend={kpis[0]?.trend} />
        <KPICard label="Recurring Revenue" value="$450k" change={5.2} trend="up" />
        <KPICard label="Avg Deal Size" value="$12,500" change={-1.2} trend="down" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white">Revenue Performance</h3>
          <select
            value={periodType}
            onChange={(e) => setPeriodType(e.target.value as 'monthly' | 'quarterly' | 'yearly')}
            className="px-3 py-1.5 bg-gray-50 dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary"
          >
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <GradientAreaChart 
          data={revenueChartData} 
          xKey="period"
          areas={[
            { key: 'revenue', name: 'Actual', color: CHART_COLORS[0] },
            { key: 'previousRevenue', name: 'Previous', color: CHART_COLORS[4] }
          ]}
          height={400}
          isLoading={revenueLoading}
        />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Revenue by Branch</h3>
        <MetricBarChart 
          data={revenueBySegment}
          xKey="name"
          bars={[{ key: 'value', name: 'Revenue', color: CHART_COLORS[1] }]}
          height={300}
        />
      </div>
    </div>
  );
}

