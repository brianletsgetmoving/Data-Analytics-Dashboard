import React, { useState } from 'react';
import { KPICard } from '@/components/ui/KPICard';
import { GradientAreaChart, MetricBarChart, DonutChart, DensityHeatmap } from '@/components/charts';
import { RefreshCw, Download, Calendar, X, TrendingUp, Award, User, Clock } from 'lucide-react';
import { useRevenueTrendsQuery, useMonthlyMetricsQuery, useSalesPersonPerformanceQuery, useHeatmapQuery, useLeadSourcesQuery } from '@/hooks/useAnalytics';
import { CHART_COLORS } from '@/constants';
import {
  transformRevenueMetricsToChartData,
  transformSalesPersonToPerformer,
  calculateKPIsFromMetrics,
  transformHeatmapToPoints,
} from '@/utils/dataTransform';
import { useQuery } from '@tanstack/react-query';
import { useFilterStore } from '@/store/filterStore';

export default function Overview() {
  const [selectedPerformer, setSelectedPerformer] = useState<any>(null);
  const [periodType, setPeriodType] = useState<'monthly' | 'quarterly' | 'yearly'>('monthly');
  const { filters } = useFilterStore();

  // Fetch data
  const { data: revenueData, isLoading: revenueLoading } = useRevenueTrendsQuery(periodType, filters);
  const { data: metricsData, isLoading: metricsLoading } = useMonthlyMetricsQuery(filters);
  const { data: salesData, isLoading: salesLoading } = useSalesPersonPerformanceQuery(filters);
  const { data: heatmapData, isLoading: heatmapLoading } = useHeatmapQuery(filters);

  // Fetch lead sources data
  const { data: leadSourcesData, isLoading: leadSourcesLoading } = useLeadSourcesQuery(filters);

  // Transform data
  const kpis = calculateKPIsFromMetrics(metricsData?.data || [], []);
  const revenueChartData = transformRevenueMetricsToChartData(revenueData?.data || [], []);
  const salesPerformance = transformSalesPersonToPerformer(salesData?.data || []).slice(0, 5);
  // Transform lead sources data to chart format
  // SQL returns: referral_source, affiliate_name, total_leads, total_revenue
  const leadSources = (leadSourcesData?.data || []).map((source: any, index: number) => ({
    name: source.referral_source || source.affiliate_name || source.lead_source_name || source.name || 'Unnamed Source',
    value: source.total_leads || source.total_revenue || source.count || source.value || 0,
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));
  
  // Transform heatmap data (mock for now - will need proper transformation)
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = ['9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm'];
  const heatmapPoints = heatmapData?.data 
    ? transformHeatmapToPoints(heatmapData.data, 'month', 'branch_name')
    : [];

  const handlePerformerClick = (data: any) => {
    setSelectedPerformer(data);
  };

  return (
    <div className="animate-in fade-in duration-500">
      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
        {kpis.map((kpi, idx) => (
          <KPICard key={idx} {...kpi} />
        ))}
      </div>

      {/* Charts Row 1: Revenue Trend + Sales Leaderboard */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
        {/* Main Revenue Chart */}
        <div className="xl:col-span-2 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none min-h-[420px] flex flex-col border border-transparent dark:border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-text-primary dark:text-white">Revenue Trends</h3>
              <p className="text-xs text-text-tertiary dark:text-gray-400 mt-1">Year over year comparison</p>
            </div>
            <div className="flex gap-2">
              <select
                value={periodType}
                onChange={(e) => setPeriodType(e.target.value as 'monthly' | 'quarterly' | 'yearly')}
                className="px-3 py-1.5 bg-gray-50 dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary"
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
              <button className="p-2 hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg text-text-tertiary dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors">
                <RefreshCw className="w-4 h-4" />
              </button>
              <button className="p-2 hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg text-text-tertiary dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors">
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="flex-1 w-full min-h-0">
            <GradientAreaChart 
              data={revenueChartData} 
              xKey="period"
              areas={[
                { key: 'revenue', name: 'Current Year', color: CHART_COLORS[0] },
                { key: 'previousRevenue', name: 'Previous Year', color: CHART_COLORS[1] }
              ]}
              height={320}
              isLoading={revenueLoading}
            />
          </div>
        </div>

        {/* Top Salespeople */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none min-h-[420px] flex flex-col border border-transparent dark:border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-text-primary dark:text-white">Top Performers</h3>
              <p className="text-xs text-text-tertiary dark:text-gray-400 mt-1">Click bar for details</p>
            </div>
            <button className="text-xs font-medium text-primary hover:underline">View All</button>
          </div>
          <div className="flex-1 w-full min-h-0">
            <MetricBarChart 
              data={salesPerformance.map(sp => ({ name: sp.name, value: sp.revenue }))} 
              xKey="name"
              bars={[{ key: 'value', name: 'Revenue', color: CHART_COLORS[5] }]}
              layout="vertical"
              height={320}
              isLoading={salesLoading}
              onBarClick={handlePerformerClick}
            />
          </div>
        </div>
      </div>

      {/* Selected Performer Drill-down Panel */}
      {selectedPerformer && (
        <div className="mb-8 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border-l-4 border-primary relative overflow-hidden animate-in slide-in-from-right-4 duration-300 dark:border dark:border-l-4 border-transparent dark:border-slate-700">
          <button 
            onClick={() => setSelectedPerformer(null)}
            className="absolute top-4 right-4 p-1 text-text-tertiary dark:text-gray-400 hover:text-text-primary dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-hover flex items-center justify-center text-white shadow-lg shadow-primary/30">
               <User className="w-7 h-7" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h3 className="text-xl font-bold text-text-primary dark:text-white">{selectedPerformer.name}</h3>
                <span className="px-2 py-0.5 bg-success/10 dark:bg-success/20 text-success text-[10px] font-bold uppercase rounded-full tracking-wide">Top Tier</span>
              </div>
              <p className="text-text-secondary dark:text-gray-300 text-sm mb-4 max-w-2xl">
                Currently performing in the top 5% percentile. Shows strong consistency in closing deals and high customer satisfaction scores.
              </p>
              
              <div className="grid grid-cols-3 gap-4 max-w-lg">
                <div className="bg-gray-50 dark:bg-slate-700/50 rounded-xl p-3 border border-gray-100 dark:border-slate-600">
                  <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-text-tertiary dark:text-gray-400 mb-1">
                    <Award className="w-3 h-3" /> Revenue
                  </div>
                  <div className="text-lg font-bold text-primary">${(selectedPerformer.value / 1000).toFixed(0)}k</div>
                </div>
                <div className="bg-gray-50 dark:bg-slate-700/50 rounded-xl p-3 border border-gray-100 dark:border-slate-600">
                  <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-text-tertiary dark:text-gray-400 mb-1">
                    <TrendingUp className="w-3 h-3" /> Growth
                  </div>
                  <div className="text-lg font-bold text-success">+12.4%</div>
                </div>
                <div className="bg-gray-50 dark:bg-slate-700/50 rounded-xl p-3 border border-gray-100 dark:border-slate-600">
                  <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-text-tertiary dark:text-gray-400 mb-1">
                    <Calendar className="w-3 h-3" /> Deals
                  </div>
                  <div className="text-lg font-bold text-text-primary dark:text-white">{selectedPerformer.deals || 0}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Row 2: Lead Sources + Activity Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Source Donut */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-text-primary dark:text-white">Lead Sources</h3>
            <div className="flex items-center gap-1 text-xs font-medium text-text-secondary dark:text-gray-300 bg-gray-50 dark:bg-slate-700 px-2 py-1 rounded-md">
              <Calendar className="w-3 h-3" />
              <span>This Month</span>
            </div>
          </div>
          <DonutChart data={leadSources} height={280} isLoading={leadSourcesLoading} />
        </div>
        
        {/* Activity Heatmap */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <div>
               <h3 className="text-lg font-semibold text-text-primary dark:text-white">Activity Heatmap</h3>
               <p className="text-xs text-text-tertiary dark:text-gray-400 mt-1">System usage intensity by time of day</p>
            </div>
            <div className="p-2 bg-primary/5 dark:bg-primary/10 rounded-lg">
              <Clock className="w-4 h-4 text-primary" />
            </div>
          </div>
          <div className="flex justify-center">
            <DensityHeatmap 
              data={heatmapPoints}
              xAxisLabels={days}
              yAxisLabels={hours}
              isLoading={heatmapLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

