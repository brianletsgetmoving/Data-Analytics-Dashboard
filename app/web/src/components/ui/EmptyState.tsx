import React from 'react';
import { Inbox, Search, Filter } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  type?: 'no-data' | 'no-results' | 'no-permission';
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  message,
  icon,
  action,
  type = 'no-data',
}) => {
  const defaultConfig = {
    'no-data': {
      title: 'No data available',
      message: 'There is no data to display for this view.',
      icon: <Inbox className="w-12 h-12 text-text-tertiary dark:text-gray-500" />,
    },
    'no-results': {
      title: 'No results found',
      message: 'Try adjusting your filters to see more results.',
      icon: <Search className="w-12 h-12 text-text-tertiary dark:text-gray-500" />,
    },
    'no-permission': {
      title: 'Access denied',
      message: 'You do not have permission to view this data.',
      icon: <Filter className="w-12 h-12 text-text-tertiary dark:text-gray-500" />,
    },
  };

  const config = defaultConfig[type];

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="mb-4">
        {icon || config.icon}
      </div>
      <h3 className="text-lg font-semibold text-text-primary dark:text-white mb-2">
        {title || config.title}
      </h3>
      <p className="text-sm text-text-secondary dark:text-gray-400 mb-6 max-w-md">
        {message || config.message}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
};

