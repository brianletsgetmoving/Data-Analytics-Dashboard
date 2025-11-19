import React, { useState } from 'react';
import { KPICard } from '../KPICard';
import { GradientAreaChart, MetricBarChart } from '../Charts';
import { api } from '../../lib/api';
import { CHART_COLORS } from '../../constants';
import { Filter, X } from 'lucide-react';

export const RevenueView: React.FC = () => {
  const revenueData = api.getRevenueTrends();
  const customerSegments = api.getCustomerSegments();
  const [filterSegment, setFilterSegment] = useState<string | null>(null);

  const handleSegmentClick = (data: any) => {
    setFilterSegment(filterSegment === data.name ? null : data.name);
  };

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard label="Total Revenue" value="$1.2M" change={12.5} trend="up" />
        <KPICard label="Recurring Revenue" value="$450k" change={5.2} trend="up" />
        <KPICard label="Avg Deal Size" value="$12,500" change={-1.2} trend="down" />
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white">Revenue Performance</h3>
          {filterSegment && (
            <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 dark:bg-primary/20 text-primary rounded-full text-xs font-medium animate-in fade-in">
              <Filter className="w-3 h-3" />
              Filtered by: {filterSegment}
              <button onClick={() => setFilterSegment(null)} className="hover:bg-primary/20 rounded-full p-0.5">
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
        {/* Using Gradient Area Chart for better visuals */}
        <GradientAreaChart 
          data={revenueData} 
          xKey="period"
          areas={[
            { key: 'revenue', name: 'Actual', color: CHART_COLORS[0] },
            { key: 'target', name: 'Target', color: CHART_COLORS[4] }
          ]}
          height={400} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Revenue by Segment</h3>
          <p className="text-xs text-text-tertiary dark:text-gray-400 mb-4 -mt-4">Click a bar to filter the dashboard</p>
          <MetricBarChart 
            data={customerSegments}
            xKey="name"
            bars={[{ key: 'value', name: 'Revenue', color: CHART_COLORS[1] }]}
            height={300}
            onBarClick={handleSegmentClick}
          />
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Top Revenue Sources</h3>
           {/* Placeholder for table */}
           <div className="overflow-x-auto">
             <table className="w-full">
               <thead>
                 <tr className="text-left border-b border-gray-100 dark:border-slate-700">
                   <th className="pb-3 text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase">Source</th>
                   <th className="pb-3 text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase text-right">Revenue</th>
                   <th className="pb-3 text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase text-right">%</th>
                 </tr>
               </thead>
               <tbody className="text-sm">
                 <tr className="border-b border-gray-50 dark:border-slate-700/50">
                   <td className="py-3 text-text-primary dark:text-gray-200 font-medium">Organic Search</td>
                   <td className="py-3 text-right text-text-secondary dark:text-gray-300">$450,000</td>
                   <td className="py-3 text-right text-success font-medium">35%</td>
                 </tr>
                 <tr className="border-b border-gray-50 dark:border-slate-700/50">
                   <td className="py-3 text-text-primary dark:text-gray-200 font-medium">Direct Sales</td>
                   <td className="py-3 text-right text-text-secondary dark:text-gray-300">$320,000</td>
                   <td className="py-3 text-right text-success font-medium">28%</td>
                 </tr>
                  <tr>
                   <td className="py-3 text-text-primary dark:text-gray-200 font-medium">Referrals</td>
                   <td className="py-3 text-right text-text-secondary dark:text-gray-300">$180,000</td>
                   <td className="py-3 text-right text-success font-medium">15%</td>
                 </tr>
               </tbody>
             </table>
           </div>
        </div>
      </div>
    </div>
  );
};