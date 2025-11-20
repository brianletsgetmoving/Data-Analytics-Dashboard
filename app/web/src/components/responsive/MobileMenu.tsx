import React from 'react';
import { X } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ViewType } from '@/shared/types';
import { VIEW_CONFIG } from '@/constants';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

const CORE_VIEWS: ViewType[] = ['Overview', 'Revenue', 'Customers', 'Jobs', 'Sales Performance'];
const ADVANCED_VIEWS: ViewType[] = ['Leads', 'Operational', 'Geographic'];
const STRATEGIC_VIEWS: ViewType[] = ['Profitability', 'Forecasting', 'Benchmarking'];

export const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const currentView = location.pathname.split('/').filter(Boolean)[0] || 'overview';
  const activeView: ViewType = currentView === '' || currentView === 'overview'
    ? 'Overview'
    : currentView.split('-').map(
        (word) => word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ') as ViewType;

  const handleViewClick = (view: ViewType) => {
    const path = view.toLowerCase().replace(/\s+/g, '-');
    navigate(`/${path}`);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden animate-in fade-in duration-200">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Menu Panel */}
      <div className="absolute left-0 top-0 h-full w-80 bg-white dark:bg-slate-900 shadow-2xl overflow-y-auto custom-scrollbar animate-in slide-in-from-left-4 duration-300">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between p-6 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-text-primary dark:text-white">Navigation</h2>
          <button
            onClick={onClose}
            className="p-2 text-text-tertiary dark:text-gray-400 hover:text-text-primary dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-6">
          <div>
            <h3 className="text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase tracking-wider mb-3 px-2">
              Core Views
            </h3>
            <div className="space-y-1">
              {CORE_VIEWS.map((view) => (
                <button
                  key={view}
                  onClick={() => handleViewClick(view)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    activeView === view
                      ? 'bg-primary text-white'
                      : 'text-text-secondary dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-800'
                  }`}
                >
                  {view}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase tracking-wider mb-3 px-2">
              Advanced Analytics
            </h3>
            <div className="space-y-1">
              {ADVANCED_VIEWS.map((view) => (
                <button
                  key={view}
                  onClick={() => handleViewClick(view)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    activeView === view
                      ? 'bg-primary text-white'
                      : 'text-text-secondary dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-800'
                  }`}
                >
                  {view}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase tracking-wider mb-3 px-2">
              Strategic Analysis
            </h3>
            <div className="space-y-1">
              {STRATEGIC_VIEWS.map((view) => (
                <button
                  key={view}
                  onClick={() => handleViewClick(view)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    activeView === view
                      ? 'bg-primary text-white'
                      : 'text-text-secondary dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-800'
                  }`}
                >
                  {view}
                </button>
              ))}
            </div>
          </div>
        </nav>
      </div>
    </div>
  );
};

