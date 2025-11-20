import React from 'react';
import { X, ArrowLeft, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface DrillDownPanelProps {
  title: string;
  subtitle?: string;
  data: any;
  onClose: () => void;
  onNavigate?: (path: string) => void;
}

export const DrillDownPanel: React.FC<DrillDownPanelProps> = ({
  title,
  subtitle,
  data,
  onClose,
  onNavigate,
}) => {
  const navigate = useNavigate();

  const handleNavigate = (path: string) => {
    if (onNavigate) {
      onNavigate(path);
    } else {
      navigate(path);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center animate-in fade-in duration-200">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-800/50">
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-text-secondary dark:text-gray-300" />
            </button>
            <div>
              <h2 className="text-xl font-semibold text-text-primary dark:text-white">{title}</h2>
              {subtitle && (
                <p className="text-sm text-text-secondary dark:text-gray-400 mt-1">{subtitle}</p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-text-tertiary dark:text-gray-400 hover:text-text-primary dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)] custom-scrollbar">
          <div className="space-y-6">
            {Object.entries(data).map(([key, value]) => (
              <div key={key} className="border-b border-gray-100 dark:border-slate-700 pb-4 last:border-0">
                <div className="text-xs font-semibold text-text-tertiary dark:text-gray-400 uppercase tracking-wider mb-2">
                  {key.replace(/_/g, ' ')}
                </div>
                <div className="text-sm text-text-primary dark:text-white">
                  {typeof value === 'object' && value !== null ? (
                    <pre className="bg-gray-50 dark:bg-slate-800 p-3 rounded-lg overflow-x-auto text-xs">
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  ) : (
                    String(value ?? 'N/A')
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-800/50 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-200 dark:border-slate-600 text-text-secondary dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors text-sm font-medium"
          >
            Close
          </button>
          {onNavigate && (
            <button
              onClick={() => handleNavigate(`/detail/${data.id || ''}`)}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors text-sm font-medium flex items-center gap-2"
            >
              View Full Details
              <ExternalLink className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

