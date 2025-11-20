import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ChevronDown, Search } from 'lucide-react';
import { ViewType, VIEW_CONFIG } from '@/constants';
import { ViewType as SharedViewType } from '@/shared/types';

const ALL_VIEWS: ViewType[] = [
  'Overview', 'Revenue', 'Customers', 'Jobs', 'Sales Performance',
  'Leads', 'Operational', 'Geographic', 'Profitability', 'Forecasting', 'Benchmarking'
];

interface ViewSwitcherProps {
  className?: string;
}

export const ViewSwitcher: React.FC<ViewSwitcherProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const currentView = location.pathname.split('/').filter(Boolean)[0] || 'overview';
  const activeView: ViewType = currentView === '' || currentView === 'overview'
    ? 'Overview'
    : currentView.split('-').map(
        (word) => word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ') as ViewType;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredViews = ALL_VIEWS.filter(view => {
    if (!searchQuery) return true;
    const viewLower = view.toLowerCase();
    const queryLower = searchQuery.toLowerCase();
    return viewLower.includes(queryLower) || 
           VIEW_CONFIG[view as SharedViewType]?.description.toLowerCase().includes(queryLower);
  });

  const handleViewSelect = (view: ViewType) => {
    const path = view.toLowerCase().replace(/\s+/g, '-');
    navigate(`/${path}`);
    setIsOpen(false);
    setSearchQuery('');
  };

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 rounded-lg border border-gray-200 dark:border-slate-700 hover:border-primary transition-colors text-sm font-medium text-text-primary dark:text-white"
      >
        <span>{activeView}</span>
        <ChevronDown className={`w-4 h-4 text-text-tertiary dark:text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 bg-white dark:bg-slate-800 rounded-xl shadow-panel dark:shadow-xl border border-gray-100 dark:border-slate-700 z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200 origin-top-left">
          {/* Search */}
          <div className="p-3 border-b border-gray-100 dark:border-slate-700">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary dark:text-gray-400" />
              <input
                type="text"
                placeholder="Search views..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-600 rounded-lg text-sm text-text-primary dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                autoFocus
              />
            </div>
          </div>

          {/* View List */}
          <div className="max-h-96 overflow-y-auto custom-scrollbar">
            {filteredViews.length === 0 ? (
              <div className="p-4 text-center text-sm text-text-tertiary dark:text-gray-400">
                No views found
              </div>
            ) : (
              filteredViews.map((view) => {
                const viewConfig = VIEW_CONFIG[view as SharedViewType];
                const isActive = view === activeView;
                
                return (
                  <button
                    key={view}
                    onClick={() => handleViewSelect(view)}
                    className={`w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors ${
                      isActive ? 'bg-primary/5 dark:bg-primary/10 border-l-2 border-primary' : ''
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className={`text-sm font-medium ${isActive ? 'text-primary' : 'text-text-primary dark:text-white'}`}>
                        {view}
                      </div>
                      {viewConfig?.description && (
                        <div className="text-xs text-text-tertiary dark:text-gray-400 mt-0.5 line-clamp-1">
                          {viewConfig.description}
                        </div>
                      )}
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

