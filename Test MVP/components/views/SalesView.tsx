import React from 'react';
import { KPICard } from '../KPICard';
import { MetricBarChart, SkillRadarChart } from '../Charts';
import { api } from '../../lib/api';
import { CHART_COLORS } from '../../constants';
import { Radar } from 'lucide-react';

export const SalesView: React.FC = () => {
  const performers = api.getSalesPerformance();
  const skillsData = api.getSkillsRadar();

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard label="Total Sales" value="$854k" change={15.2} trend="up" />
        <KPICard label="Deals Closed" value="142" change={8.5} trend="up" />
        <KPICard label="Avg Commission" value="$3,200" change={2.4} trend="up" />
        <KPICard label="Pipeline Value" value="$2.1M" change={-1.5} trend="down" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Leaderboard */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-6">Sales Leaderboard</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-slate-700">
                  <th className="text-left py-4 px-4 font-semibold text-xs text-text-tertiary dark:text-gray-400 uppercase">Agent</th>
                  <th className="text-right py-4 px-4 font-semibold text-xs text-text-tertiary dark:text-gray-400 uppercase">Deals</th>
                  <th className="text-right py-4 px-4 font-semibold text-xs text-text-tertiary dark:text-gray-400 uppercase">Conversion</th>
                  <th className="text-right py-4 px-4 font-semibold text-xs text-text-tertiary dark:text-gray-400 uppercase">Revenue</th>
                  <th className="text-center py-4 px-4 font-semibold text-xs text-text-tertiary dark:text-gray-400 uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {performers.map((agent) => (
                  <tr key={agent.id} className="border-b border-gray-50 dark:border-slate-700/50 hover:bg-gray-50/50 dark:hover:bg-slate-700/30 transition-colors">
                    <td className="py-4 px-4 flex items-center gap-3">
                      <img src={agent.avatar} alt={agent.name} className="w-10 h-10 rounded-full object-cover border-2 border-white dark:border-slate-700 shadow-sm" />
                      <div>
                        <p className="font-semibold text-text-primary dark:text-gray-200 text-sm">{agent.name}</p>
                        <p className="text-xs text-text-tertiary dark:text-gray-500">Senior Agent</p>
                      </div>
                    </td>
                    <td className="text-right py-4 px-4 text-sm font-medium text-text-secondary dark:text-gray-300">{agent.deals}</td>
                    <td className="text-right py-4 px-4 text-sm font-medium text-text-secondary dark:text-gray-300">{agent.conversion}%</td>
                    <td className="text-right py-4 px-4 text-sm font-bold text-text-primary dark:text-white">${agent.revenue.toLocaleString()}</td>
                    <td className="text-center py-4 px-4">
                      <span className="px-2 py-1 rounded-full bg-success/10 dark:bg-success/20 text-success text-xs font-bold">Active</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Skills Radar Analysis */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-primary dark:text-white">Team Skill Gap</h3>
            <Radar className="w-4 h-4 text-text-tertiary dark:text-gray-400" />
          </div>
          <p className="text-xs text-text-secondary dark:text-gray-300 mb-6">Comparing top agent avg vs team avg</p>
          <SkillRadarChart data={skillsData} height={300} />
          <div className="mt-4 flex justify-center gap-4 text-xs dark:text-gray-400">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{backgroundColor: CHART_COLORS[0]}}></div>
              <span>Top Agent</span>
            </div>
            <div className="flex items-center gap-1">
               <div className="w-2 h-2 rounded-full" style={{backgroundColor: CHART_COLORS[4]}}></div>
               <span>Team Avg</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};