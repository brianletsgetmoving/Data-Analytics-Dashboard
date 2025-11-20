import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { MetricBarChart, DonutChart } from '@/components/charts';
import { useLeadConversionQuery, useLeadSourcesQuery } from '@/hooks/useAnalytics';
import { useFilterStore } from '@/store/filterStore';
import { CHART_COLORS } from '@/constants';
import { EmptyState } from '@/components/ui/EmptyState';
import { getNormalizedName, getNormalizedValue } from '@/utils/dataTransform';

export default function Leads() {
  const { filters } = useFilterStore();
  const { data: conversionData, isLoading: conversionLoading, error: conversionError } = useLeadConversionQuery(filters);
  const { data: sourcesData, isLoading: sourcesLoading } = useLeadSourcesQuery(filters);

  if (conversionError) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading lead data"
        message={conversionError.message || 'Failed to load lead metrics.'}
      />
    );
  }

  // Transform conversion funnel data
  const funnelData = (conversionData?.data || []).map((item: any, index: number) => ({
    name: item.stage || item.status || getNormalizedName(item, 'Unknown Stage'),
    value: item.count || item.leads || getNormalizedValue(item, 0),
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));

  // Transform sources data - SQL returns referral_source, affiliate_name
  const sourcesChartData = (sourcesData?.data || []).map((item: any, index: number) => ({
    name: item.referral_source || item.affiliate_name || item.lead_source || item.source || getNormalizedName(item, 'Unnamed Source'),
    value: item.total_leads || item.total_revenue || item.count || item.leads || getNormalizedValue(item, 0),
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Total Leads" value="1,234" change={12.5} trend="up" />
        <KPICard label="Conversion Rate" value="24.8%" change={5.2} trend="up" statusBadge="new" />
        <KPICard label="Response Time" value="2.4h" change={-1.2} trend="down" />
        <KPICard label="Lost Leads" value="342" change={-2.4} trend="down" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Lead Conversion Funnel</h3>
          <MetricBarChart 
            data={funnelData}
            xKey="name"
            bars={[{ key: 'value', name: 'Leads', color: CHART_COLORS[0] }]}
            layout="vertical"
            height={300}
            isLoading={conversionLoading}
          />
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Lead Sources</h3>
          <DonutChart 
            data={sourcesChartData}
            height={300}
            isLoading={sourcesLoading}
          />
        </div>
      </div>
    </div>
  );
}

