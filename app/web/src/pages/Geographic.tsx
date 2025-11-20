import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { MetricBarChart } from '@/components/charts';
import { useGeographicCoverageQuery } from '@/hooks/useAnalytics';
import { useFilterStore } from '@/store/filterStore';
import { CHART_COLORS } from '@/constants';
import { EmptyState } from '@/components/ui/EmptyState';
import { getNormalizedName, getNormalizedValue } from '@/utils/dataTransform';

export default function Geographic() {
  const { filters } = useFilterStore();
  const { data, isLoading, error } = useGeographicCoverageQuery(filters);

  if (error) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading geographic data"
        message={error.message || 'Failed to load geographic metrics.'}
      />
    );
  }

  // Transform geographic data
  const originCities = (data?.data || []).slice(0, 10).map((item: any) => ({
    name: item.origin_city || item.city || getNormalizedName(item, 'Unknown City'),
    value: item.job_count || item.count || getNormalizedValue(item, 0),
  }));

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Total Cities" value="156" change={8.2} trend="up" />
        <KPICard label="Active Routes" value="342" change={12.5} trend="up" />
        <KPICard label="Coverage Area" value="48 states" change={0} trend="neutral" />
        <KPICard label="Geographic Revenue" value="$2.1M" change={15.3} trend="up" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Top Origin Cities</h3>
          <MetricBarChart 
            data={originCities} 
            xKey="name"
            bars={[{ key: 'value', name: 'Jobs', color: CHART_COLORS[0] }]}
            height={350}
            isLoading={isLoading}
          />
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Geographic Coverage</h3>
          <p className="text-sm text-text-secondary dark:text-gray-400">Map visualization coming soon...</p>
        </div>
      </div>
    </div>
  );
}

