import { ReactNode, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { DateRangeFilter } from '../filters/DateRangeFilter';
import { Breadcrumbs } from '../navigation/Breadcrumbs';
import { ViewSwitcher } from '../navigation/ViewSwitcher';
import { MobileMenu } from '../responsive/MobileMenu';
import { SkipLink } from '../accessibility/SkipLink';
import { useAppKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { VIEW_CONFIG } from '@/constants';
import { ViewType } from '@/shared/types';

interface LayoutProps {
  children: ReactNode;
}

function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  
  // Enable keyboard shortcuts
  useAppKeyboardShortcuts();
  
  const currentView = location.pathname.split('/').filter(Boolean)[0] || 'overview';
  const viewType = currentView === '' 
    ? 'Overview' 
    : currentView.split('-').map(
        (word) => word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ') as ViewType;
  
  const viewConfig = VIEW_CONFIG[viewType] || VIEW_CONFIG['Overview'];

  return (
    <>
      <SkipLink />
      <div className="min-h-screen flex bg-bg-canvas dark:bg-slate-950 lg:bg-transparent lg:dark:bg-transparent lg:bg-[linear-gradient(12deg,#2D5BFF_0%,#7B4CFF_100%)]">
      
      {/* Responsive Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      {/* Mobile Menu */}
      <MobileMenu 
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Wrapper */}
      <div className="flex-1 flex flex-col pl-[80px] lg:pl-[260px] transition-all duration-300 min-h-screen">
        
        <main 
          className="flex-1 flex flex-col lg:m-6 lg:rounded-[32px] lg:shadow-2xl overflow-hidden bg-bg-canvas dark:bg-slate-950 lg:bg-[#F4F6FB] lg:dark:bg-slate-900 relative transition-colors duration-300"
          style={{ height: 'calc(100vh - 48px)' }}
        >
          <Header onMenuClick={() => {
            if (window.innerWidth < 1024) {
              setIsMobileMenuOpen(!isMobileMenuOpen);
            } else {
              setIsSidebarOpen(!isSidebarOpen);
            }
          }} />

          <div id="main-content" className="flex-1 overflow-y-auto p-6 lg:p-8 custom-scrollbar">
            
            {/* Breadcrumbs */}
            <div className="mb-4">
              <Breadcrumbs />
            </div>

            {/* Page Actions Row */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl font-bold text-text-primary dark:text-white">{viewType}</h1>
                  <ViewSwitcher className="hidden lg:block" />
                </div>
                <p className="text-sm text-text-secondary dark:text-gray-400">
                  {viewConfig.description}
                </p>
              </div>
              
              {/* Date Range Filter Integration */}
              <div className="w-full md:w-auto z-10 flex items-center gap-3">
                <DateRangeFilter />
              </div>
            </div>

            {/* View Content */}
            {children}
            
            <footer className="mt-12 text-center text-xs text-text-tertiary dark:text-gray-500 pb-4">
              &copy; 2024 SmartMove CRM Analytics V5. All rights reserved.
            </footer>

          </div>
        </main>
      </div>
      </div>
    </>
  );
}

export default Layout;

