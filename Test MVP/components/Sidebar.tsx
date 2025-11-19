import React from 'react';
import { LayoutDashboard, Users, Briefcase, DollarSign, TrendingUp, Settings, LogOut } from 'lucide-react';
import { ViewType } from '../types';

interface SidebarProps {
  activeView: ViewType;
  onViewChange: (view: ViewType) => void;
  isOpen?: boolean;
}

const NAV_ITEMS: { icon: any; label: ViewType }[] = [
  { icon: LayoutDashboard, label: "Overview" },
  { icon: Users, label: "Customers" },
  { icon: Briefcase, label: "Jobs" },
  { icon: DollarSign, label: "Revenue" },
  { icon: TrendingUp, label: "Sales Performance" },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onViewChange, isOpen }) => {
  
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
        <div>
          <div className="mb-4 px-2 h-5 flex items-center overflow-hidden">
            <p className={`
              text-micro text-text-tertiary dark:text-gray-500 font-semibold uppercase tracking-wider whitespace-nowrap transition-all duration-500
              ${isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 lg:opacity-100 lg:translate-x-0'}
            `}>
              Main Menu
            </p>
            <div className={`
              w-4 h-0.5 bg-gray-200 dark:bg-slate-700 rounded-full absolute
              ${isOpen ? 'opacity-0' : 'opacity-100 lg:opacity-0'}
              transition-opacity duration-500
            `}></div>
          </div>
          
          <div className="space-y-2">
            {NAV_ITEMS.map((item) => (
              <button 
                key={item.label}
                onClick={() => onViewChange(item.label)}
                className={`
                  w-full flex items-center relative group rounded-xl transition-all duration-300
                  ${activeView === item.label 
                    ? 'bg-primary shadow-md shadow-primary/25' 
                    : 'hover:bg-gray-50 dark:hover:bg-slate-800'
                  }
                  h-12
                `}
                title={item.label}
              >
                {/* Icon Container - Fixed width to prevent jumping */}
                <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 ml-1">
                  <item.icon className={`
                    w-5 h-5 transition-colors duration-300
                    ${activeView === item.label ? 'text-white' : 'text-text-secondary dark:text-gray-400 group-hover:text-primary'}
                  `} />
                </div>
                
                {/* Label Container */}
                <div className={`
                  overflow-hidden whitespace-nowrap transition-all duration-500 ease-in-out
                  ${isOpen ? 'opacity-100 max-w-[150px] translate-x-0' : 'opacity-0 max-w-0 -translate-x-4 lg:opacity-100 lg:max-w-[150px] lg:translate-x-0'}
                `}>
                  <span className={`
                    ml-1 font-medium text-sm tracking-wide block
                    ${activeView === item.label ? 'text-white' : 'text-text-secondary dark:text-gray-300 group-hover:text-primary'}
                  `}>
                    {item.label}
                  </span>
                </div>

                {/* Active Indicator Pill for Collapsed State */}
                {!isOpen && activeView === item.label && (
                  <div className="absolute right-1 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-white rounded-full lg:hidden shadow-sm animate-pulse"></div>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-auto">
          <div className="mb-4 px-2 h-5 flex items-center overflow-hidden">
             <p className={`
               text-micro text-text-tertiary dark:text-gray-500 font-semibold uppercase tracking-wider whitespace-nowrap transition-all duration-500
               ${isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 lg:opacity-100 lg:translate-x-0'}
             `}>
              System
            </p>
             <div className={`
               w-4 h-0.5 bg-gray-200 dark:bg-slate-700 rounded-full absolute
               ${isOpen ? 'opacity-0' : 'opacity-100 lg:opacity-0'}
               transition-opacity duration-500
             `}></div>
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