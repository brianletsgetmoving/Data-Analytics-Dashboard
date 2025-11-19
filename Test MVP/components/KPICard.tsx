import React from 'react';
import { KPIProps } from '../types';
import { Info, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export const KPICard: React.FC<KPIProps> = ({ label, value, change, statusBadge, trend }) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-card dark:shadow-none border border-transparent dark:border-slate-700 hover:shadow-card-hover hover:scale-[1.02] transition-all duration-300 cursor-default hover:border-primary/20 flex flex-col justify-between min-h-[160px]">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-text-secondary dark:text-gray-400">{label}</span>
          {statusBadge && (
            <span className="px-2 py-0.5 rounded-full bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary-hover text-[10px] font-bold uppercase tracking-wide">
              {statusBadge}
            </span>
          )}
        </div>
        <button className="text-text-tertiary dark:text-gray-500 hover:text-primary dark:hover:text-primary transition-colors p-1 rounded-md hover:bg-gray-50 dark:hover:bg-slate-700">
          <Info className="w-4 h-4" />
        </button>
      </div>

      <div className="mt-4">
        <div className="text-4xl font-semibold text-text-primary dark:text-white tracking-tight">
          {value}
        </div>
        
        {change !== undefined && (
          <div className="flex items-center gap-2 mt-3">
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
              trend === 'up' ? 'bg-success/10 dark:bg-success/20 text-success' : 
              trend === 'down' ? 'bg-danger/10 dark:bg-danger/20 text-danger' : 'bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300'
            }`}>
              {trend === 'up' && <TrendingUp className="w-3 h-3" />}
              {trend === 'down' && <TrendingDown className="w-3 h-3" />}
              {trend === 'neutral' && <Minus className="w-3 h-3" />}
              <span>{Math.abs(change)}%</span>
            </div>
            <span className="text-xs text-text-tertiary dark:text-gray-500">vs last month</span>
          </div>
        )}
      </div>
    </div>
  );
};