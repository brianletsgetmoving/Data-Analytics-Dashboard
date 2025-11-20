import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { GradientAreaChart } from '@/components/charts';
import { useProfitabilityQuery } from '@/hooks/useAnalytics';
import { useFilterStore } from '@/store/filterStore';
import { CHART_COLORS } from '@/constants';
import { EmptyState } from '@/components/ui/EmptyState';

export default function Profitability() {
  const { filters } = useFilterStore();
  const { data, isLoading, error } = useProfitabilityQuery(filters);

  if (error) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading profitability data"
        message={error.message || 'Failed to load profitability metrics.'}
      />
    );
  }

  // Transform data for charts
  const profitabilityData = (data?.data || []).map((item: any) => ({
    period: item.period || item.month || 'Unknown',
    profit: item.total_profit || item.profit || 0,
    margin: item.profit_margin || 0,
  }));

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Total Profit" value="$1.2M" change={18.5} trend="up" />
        <KPICard label="Profit Margin" value="24.8%" change={2.1} trend="up" />
        <KPICard label="ROI" value="156%" change={5.4} trend="up" />
        <KPICard label="Cost Efficiency" value="87%" change={-1.2} trend="down" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Profitability Trends</h3>
        <GradientAreaChart 
          data={profitabilityData}
          xKey="period"
          areas={[
            { key: 'profit', name: 'Profit', color: CHART_COLORS[2] },
            { key: 'margin', name: 'Margin %', color: CHART_COLORS[4] }
          ]}
          height={350}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

