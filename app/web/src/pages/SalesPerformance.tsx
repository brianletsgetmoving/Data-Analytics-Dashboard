import React from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { MetricBarChart, SkillRadarChart } from '@/components/charts';
import { DataTable, Column } from '@/components/tables/DataTable';
import { CHART_COLORS } from '@/constants';
import { useSalesPersonPerformanceQuery, useRadarChartQuery } from '@/hooks/useAnalytics';
import { transformSalesPersonToPerformer, transformRadarData } from '@/utils/dataTransform';
import { useFilterStore } from '@/store/filterStore';
import { SalesPersonPerformance } from '@/shared/types';

export default function SalesPerformance() {
  const { filters } = useFilterStore();
  const { data: salesData, isLoading: salesLoading } = useSalesPersonPerformanceQuery(filters);
  const { data: radarData, isLoading: radarLoading } = useRadarChartQuery('salesperson', filters);

  const performers = transformSalesPersonToPerformer(salesData?.data || []).slice(0, 5);
  const radarMetrics = transformRadarData(radarData?.data || []);

  const columns: Column<SalesPersonPerformance>[] = [
    { key: 'sales_person_name', header: 'Sales Person', sortable: true },
    { key: 'total_jobs', header: 'Total Jobs', sortable: true, align: 'right' },
    { 
      key: 'total_revenue', 
      header: 'Revenue', 
      sortable: true, 
      align: 'right',
      render: (value) => value ? `$${Number(value).toLocaleString()}` : '$0'
    },
    { 
      key: 'avg_job_value', 
      header: 'Avg Job Value', 
      sortable: true, 
      align: 'right',
      render: (value) => value ? `$${Number(value).toLocaleString()}` : '$0'
    },
    { key: 'booked_jobs', header: 'Booked', sortable: true, align: 'right' },
    { key: 'closed_jobs', header: 'Closed', sortable: true, align: 'right' },
  ];

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Total Sales" value="$854k" change={15.2} trend="up" />
        <KPICard label="Deals Closed" value="142" change={8.5} trend="up" />
        <KPICard label="Avg Commission" value="$3,200" change={2.4} trend="up" />
        <KPICard label="Pipeline Value" value="$2.1M" change={-1.5} trend="down" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DataTable
            data={salesData?.data || []}
            columns={columns}
            isLoading={salesLoading}
            exportable
            searchable
            pageSize={10}
            onRowClick={(row) => {
              // Could navigate to detail page or show drill-down
              console.log('Row clicked:', row);
            }}
          />
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-4">Team Skill Gap</h3>
          <p className="text-xs text-text-secondary dark:text-gray-300 mb-6">Comparing top agent avg vs team avg</p>
          <SkillRadarChart data={radarMetrics} height={300} isLoading={radarLoading} />
        </div>
      </div>
    </div>
  );
}

