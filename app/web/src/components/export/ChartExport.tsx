import React from 'react';
import { Download, Image, FileText } from 'lucide-react';

interface ChartExportProps {
  chartId?: string;
  chartTitle?: string;
  onExportPNG?: () => void;
  onExportCSV?: () => void;
  onExportPDF?: () => void;
}

export const ChartExport: React.FC<ChartExportProps> = ({
  chartId,
  chartTitle = 'Chart',
  onExportPNG,
  onExportCSV,
  onExportPDF,
}) => {
  const handleExportPNG = async () => {
    if (onExportPNG) {
      onExportPNG();
      return;
    }

    if (!chartId) return;

    try {
      const chartElement = document.getElementById(chartId);
      if (!chartElement) return;

      // Use html2canvas if available, otherwise fallback
      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(chartElement);
      const url = canvas.toDataURL('image/png');
      
      const link = document.createElement('a');
      link.download = `${chartTitle}-${new Date().toISOString().split('T')[0]}.png`;
      link.href = url;
      link.click();
    } catch (error) {
      console.error('Failed to export PNG:', error);
    }
  };

  const handleExportCSV = () => {
    if (onExportCSV) {
      onExportCSV();
    }
  };

  const handleExportPDF = () => {
    if (onExportPDF) {
      onExportPDF();
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleExportPNG}
        className="p-2 text-text-tertiary dark:text-gray-400 hover:text-primary dark:hover:text-primary hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg transition-colors"
        title="Export as PNG"
      >
        <Image className="w-4 h-4" />
      </button>
      <button
        onClick={handleExportCSV}
        className="p-2 text-text-tertiary dark:text-gray-400 hover:text-primary dark:hover:text-primary hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg transition-colors"
        title="Export as CSV"
      >
        <FileText className="w-4 h-4" />
      </button>
      <button
        onClick={handleExportPDF}
        className="p-2 text-text-tertiary dark:text-gray-400 hover:text-primary dark:hover:text-primary hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg transition-colors"
        title="Export as PDF"
      >
        <Download className="w-4 h-4" />
      </button>
    </div>
  );
};

