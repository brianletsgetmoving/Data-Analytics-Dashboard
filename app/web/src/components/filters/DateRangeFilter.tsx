import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronDown, X, Check } from 'lucide-react';
import { DateRangePreset, FilterParams } from '@/shared/types';
import { useFilterStore } from '@/store/filterStore';

interface DateRangeFilterProps {
  className?: string;
  onChange?: (filters: FilterParams) => void;
}

export const DateRangeFilter: React.FC<DateRangeFilterProps> = ({ className, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<DateRangePreset>('This Month');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const { setFilters } = useFilterStore();

  const PRESETS: DateRangePreset[] = [
    'Today',
    'Last 7 Days',
    'Last 30 Days',
    'This Month',
    'Last Month'
  ];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const calculateDateRange = (preset: DateRangePreset): { start: string; end: string } => {
    const today = new Date();
    const end = new Date(today);
    end.setHours(23, 59, 59, 999);

    let start = new Date(today);

    switch (preset) {
      case 'Today':
        start.setHours(0, 0, 0, 0);
        break;
      case 'Last 7 Days':
        start.setDate(today.getDate() - 7);
        start.setHours(0, 0, 0, 0);
        break;
      case 'Last 30 Days':
        start.setDate(today.getDate() - 30);
        start.setHours(0, 0, 0, 0);
        break;
      case 'This Month':
        start = new Date(today.getFullYear(), today.getMonth(), 1);
        start.setHours(0, 0, 0, 0);
        break;
      case 'Last Month':
        start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        start.setHours(0, 0, 0, 0);
        end.setDate(0); // Last day of previous month
        end.setHours(23, 59, 59, 999);
        break;
      default:
        start.setHours(0, 0, 0, 0);
    }

    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0],
    };
  };

  const handlePresetChange = (preset: DateRangePreset) => {
    setSelectedPreset(preset);
    if (preset !== 'Custom') {
      setIsOpen(false);
      const { start, end } = calculateDateRange(preset);
      const filterParams: FilterParams = {
        date_from: start,
        date_to: end,
      };
      setFilters(filterParams);
      if (onChange) {
        onChange(filterParams);
      }
    }
  };

  const handleApplyCustom = () => {
    if (startDate && endDate) {
      setSelectedPreset('Custom');
      setIsOpen(false);
      const filterParams: FilterParams = {
        date_from: startDate,
        date_to: endDate,
      };
      setFilters(filterParams);
      if (onChange) {
        onChange(filterParams);
      }
    }
  };

  const getDisplayLabel = () => {
    if (selectedPreset === 'Custom' && startDate && endDate) {
      return `${new Date(startDate).toLocaleDateString()} - ${new Date(endDate).toLocaleDateString()}`;
    }
    return selectedPreset;
  };

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-3 px-4 py-2.5 bg-white dark:bg-slate-800 rounded-xl border transition-all duration-200
          ${isOpen ? 'border-primary ring-2 ring-primary/10 shadow-card' : 'border-gray-200 dark:border-slate-700 hover:border-primary/50 shadow-sm hover:shadow-md dark:shadow-none'}
        `}
      >
        <Calendar className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-text-primary dark:text-gray-200 min-w-[100px] text-left">
          {getDisplayLabel()}
        </span>
        <ChevronDown className={`w-4 h-4 text-text-tertiary dark:text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-800 rounded-xl shadow-panel dark:shadow-xl border border-gray-100 dark:border-slate-700 z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200 origin-top-right">
          
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-100 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-900/50">
            <span className="text-micro text-text-tertiary dark:text-gray-500 font-semibold uppercase tracking-wider">
              Select Range
            </span>
          </div>

          {/* Presets */}
          <div className="p-2 space-y-0.5">
            {PRESETS.map((preset) => (
              <button
                key={preset}
                onClick={() => handlePresetChange(preset)}
                className={`
                  w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors
                  ${selectedPreset === preset 
                    ? 'bg-primary/5 dark:bg-primary/10 text-primary font-medium' 
                    : 'text-text-secondary dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 hover:text-text-primary dark:hover:text-white'}
                `}
              >
                <span>{preset}</span>
                {selectedPreset === preset && <Check className="w-4 h-4" />}
              </button>
            ))}
          </div>

          <div className="h-px bg-gray-100 dark:bg-slate-700 mx-2 my-1" />

          {/* Custom Range */}
          <div className="p-4 space-y-3">
            <span className="text-micro text-text-tertiary dark:text-gray-500 font-semibold uppercase tracking-wider block mb-2">
              Custom Range
            </span>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[10px] font-medium text-text-tertiary dark:text-gray-400">Start</label>
                <input 
                  type="date" 
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(e.target.value);
                    setSelectedPreset('Custom');
                  }}
                  className="w-full px-2 py-1.5 bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg text-xs text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-medium text-text-tertiary dark:text-gray-400">End</label>
                <input 
                  type="date" 
                  value={endDate}
                  onChange={(e) => {
                    setEndDate(e.target.value);
                    setSelectedPreset('Custom');
                  }}
                  className="w-full px-2 py-1.5 bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg text-xs text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>

            <button 
              onClick={handleApplyCustom}
              disabled={!startDate || !endDate}
              className="w-full mt-2 py-2 bg-primary text-white text-xs font-semibold rounded-lg shadow-lg shadow-primary/25 hover:bg-primary-hover hover:shadow-primary/40 disabled:opacity-50 disabled:shadow-none transition-all"
            >
              Apply Range
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

