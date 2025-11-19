import { useState } from 'react';
import { useRadarChartQuery } from '@/hooks/useAnalytics';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import type { SalesRadar } from '@/shared/types';

function PerformanceRadar() {
  const [dimension, setDimension] = useState<'customer' | 'salesperson' | 'branch'>('customer');
  
  const { data, isLoading, error } = useRadarChartQuery(dimension);

  if (error) {
    return (
      <div className="neo-card">
        <p className="text-red-500">Error loading radar chart data</p>
      </div>
    );
  }

  const radarData = data?.data?.map((item: SalesRadar) => ({
    subject: item.subject,
    value: item.value ?? 0,
    fullMark: item.full_mark ?? 100,
  })) || [];

  // Normalize values to 0-100 scale if fullMark is provided
  const normalizedData = radarData.map((item) => ({
    ...item,
    value: item.fullMark > 0 ? (item.value / item.fullMark) * 100 : item.value,
  }));

  return (
    <div className="neo-card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold neo-text-primary">Performance Radar</h2>
        <div className="flex gap-2">
          {(['customer', 'salesperson', 'branch'] as const).map((dim) => (
            <button
              key={dim}
              onClick={() => setDimension(dim)}
              className={`neo-button ${
                dimension === dim ? 'neo-button-primary' : ''
              }`}
              style={{ padding: '8px 16px', fontSize: '14px' }}
              aria-label={`Select ${dim} dimension`}
            >
              {dim.charAt(0).toUpperCase() + dim.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <SkeletonLoader height={400} variant="card" />
      ) : (
        <div className="neo-glass" style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={normalizedData}>
              <PolarGrid stroke="rgba(0,0,0,0.1)" />
              <PolarAngleAxis 
                dataKey="subject" 
                tick={{ fill: '#4a4a4a', fontSize: 12 }}
              />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]}
                tick={{ fill: '#4a4a4a', fontSize: 10 }}
              />
              <Radar
                name="Performance"
                dataKey="value"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.6}
                strokeWidth={2}
              />
              <Tooltip 
                formatter={(value: number) => `${value.toFixed(1)}%`}
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid rgba(0,0,0,0.1)',
                  borderRadius: '8px',
                }}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default PerformanceRadar;

