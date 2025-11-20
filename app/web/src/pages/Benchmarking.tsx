import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { MetricBarChart } from '@/components/charts';
import { useBenchmarksQuery } from '@/hooks/useAnalytics';
import { useFilterStore } from '@/store/filterStore';
import { CHART_COLORS } from '@/constants';
import { EmptyState } from '@/components/ui/EmptyState';

export default function Benchmarking() {
  const { filters } = useFilterStore();
  const { data, isLoading, error } = useBenchmarksQuery(filters);

  if (error) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading benchmark data"
        message={error.message || 'Failed to load benchmark data.'}
      />
    );
  }

  // Transform benchmark data
  const benchmarkData = (data?.data || []).slice(0, 10).map((item: any) => ({
    name: item.entity_name || item.name || 'Unknown',
    value: item.performance_value || item.value || 0,
    benchmark: item.benchmark_value || item.benchmark || 100,
  }));

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Industry Avg" value="$850k" change={0} trend="neutral" />
        <KPICard label="Our Performance" value="$1.2M" change={41.2} trend="up" />
        <KPICard label="Market Share" value="12.5%" change={2.1} trend="up" />
        <KPICard label="Competitive Index" value="1.41x" change={0.15} trend="up" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Performance vs Benchmarks</h3>
        <MetricBarChart 
          data={benchmarkData} 
          xKey="name"
          bars={[
            { key: 'value', name: 'Performance', color: CHART_COLORS[0] },
            { key: 'benchmark', name: 'Benchmark', color: CHART_COLORS[4] }
          ]}
          height={350}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

