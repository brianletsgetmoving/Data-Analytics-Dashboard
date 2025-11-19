import React from 'react';
import { KPICard } from '../KPICard';
import { MetricBarChart, DonutChart } from '../Charts';
import { api } from '../../lib/api';
import { CHART_COLORS } from '../../constants';

export const CustomersView: React.FC = () => {
  const demographics = api.getCustomerDemographics();
  const segments = api.getCustomerSegments();

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
          />
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Customer Segments</h3>
          <div className="flex items-center justify-center">
             <DonutChart data={segments} height={350} />
          </div>
        </div>
      </div>
    </div>
  );
};