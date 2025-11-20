import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = 'Error',
  message,
  onRetry,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200 dark:border-red-800 ${className}`}>
      <AlertCircle className="w-12 h-12 text-danger mb-4" />
      <h3 className="text-lg font-semibold text-red-800 dark:text-red-300 mb-2">
        {title}
      </h3>
      <p className="text-sm text-red-600 dark:text-red-400 mb-4 text-center max-w-md">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-danger text-white rounded-lg hover:bg-danger-dark transition-colors text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
    </div>
  );
};

