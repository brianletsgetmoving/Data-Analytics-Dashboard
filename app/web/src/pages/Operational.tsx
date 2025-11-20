import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { MetricBarChart } from '@/components/charts';
import { useOperationalEfficiencyQuery } from '@/hooks/useAnalytics';
import { useFilterStore } from '@/store/filterStore';
import { CHART_COLORS } from '@/constants';
import { EmptyState } from '@/components/ui/EmptyState';

export default function Operational() {
  const { filters } = useFilterStore();
  const { data, isLoading, error } = useOperationalEfficiencyQuery(filters);

  if (error) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading operational data"
        message={error.message || 'Failed to load operational metrics.'}
      />
    );
  }

  // Transform data for charts
  const efficiencyData = (data?.data || []).slice(0, 10).map((item: any) => ({
    name: item.branch_name || item.period || 'Unknown',
    value: item.efficiency_score || item.utilization_rate || 0,
  }));

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Scheduling Efficiency" value="87%" change={2.1} trend="up" />
        <KPICard label="Capacity Utilization" value="72%" change={-1.5} trend="down" />
        <KPICard label="Avg Job Duration" value="14 days" change={-0.8} trend="down" />
        <KPICard label="Resource Utilization" value="68%" change={3.2} trend="up" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Operational Efficiency</h3>
        <MetricBarChart 
          data={efficiencyData}
          xKey="name"
          bars={[{ key: 'value', name: 'Efficiency Score', color: CHART_COLORS[0] }]}
          height={350}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

