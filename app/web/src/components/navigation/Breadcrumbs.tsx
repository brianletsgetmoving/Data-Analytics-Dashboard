import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { ViewType, VIEW_CONFIG } from '@/constants';
import { ViewType as SharedViewType } from '@/shared/types';

interface BreadcrumbItem {
  label: string;
  path: string;
}

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', path: '/' },
  ];

  if (pathSegments.length > 0) {
    const viewPath = pathSegments[0];
    const viewType = viewPath === 'overview' || viewPath === ''
      ? 'Overview'
      : viewPath.split('-').map(
          (word) => word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ') as ViewType;
    
    const viewConfig = VIEW_CONFIG[viewType as SharedViewType];
    if (viewConfig) {
      breadcrumbs.push({
        label: viewType,
        path: `/${viewPath}`,
      });
    }

    // Add additional segments if present (for drill-down views)
    if (pathSegments.length > 1) {
      pathSegments.slice(1).forEach((segment, index) => {
        breadcrumbs.push({
          label: segment.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
          path: `/${pathSegments.slice(0, index + 2).join('/')}`,
        });
      });
    }
  }

  return (
    <nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
      <ol className="flex items-center gap-2">
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === breadcrumbs.length - 1;
          
          return (
            <li key={crumb.path} className="flex items-center gap-2">
              {index === 0 ? (
                <Link
                  to={crumb.path}
                  className="flex items-center gap-1 text-text-tertiary dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors"
                >
                  <Home className="w-4 h-4" />
                </Link>
              ) : (
                <>
                  <ChevronRight className="w-4 h-4 text-text-tertiary dark:text-gray-500" />
                  {isLast ? (
                    <span className="font-medium text-text-primary dark:text-white">
                      {crumb.label}
                    </span>
                  ) : (
                    <Link
                      to={crumb.path}
                      className="text-text-secondary dark:text-gray-300 hover:text-primary dark:hover:text-primary transition-colors"
                    >
                      {crumb.label}
                    </Link>
                  )}
                </>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

