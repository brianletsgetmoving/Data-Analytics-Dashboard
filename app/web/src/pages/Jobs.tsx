import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { GradientAreaChart, DonutChart } from '@/components/charts';
import { CHART_COLORS } from '@/constants';
import { useMonthlyMetricsQuery, useJobStatusDistributionQuery, useJobTrendsQuery } from '@/hooks/useAnalytics';
import { transformMetricsToJobMetrics } from '@/utils/dataTransform';
import { useFilterStore } from '@/store/filterStore';
import { EmptyState } from '@/components/ui/EmptyState';

export default function Jobs() {
  const { filters } = useFilterStore();
  const { data: metricsData, isLoading: metricsLoading, error: metricsError } = useMonthlyMetricsQuery(filters);
  const { data: statusData, isLoading: statusLoading, error: statusError } = useJobStatusDistributionQuery(filters);
  const { data: trendsData, isLoading: trendsLoading } = useJobTrendsQuery(filters);
  
  // Use job trends if available, otherwise fall back to monthly metrics
  const jobTrends = trendsData?.data?.length 
    ? (trendsData.data as any[]).map((item: any) => ({
        period: item.period || item.month || 'Unknown',
        total: item.total_jobs || item.job_count || 0,
        booked: item.booked_jobs || 0,
        closed: item.closed_jobs || 0,
      }))
    : transformMetricsToJobMetrics(metricsData?.data || []);

  // Transform status distribution data
  const statusDist = (statusData?.data || []).map((item: any, index: number) => ({
    name: item.status || item.opportunity_status || item.name || 'Unknown',
    value: item.count || item.job_count || item.value || 0,
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));

  if (metricsError || statusError) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading job data"
        message={metricsError?.message || statusError?.message || 'Failed to load job data.'}
      />
    );
  }

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard label="Active Jobs" value="145" change={4.5} trend="up" />
        <KPICard label="Completion Rate" value="94%" change={1.2} trend="up" />
        <KPICard label="Avg Duration" value="14 days" change={-2} trend="down" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Job Volume Trends</h3>
        <GradientAreaChart 
          data={jobTrends} 
          xKey="period"
          areas={[
            { key: 'total', name: 'Total Jobs', color: CHART_COLORS[0] },
            { key: 'booked', name: 'Booked', color: CHART_COLORS[4] },
            { key: 'closed', name: 'Closed', color: CHART_COLORS[3] }
          ]}
          height={350}
          isLoading={metricsLoading || trendsLoading}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Status Distribution</h3>
          <DonutChart data={statusDist} height={300} isLoading={statusLoading} />
        </div>
        
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Recent Jobs</h3>
          <div className="space-y-4">
            {[1,2,3,4,5].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-700/50 rounded-lg border border-gray-100 dark:border-slate-700">
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-text-primary dark:text-gray-200">Moving Job #{2000+i}</span>
                  <span className="text-xs text-text-tertiary dark:text-gray-400">New York to Boston</span>
                </div>
                <span className="px-2 py-1 bg-white dark:bg-slate-700 rounded text-xs font-medium border border-gray-200 dark:border-slate-600 text-text-secondary dark:text-gray-300 shadow-sm">
                  In Progress
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

