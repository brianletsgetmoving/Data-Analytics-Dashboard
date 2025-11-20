import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Briefcase, 
  DollarSign, 
  TrendingUp, 
  Settings, 
  LogOut,
  Target,
  MapPin,
  PiggyBank,
  BarChart3,
} from 'lucide-react';
import { ViewType } from '@/shared/types';
import { VIEW_CONFIG } from '@/constants';

interface SidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

const CORE_VIEWS: ViewType[] = ['Overview', 'Revenue', 'Customers', 'Jobs', 'Sales Performance'];
const ADVANCED_VIEWS: ViewType[] = ['Leads', 'Operational', 'Geographic'];
const STRATEGIC_VIEWS: ViewType[] = ['Profitability', 'Forecasting', 'Benchmarking'];

const ICON_MAP: Record<ViewType, React.ComponentType<{ className?: string }>> = {
  'Overview': LayoutDashboard,
  'Revenue': DollarSign,
  'Customers': Users,
  'Jobs': Briefcase,
  'Sales Performance': TrendingUp,
  'Leads': Target,
  'Operational': Settings,
  'Geographic': MapPin,
  'Profitability': PiggyBank,
  'Forecasting': TrendingUp,
  'Benchmarking': BarChart3,
};

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const currentView = location.pathname.split('/').filter(Boolean)[0] || 'overview';
  const activeView: ViewType = currentView === '' || currentView === 'overview' 
    ? 'Overview' 
    : currentView.split('-').map(
        (word) => word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ') as ViewType;

  const handleViewChange = (view: ViewType) => {
    const path = view.toLowerCase().replace(/\s+/g, '-');
    navigate(`/${path}`);
    if (onToggle && window.innerWidth < 1024) {
      onToggle();
    }
  };

  const renderNavSection = (title: string, views: ViewType[]) => (
    <div className="mb-6">
      <div className="mb-4 px-2 h-5 flex items-center overflow-hidden">
        <p className={`
          text-micro text-text-tertiary dark:text-gray-500 font-semibold uppercase tracking-wider whitespace-nowrap transition-all duration-500
          ${isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 lg:opacity-100 lg:translate-x-0'}
        `}>
          {title}
        </p>
      </div>
      
      <div className="space-y-2">
        {views.map((view) => {
          const Icon = ICON_MAP[view];
          const isActive = activeView === view;
          const path = view.toLowerCase().replace(/\s+/g, '-');
          
          return (
            <button 
              key={view}
              onClick={() => handleViewChange(view)}
              className={`
                w-full flex items-center relative group rounded-xl transition-all duration-300
                ${isActive 
                  ? 'bg-primary shadow-md shadow-primary/25' 
                  : 'hover:bg-gray-50 dark:hover:bg-slate-800'
                }
                h-12
              `}
              title={view}
            >
              <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 ml-1">
                <Icon className={`
                  w-5 h-5 transition-colors duration-300
                  ${isActive ? 'text-white' : 'text-text-secondary dark:text-gray-400 group-hover:text-primary'}
                `} />
              </div>
              
              <div className={`
                overflow-hidden whitespace-nowrap transition-all duration-500 ease-in-out
                ${isOpen ? 'opacity-100 max-w-[150px] translate-x-0' : 'opacity-0 max-w-0 -translate-x-4 lg:opacity-100 lg:max-w-[150px] lg:translate-x-0'}
              `}>
                <span className={`
                  ml-1 font-medium text-sm tracking-wide block
                  ${isActive ? 'text-white' : 'text-text-secondary dark:text-gray-300 group-hover:text-primary'}
                `}>
                  {view}
                </span>
              </div>

              {!isOpen && isActive && (
                <div className="absolute right-1 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-white rounded-full lg:hidden shadow-sm animate-pulse"></div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <aside className={`
      fixed left-0 top-0 z-50 h-screen bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-r border-gray-100/50 dark:border-slate-800 shadow-2xl lg:shadow-none
      flex flex-col overflow-hidden
      transition-[width] duration-500 cubic-bezier(0.4, 0, 0.2, 1)
      ${isOpen ? 'w-[260px]' : 'w-[80px] lg:w-[260px]'}
    `}>
      {/* Logo Area */}
      <div className="h-[72px] flex items-center px-6 flex-shrink-0 border-b border-gray-100/50 dark:border-slate-800">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/30 z-10 relative">
          <div className="w-4 h-4 bg-white rounded-sm opacity-50 rotate-45"></div>
        </div>
        
        <div className={`
          ml-3 overflow-hidden whitespace-nowrap transition-all duration-500 ease-in-out
          ${isOpen ? 'opacity-100 max-w-[150px] translate-x-0' : 'opacity-0 max-w-0 -translate-x-4 lg:opacity-100 lg:max-w-[150px] lg:translate-x-0'}
        `}>
          <span className="text-lg font-bold text-text-primary dark:text-white tracking-tight block">SmartMove</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-8 px-4 space-y-6 overflow-y-auto overflow-x-hidden custom-scrollbar">
        {renderNavSection('Core Views', CORE_VIEWS)}
        {renderNavSection('Advanced Analytics', ADVANCED_VIEWS)}
        {renderNavSection('Strategic Analysis', STRATEGIC_VIEWS)}

        <div className="mt-auto">
          <div className="mb-4 px-2 h-5 flex items-center overflow-hidden">
            <p className={`
              text-micro text-text-tertiary dark:text-gray-500 font-semibold uppercase tracking-wider whitespace-nowrap transition-all duration-500
              ${isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 lg:opacity-100 lg:translate-x-0'}
            `}>
              System
            </p>
          </div>
          
          <div className="space-y-2">
            <button className={`
              w-full flex items-center h-12 rounded-xl text-text-secondary dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-primary transition-all group
            `}>
              <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 ml-1">
                <Settings className="w-5 h-5 text-text-tertiary dark:text-gray-500 group-hover:text-primary transition-colors" />
              </div>
              <div className={`
                overflow-hidden whitespace-nowrap transition-all duration-500 ease-in-out
                ${isOpen ? 'opacity-100 max-w-[150px] translate-x-0' : 'opacity-0 max-w-0 -translate-x-4 lg:opacity-100 lg:max-w-[150px] lg:translate-x-0'}
              `}>
                <span className="ml-1 font-medium text-sm tracking-wide group-hover:text-primary">Settings</span>
              </div>
            </button>
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100/50 dark:border-slate-800">
        <button className={`
          w-full flex items-center h-12 rounded-xl border border-transparent text-text-secondary dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-danger hover:border-red-100 dark:hover:border-red-900/30 transition-all group
        `}>
          <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 ml-1">
            <LogOut className="w-5 h-5 transition-colors" />
          </div>
          <div className={`
            overflow-hidden whitespace-nowrap transition-all duration-500 ease-in-out
            ${isOpen ? 'opacity-100 max-w-[150px] translate-x-0' : 'opacity-0 max-w-0 -translate-x-4 lg:opacity-100 lg:max-w-[150px] lg:translate-x-0'}
          `}>
            <span className="ml-1 font-medium text-sm">Sign Out</span>
          </div>
        </button>
      </div>
    </aside>
  );
};

