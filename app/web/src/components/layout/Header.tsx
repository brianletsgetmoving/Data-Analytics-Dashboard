import React, { useState } from 'react';
import { Search, Bell, Filter, ChevronDown, Menu, Moon, Sun } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import { AdvancedFilterPanel } from '../filters/AdvancedFilterPanel';
import { useLocation } from 'react-router-dom';
import { VIEW_CONFIG } from '@/constants';
import { ViewType } from '@/shared/types';

interface HeaderProps {
  onMenuClick: () => void;
}

const getViewTitle = (pathname: string): string => {
  const view = pathname.split('/').filter(Boolean)[0] || 'overview';
  const viewType = view.split('-').map(
    (word) => word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ') as ViewType;
  
  return VIEW_CONFIG[viewType]?.description || 'Analytics Dashboard';
};

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { theme, toggleTheme } = useTheme();
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const location = useLocation();
  const viewTitle = getViewTitle(location.pathname);

  return (
    <header className="h-[72px] flex items-center justify-between px-6 lg:px-8 sticky top-0 z-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-gray-100/50 dark:border-slate-800">
      <div className="flex items-center gap-4">
        <button 
          onClick={onMenuClick}
          className="lg:hidden p-2 text-text-secondary dark:text-gray-400 hover:text-primary rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800"
        >
          <Menu className="w-6 h-6" />
        </button>
        <h2 className="text-xl font-semibold text-text-primary dark:text-white hidden sm:block">
          {viewTitle}
        </h2>
      </div>

      <div className="flex items-center gap-3 sm:gap-6">
        {/* Search Pill */}
        <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full bg-gray-50 dark:bg-slate-800 hover:bg-white dark:hover:bg-slate-700 hover:shadow-md transition-all border border-transparent hover:border-gray-100 dark:hover:border-slate-600 cursor-pointer group w-64">
          <Search className="w-4 h-4 text-text-tertiary dark:text-gray-500 group-hover:text-primary transition-colors" />
          <input 
            type="text" 
            placeholder="Search metrics..." 
            className="bg-transparent border-none outline-none text-sm w-full text-text-primary dark:text-gray-200 placeholder-text-tertiary dark:placeholder-gray-500"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <button 
            onClick={toggleTheme}
            className="p-2 text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-primary rounded-full hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          </button>

          <button 
            className="relative p-2 text-text-secondary dark:text-gray-400 hover:text-primary rounded-full hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-2 w-2 h-2 bg-danger rounded-full border-2 border-white dark:border-slate-900"></span>
          </button>
          
          <button 
            onClick={() => setIsFilterPanelOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-700 text-text-secondary dark:text-gray-300 text-sm font-medium hover:border-primary hover:text-primary transition-colors bg-white dark:bg-slate-800"
          >
            <Filter className="w-4 h-4" />
            <span className="hidden sm:inline">Filters</span>
            <span className="flex items-center justify-center w-5 h-5 bg-primary text-white text-[10px] rounded-full ml-1">3</span>
          </button>

          <div className="h-8 w-[1px] bg-gray-200 dark:bg-slate-700 mx-1 hidden sm:block"></div>

          <button className="flex items-center gap-3 pl-1 pr-2 py-1 rounded-full hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors">
            <img 
              src="https://picsum.photos/100/100" 
              alt="User" 
              className="w-8 h-8 rounded-full border-2 border-white dark:border-slate-700 shadow-sm object-cover"
            />
            <div className="hidden lg:block text-left">
              <p className="text-xs font-semibold text-text-primary dark:text-gray-200">Alex M.</p>
              <p className="text-[10px] text-text-tertiary dark:text-gray-500">Admin</p>
            </div>
            <ChevronDown className="w-4 h-4 text-text-tertiary dark:text-gray-500 hidden lg:block" />
          </button>
        </div>
      </div>

      <AdvancedFilterPanel 
        isOpen={isFilterPanelOpen} 
        onClose={() => setIsFilterPanelOpen(false)} 
      />
    </header>
  );
};
