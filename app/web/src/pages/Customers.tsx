import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { MetricBarChart, DonutChart } from '@/components/charts';
import { CHART_COLORS } from '@/constants';
import { useFilterStore } from '@/store/filterStore';
import { useCustomerDemographicsQuery, useCustomerSegmentsQuery } from '@/hooks/useAnalytics';
import { EmptyState } from '@/components/ui/EmptyState';
import { getNormalizedName, getNormalizedValue } from '@/utils/dataTransform';

export default function Customers() {
  const { filters } = useFilterStore();
  const { data: demographicsData, isLoading: demographicsLoading, error: demographicsError } = useCustomerDemographicsQuery(filters);
  const { data: segmentsData, isLoading: segmentsLoading, error: segmentsError } = useCustomerSegmentsQuery(filters);

  // Transform demographics data
  const demographics = (demographicsData?.data || []).slice(0, 6).map((item: any) => ({
    name: item.origin_city || item.city || getNormalizedName(item, 'Unknown City'),
    value: item.customer_count || item.count || getNormalizedValue(item, 0),
  }));

  // Transform segments data
  const segments = (segmentsData?.data || []).map((item: any, index: number) => ({
    name: item.segment || item.segment_name || getNormalizedName(item, 'Unknown Segment'),
    value: item.revenue || item.total_revenue || getNormalizedValue(item, 0),
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));

  if (demographicsError || segmentsError) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading customer data"
        message={demographicsError?.message || segmentsError?.message || 'Failed to load customer data.'}
      />
    );
  }

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Total Customers" value="2,543" change={8.4} trend="up" />
        <KPICard label="New This Month" value="124" change={12.1} trend="up" statusBadge="new" />
        <KPICard label="Churn Rate" value="1.2%" change={-0.5} trend="down" />
        <KPICard label="NPS Score" value="72" change={2.0} trend="up" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Customer Geography</h3>
          <MetricBarChart 
            data={demographics} 
            xKey="name"
            bars={[{ key: 'value', name: 'Customers', color: CHART_COLORS[3] }]}
            height={350}
            isLoading={demographicsLoading}
          />
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Customer Segments</h3>
          <DonutChart data={segments} height={350} isLoading={segmentsLoading} />
        </div>
      </div>
    </div>
  );
}

