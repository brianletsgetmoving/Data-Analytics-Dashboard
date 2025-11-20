import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { GradientAreaChart } from '@/components/charts';
import { useForecastQuery } from '@/hooks/useAnalytics';
import { useFilterStore } from '@/store/filterStore';
import { CHART_COLORS } from '@/constants';
import { EmptyState } from '@/components/ui/EmptyState';

export default function Forecasting() {
  const { filters } = useFilterStore();
  const { data, isLoading, error } = useForecastQuery(filters);

  if (error) {
    return (
      <EmptyState
        type="no-data"
        title="Error loading forecast data"
        message={error.message || 'Failed to load forecast data.'}
      />
    );
  }

  // Transform forecast data
  const forecastData = (data?.data || []).map((item: any) => ({
    period: item.period || item.month || 'Unknown',
    revenue: item.actual_revenue || item.revenue || 0,
    forecast: item.forecasted_revenue || item.forecast || 0,
  }));

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Revenue Forecast" value="$2.4M" change={12.5} trend="up" />
        <KPICard label="Job Volume Forecast" value="1,450" change={8.2} trend="up" />
        <KPICard label="Growth Rate" value="15.2%" change={2.1} trend="up" />
        <KPICard label="Forecast Accuracy" value="94%" change={1.5} trend="up" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Revenue Forecast</h3>
        <GradientAreaChart 
          data={forecastData} 
          xKey="period"
          areas={[
            { key: 'revenue', name: 'Actual', color: CHART_COLORS[0] },
            { key: 'forecast', name: 'Forecast', color: CHART_COLORS[4] }
          ]}
          height={350}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

