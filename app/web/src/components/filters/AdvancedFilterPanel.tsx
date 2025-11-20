import React, { useState } from 'react';
import { X, Filter, Search } from 'lucide-react';
import { useFilterStore } from '@/store/filterStore';
import { FilterParams } from '@/shared/types';

interface AdvancedFilterPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AdvancedFilterPanel: React.FC<AdvancedFilterPanelProps> = ({ isOpen, onClose }) => {
  const { filters, setFilters, clearFilters } = useFilterStore();
  const [localFilters, setLocalFilters] = useState<FilterParams>(filters);

  const handleApply = () => {
    setFilters(localFilters);
    onClose();
  };

  const handleReset = () => {
    setLocalFilters({});
    clearFilters();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end animate-in fade-in duration-200">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="relative w-full max-w-md h-full bg-white dark:bg-slate-900 shadow-2xl overflow-y-auto custom-scrollbar animate-in slide-in-from-right-4 duration-300">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between p-6 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <Filter className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold text-text-primary dark:text-white">Advanced Filters</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-text-tertiary dark:text-gray-400 hover:text-text-primary dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-text-primary dark:text-white mb-2">
              Date Range
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-text-tertiary dark:text-gray-400 mb-1">From</label>
                <input
                  type="date"
                  value={localFilters.date_from || ''}
                  onChange={(e) => setLocalFilters({ ...localFilters, date_from: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-xs text-text-tertiary dark:text-gray-400 mb-1">To</label>
                <input
                  type="date"
                  value={localFilters.date_to || ''}
                  onChange={(e) => setLocalFilters({ ...localFilters, date_to: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>
          </div>

          {/* Branch Filter */}
          <div>
            <label className="block text-sm font-medium text-text-primary dark:text-white mb-2">
              Branch
            </label>
            <input
              type="text"
              placeholder="Branch name or ID"
              value={localFilters.branch_name || localFilters.branch_id || ''}
              onChange={(e) => setLocalFilters({ 
                ...localFilters, 
                branch_name: e.target.value,
                branch_id: e.target.value.includes('-') ? e.target.value : undefined
              })}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Sales Person Filter */}
          <div>
            <label className="block text-sm font-medium text-text-primary dark:text-white mb-2">
              Sales Person
            </label>
            <input
              type="text"
              placeholder="Sales person name or ID"
              value={localFilters.sales_person_name || localFilters.sales_person_id || ''}
              onChange={(e) => setLocalFilters({ 
                ...localFilters, 
                sales_person_name: e.target.value,
                sales_person_id: e.target.value.includes('-') ? e.target.value : undefined
              })}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Opportunity Status */}
          <div>
            <label className="block text-sm font-medium text-text-primary dark:text-white mb-2">
              Opportunity Status
            </label>
            <select
              value={localFilters.opportunity_status || ''}
              onChange={(e) => setLocalFilters({ 
                ...localFilters, 
                opportunity_status: e.target.value as FilterParams['opportunity_status'] || undefined
              })}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            >
              <option value="">All Statuses</option>
              <option value="QUOTED">Quoted</option>
              <option value="BOOKED">Booked</option>
              <option value="CLOSED">Closed</option>
              <option value="LOST">Lost</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 p-6 bg-white dark:bg-slate-900 border-t border-gray-200 dark:border-slate-700 flex gap-3">
          <button
            onClick={handleReset}
            className="flex-1 px-4 py-2 border border-gray-200 dark:border-slate-600 text-text-secondary dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
          >
            Reset
          </button>
          <button
            onClick={handleApply}
            className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors text-sm font-medium shadow-lg shadow-primary/25"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
};

