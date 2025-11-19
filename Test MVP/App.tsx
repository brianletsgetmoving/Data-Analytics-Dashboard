import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DateRangeFilter } from './components/DateRangeFilter';
import { ViewType } from './types';

// Views
import { OverviewView } from './components/views/OverviewView';
import { RevenueView } from './components/views/RevenueView';
import { CustomersView } from './components/views/CustomersView';
import { JobsView } from './components/views/JobsView';
import { SalesView } from './components/views/SalesView';

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('Overview');

  const renderView = () => {
    switch (currentView) {
      case 'Overview': return <OverviewView />;
      case 'Revenue': return <RevenueView />;
      case 'Customers': return <CustomersView />;
      case 'Jobs': return <JobsView />;
      case 'Sales Performance': return <SalesView />;
      default: return <OverviewView />;
    }
  };

  return (
    <div className="min-h-screen flex bg-bg-canvas dark:bg-slate-950 lg:bg-transparent lg:dark:bg-transparent lg:bg-[linear-gradient(12deg,#2D5BFF_0%,#7B4CFF_100%)]">
      
      {/* Responsive Sidebar */}
      <Sidebar 
        activeView={currentView} 
        onViewChange={setCurrentView}
        isOpen={isSidebarOpen}
      />

      {/* Main Content Wrapper */}
      <div className="flex-1 flex flex-col pl-[80px] lg:pl-[260px] transition-all duration-300 min-h-screen">
        
        <main 
          className="flex-1 flex flex-col lg:m-6 lg:rounded-[32px] lg:shadow-2xl overflow-hidden bg-bg-canvas dark:bg-slate-950 lg:bg-[#F4F6FB] lg:dark:bg-slate-900 relative transition-colors duration-300"
          style={{ height: 'calc(100vh - 48px)' }} // Adjust for margin on desktop
        >
          <Header onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)} />

          <div className="flex-1 overflow-y-auto p-6 lg:p-8 custom-scrollbar">
            
            {/* Page Actions Row */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6">
              <div>
                <h1 className="text-2xl font-bold text-text-primary dark:text-white mb-1">{currentView}</h1>
                <p className="text-sm text-text-secondary dark:text-gray-400">
                  {currentView === 'Overview' && "Welcome back, here's what's happening today."}
                  {currentView === 'Revenue' && "Track your financial performance and growth."}
                  {currentView === 'Customers' && "Analyze customer demographics and behavior."}
                  {currentView === 'Jobs' && "Monitor job volume, status, and operational efficiency."}
                  {currentView === 'Sales Performance' && "Evaluate agent performance and sales rankings."}
                </p>
              </div>
              
              {/* Date Range Filter Integration */}
              <div className="w-full md:w-auto z-10">
                <DateRangeFilter />
              </div>
            </div>

            {/* View Content */}
            {renderView()}
            
            <footer className="mt-12 text-center text-xs text-text-tertiary dark:text-gray-500 pb-4">
              &copy; 2024 SmartMove CRM Analytics V5. All rights reserved.
            </footer>

          </div>
        </main>
      </div>
    </div>
  );
}