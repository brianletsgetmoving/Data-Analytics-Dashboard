import { useHeatmapQuery } from '@/hooks/useAnalytics';
// Using custom table implementation for heatmap visualization
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import type { ActivityHeatmap as ActivityHeatmapType } from '@/shared/types';

function ActivityHeatmap() {
  const { data, isLoading, error } = useHeatmapQuery();

  if (error) {
    return (
      <div className="neo-card">
        <p className="text-red-500">Error loading heatmap data</p>
      </div>
    );
  }

  // Transform data for Recharts heatmap
  const heatmapData = data?.data?.reduce((acc: Record<string, Record<string, number>>, item: ActivityHeatmapType) => {
    if (!acc[item.branch_name]) {
      acc[item.branch_name] = {};
    }
    acc[item.branch_name][item.month] = item.value ?? 0;
    return acc;
  }, {}) || {};

  const branches = Object.keys(heatmapData);
  const months = Array.from(
    new Set(
      data?.data?.map((item: ActivityHeatmapType) => item.month) || []
    )
  ).sort();

  // Calculate max value for color scaling
  const maxValue = Math.max(
    ...(data?.data?.map((item: ActivityHeatmapType) => item.value ?? 0) || [0])
  );

  const getColorIntensity = (value: number): string => {
    if (value === 0) return '#f0f0f3';
    const intensity = Math.min(value / maxValue, 1);
    const hue = 200 + (1 - intensity) * 160; // Blue to purple gradient
    return `hsl(${hue}, 70%, ${50 + intensity * 30}%)`;
  };

  return (
    <div className="neo-card">
      <h2 className="text-xl font-bold neo-text-primary mb-4">Activity Heatmap</h2>
      
      {isLoading ? (
        <SkeletonLoader height={400} variant="card" />
      ) : (
        <div className="neo-glass" style={{ height: '400px', overflow: 'auto' }}>
          <div className="overflow-x-auto h-full">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="p-2 text-left text-sm font-medium neo-text-secondary sticky left-0 bg-white z-10">
                      Branch
                    </th>
                    {months.map((month) => (
                      <th
                        key={month}
                        className="p-2 text-center text-xs font-medium neo-text-secondary min-w-[80px]"
                      >
                        {month}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {branches.map((branch) => (
                    <tr key={branch}>
                      <td className="p-2 text-sm font-medium neo-text-primary sticky left-0 bg-white z-10 border-r">
                        {branch}
                      </td>
                      {months.map((month) => {
                        const value = heatmapData[branch]?.[month] ?? 0;
                        return (
                          <td
                            key={month}
                            className="p-2 text-center text-xs"
                            style={{
                              backgroundColor: getColorIntensity(value),
                            }}
                            title={`${branch} - ${month}: $${value.toLocaleString()}`}
                          >
                            {value > 0 ? (
                              <span className="neo-text-primary">
                                ${(value / 1000).toFixed(0)}k
                              </span>
                            ) : (
                              '-'
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ActivityHeatmap;

