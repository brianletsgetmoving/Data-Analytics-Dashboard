import React, { useState, useMemo, memo, Component, ErrorInfo, ReactNode } from 'react';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend, AreaChart, Area,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  TooltipProps
} from 'recharts';
import { CHART_COLORS } from '@/constants';
import { HeatmapPoint, RadarMetric } from '@/shared/types';


// --- Types ---

interface BaseChartProps {
  height?: number;
  isLoading?: boolean;
  className?: string;
}

interface Point {
  x: number;
  y: number;
  [key: string]: any;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}


// --- Performance Utilities ---

/**
 * Largest Triangle Three Buckets (LTTB) Downsampling Algorithm
 * Reduces data points while preserving visual shape and peaks
 * Based on Sveinn Steinarsson's 2013 algorithm
 * 
 * @param data - Array of data points with x and y properties
 * @param threshold - Target number of points (default: 500)
 * @returns Downsampled array maintaining visual fidelity
 */
export function downsampleLTTB<T extends Point>(data: T[], threshold: number = 500): T[] {
  const dataLength = data.length;
  
  // No downsampling needed
  if (threshold >= dataLength || threshold === 0 || dataLength <= 2) {
    return data;
  }

  const sampled: T[] = [];
  const bucketSize = (dataLength - 2) / (threshold - 2);
  
  let a = 0; // Start point index
  sampled.push(data[a]); // Always keep first point

  for (let i = 0; i < threshold - 2; i++) {
    // Calculate average point for next bucket (for area calculation)
    let avgX = 0;
    let avgY = 0;
    let avgRangeStart = Math.floor((i + 1) * bucketSize) + 1;
    let avgRangeEnd = Math.floor((i + 2) * bucketSize) + 1;
    avgRangeEnd = avgRangeEnd < dataLength ? avgRangeEnd : dataLength;
    const avgRangeLength = avgRangeEnd - avgRangeStart;

    for (let j = avgRangeStart; j < avgRangeEnd; j++) {
      avgX += data[j].x;
      avgY += data[j].y;
    }
    avgX /= avgRangeLength;
    avgY /= avgRangeLength;

    // Find point with largest triangle area in current bucket
    const rangeStart = Math.floor(i * bucketSize) + 1;
    const rangeEnd = Math.floor((i + 1) * bucketSize) + 1;
    
    let maxArea = -1;
    let maxAreaPoint: T = data[a];
    
    for (let j = rangeStart; j < rangeEnd; j++) {
      if (j >= dataLength) break;
      
      // Calculate triangle area using cross product
      const area = Math.abs(
        (data[a].x - avgX) * (data[j].y - data[a].y) -
        (data[a].x - data[j].x) * (avgY - data[a].y)
      ) * 0.5;
      
      if (area > maxArea) {
        maxArea = area;
        maxAreaPoint = data[j];
        a = j; // Update reference point
      }
    }
    
    sampled.push(maxAreaPoint);
  }

  sampled.push(data[dataLength - 1]); // Always keep last point
  return sampled;
}

/**
 * Transforms Recharts data format to Point format for LTTB
 * Handles dynamic key mapping for area/line charts
 */
function prepareDataForDownsampling<T extends Record<string, any>>(
  data: T[],
  xKey: string,
  yKey: string
): Point[] {
  return data.map((item, index) => ({
    x: typeof item[xKey] === 'number' ? item[xKey] : index,
    y: item[yKey] || 0,
    originalData: item, // Preserve original data
  }));
}

/**
 * Restores original data format after LTTB downsampling
 */
function restoreOriginalFormat<T>(downsampledPoints: Point[]): T[] {
  return downsampledPoints.map(point => point.originalData as T);
}


// --- Error Boundary ---

/**
 * Chart-specific Error Boundary
 * Isolates chart failures to prevent app-wide crashes
 * Follows best practice of wrapping unstable/external components
 */
class ChartErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to error tracking service (Sentry, LogRocket, etc.)
    console.error('Chart Error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div 
          className="flex flex-col items-center justify-center p-8 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200 dark:border-red-800"
          role="alert"
        >
          <svg className="w-12 h-12 text-red-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-sm font-semibold text-red-800 dark:text-red-300 mb-1">
            Chart failed to load
          </p>
          <p className="text-xs text-red-600 dark:text-red-400">
            {this.state.error?.message || 'Unknown error'}
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}


// --- Shared Components ---

/**
 * Reusable Skeleton Loader
 * Mimics the container size with a subtle pulse animation
 */
const ChartSkeleton: React.FC<{ height: number }> = memo(({ height }) => (
  <div 
    className="w-full bg-gray-50/50 dark:bg-slate-800/50 rounded-xl animate-pulse relative overflow-hidden border border-gray-100 dark:border-slate-700"
    style={{ height }}
    role="status"
    aria-label="Loading chart..."
  >
    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 dark:via-slate-600/40 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
    <div className="absolute bottom-8 left-8 right-8 top-8 flex items-end gap-4 opacity-20">
      <div className="h-[40%] w-full bg-gray-300 dark:bg-slate-600 rounded-t-md" />
      <div className="h-[70%] w-full bg-gray-300 dark:bg-slate-600 rounded-t-md" />
      <div className="h-[50%] w-full bg-gray-300 dark:bg-slate-600 rounded-t-md" />
      <div className="h-[80%] w-full bg-gray-300 dark:bg-slate-600 rounded-t-md" />
    </div>
  </div>
));

ChartSkeleton.displayName = 'ChartSkeleton';


/**
 * Custom Active Dot for Robust Interaction
 * Memoized to prevent re-renders during tooltips
 */
const CustomActiveDot = memo((props: any) => {
  const { cx, cy, stroke, fill, r, payload, onClick } = props;
  
  if (!cx || !cy) return null;

  return (
    <circle
      cx={cx}
      cy={cy}
      r={r || 6}
      stroke={stroke || "#fff"}
      strokeWidth={3}
      fill={fill}
      className="animate-pulse transition-all duration-300"
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      onClick={(e) => {
        e.stopPropagation();
        e.preventDefault();
        if (onClick) onClick(payload);
      }}
    />
  );
});

CustomActiveDot.displayName = 'CustomActiveDot';


/**
 * Shared Glassmorphism Tooltip
 * Handles both Multi-series and Single-series filtering
 * Optimized with useMemo to prevent filtering on every render
 */
interface GlassTooltipProps extends TooltipProps<number, string> {
  filterByKey?: string | null;
}

const GlassTooltip = memo<GlassTooltipProps>(({ active, payload, label, filterByKey }) => {
  // Memoize filtering operation to prevent recalculation on every render
  const displayPayload = useMemo(() => {
    if (!payload || payload.length === 0) return [];
    
    return filterByKey 
      ? payload.filter((entry) => entry.dataKey === filterByKey)
      : payload;
  }, [payload, filterByKey]);

  if (!active || displayPayload.length === 0) return null;

  return (
    <div 
      role="tooltip"
      className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-xl p-4 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-white/50 dark:border-slate-700 z-50 min-w-[180px]"
    >
      {label && (
        <p className="text-xs font-bold text-text-tertiary dark:text-gray-400 uppercase tracking-wider mb-2">
          {label}
        </p>
      )}
      {displayPayload.map((entry: any, index: number) => (
        <div 
          key={`${entry.dataKey}-${index}`}
          className="flex items-center justify-between gap-4 mb-1.5 last:mb-0 group"
        >
          <div className="flex items-center gap-2">
            <div 
              className="w-2 h-2 rounded-full shadow-sm ring-2 ring-white dark:ring-slate-800" 
              style={{ backgroundColor: entry.color || entry.fill }} 
            />
            <span className="text-xs font-medium text-text-secondary dark:text-gray-300">{entry.name}</span>
          </div>
          <span className="font-mono text-sm font-bold text-text-primary dark:text-white tabular-nums">
            {typeof entry.value === 'number' 
              ? entry.value.toLocaleString(undefined, { maximumFractionDigits: 1 }) 
              : entry.value}
            {entry.unit && <span className="text-[10px] text-text-tertiary dark:text-gray-400 ml-0.5">{entry.unit}</span>}
          </span>
        </div>
      ))}
    </div>
  );
});

GlassTooltip.displayName = 'GlassTooltip';


// --- 1. Gradient Area Chart (Optimized) ---

interface AreaTrendChartProps extends BaseChartProps {
  data: any[];
  xKey: string;
  areas: { key: string; name: string; color: string }[];
  onPointClick?: (data: any) => void;
  tooltipMode?: 'shared' | 'single';
  downsampleThreshold?: number; // New: configurable threshold
}

const GradientAreaChartBase: React.FC<AreaTrendChartProps> = ({ 
  data, 
  xKey, 
  areas, 
  height = 300, 
  isLoading = false,
  onPointClick,
  tooltipMode = 'single',
  downsampleThreshold = 500
}) => {
  const [activeDataKey, setActiveDataKey] = useState<string | null>(null);

  // Optimize large datasets with LTTB downsampling
  const optimizedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    if (data.length <= downsampleThreshold) return data;

    // Apply LTTB to first area key (primary metric)
    const primaryKey = areas[0]?.key;
    if (!primaryKey) return data;

    const pointsData = prepareDataForDownsampling(data, xKey, primaryKey);
    const downsampled = downsampleLTTB(pointsData, downsampleThreshold);
    return restoreOriginalFormat(downsampled);
  }, [data, xKey, areas, downsampleThreshold]);

  if (isLoading) return <ChartSkeleton height={height} />;
  if (!optimizedData || optimizedData.length === 0) {
    return (
      <div 
        className="flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm" 
        style={{ height }}
        role="status"
      >
        No data available
      </div>
    );
  }

  const areasDescription = areas.map(a => a.name).join(', ');

  return (
    <div 
      role="img"
      aria-label={`Area chart displaying ${areasDescription} trends over time`}
    >
      <ResponsiveContainer 
        width="100%" 
        height={height}
      >
        <AreaChart 
        data={optimizedData} 
        margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        onMouseLeave={() => setActiveDataKey(null)}
      >
        <defs>
          {areas.map((area) => (
            <linearGradient key={area.key} id={`color-${area.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={area.color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={area.color} stopOpacity={0}/>
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(15,23,42,0.04)" />
        <XAxis 
          dataKey={xKey} 
          axisLine={false} 
          tickLine={false} 
          tick={{ fill: 'rgba(17, 24, 39, 0.4)', fontSize: 10, fontWeight: 600 }} 
          dy={10}
        />
        <YAxis 
          axisLine={false} 
          tickLine={false} 
          tick={{ fill: 'rgba(17, 24, 39, 0.4)', fontSize: 10, fontWeight: 600 }}
          tickFormatter={(val) => val >= 1000 ? `${val/1000}k` : val}
        />
        <Tooltip 
          content={<GlassTooltip filterByKey={tooltipMode === 'single' ? activeDataKey : null} />}
          cursor={{ stroke: '#6D5BFF', strokeWidth: 1, strokeDasharray: '4 4' }}
          animationDuration={150}
          wrapperStyle={{ outline: 'none', zIndex: 1000 }}
        />
        {areas.map((area) => (
          <Area
            key={area.key}
            type="monotone"
            dataKey={area.key}
            name={area.name}
            stroke={area.color}
            strokeWidth={3}
            fillOpacity={1}
            fill={`url(#color-${area.key})`}
            onMouseEnter={() => setActiveDataKey(area.key)}
            activeDot={
              (tooltipMode === 'shared' || activeDataKey === null || activeDataKey === area.key)
                ? (props) => <CustomActiveDot {...props} onClick={onPointClick} fill={area.color} />
                : false
            }
            isAnimationActive={optimizedData.length < 100} // Disable animation for large datasets
          />
        ))}
      </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// Export with memoization and custom equality check
export const GradientAreaChart = memo(GradientAreaChartBase, (prevProps, nextProps) => {
  return (
    prevProps.data === nextProps.data &&
    prevProps.areas === nextProps.areas &&
    prevProps.isLoading === nextProps.isLoading &&
    prevProps.height === nextProps.height &&
    prevProps.tooltipMode === nextProps.tooltipMode
  );
});

GradientAreaChart.displayName = 'GradientAreaChart';


// --- 2. Metric Bar Chart (Optimized) ---

interface MetricBarChartProps extends BaseChartProps {
  data: any[];
  xKey: string;
  bars: { key: string; name: string; color: string }[];
  layout?: 'vertical' | 'horizontal';
  onBarClick?: (data: any) => void;
}

const MetricBarChartBase: React.FC<MetricBarChartProps> = ({ 
  data, 
  xKey, 
  bars, 
  height = 300, 
  layout = 'horizontal', 
  isLoading = false, 
  onBarClick 
}) => {
  
  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm" 
        style={{ height }}
        role="status"
      >
        No data available
      </div>
    );
  }

  const barsDescription = bars.map(b => b.name).join(', ');

  return (
    <div 
      role="img"
      aria-label={`Bar chart comparing ${barsDescription} across categories`}
    >
      <ResponsiveContainer 
        width="100%" 
        height={height}
      >
        <BarChart 
        data={data} 
        layout={layout}
        margin={layout === 'vertical' ? { left: 20, right: 30 } : { left: -20, right: 0 }}
        barSize={layout === 'vertical' ? 12 : 32}
      >
        <CartesianGrid 
          strokeDasharray="3 3" 
          horizontal={layout === 'horizontal'} 
          vertical={layout === 'vertical'} 
          stroke="rgba(15,23,42,0.04)" 
        />
        
        {layout === 'horizontal' ? (
          <>
            <XAxis 
              dataKey={xKey} 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'rgba(17, 24, 39, 0.4)', fontSize: 10, fontWeight: 600 }} 
              dy={10} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'rgba(17, 24, 39, 0.4)', fontSize: 10, fontWeight: 600 }} 
              tickFormatter={(val) => val >= 1000 ? `${val/1000}k` : val} 
            />
          </>
        ) : (
          <>
            <XAxis type="number" hide />
            <YAxis 
              dataKey={xKey} 
              type="category" 
              axisLine={false} 
              tickLine={false} 
              width={80} 
              tick={{ fill: 'rgba(17, 24, 39, 0.6)', fontSize: 11, fontWeight: 500 }} 
            />
          </>
        )}

        <Tooltip 
          content={<GlassTooltip />} 
          cursor={{ fill: 'rgba(109,91,255, 0.04)' }} 
          animationDuration={150}
          wrapperStyle={{ outline: 'none', zIndex: 1000 }}
        />
        {bars.map((bar) => (
          <Bar 
            key={bar.key}
            dataKey={bar.key} 
            name={bar.name}
            fill={bar.color}
            radius={layout === 'horizontal' ? [6, 6, 2, 2] : [0, 6, 6, 0]}
            onClick={onBarClick ? (data) => onBarClick(data) : undefined}
            cursor={onBarClick ? "pointer" : "default"}
            className="transition-all duration-300 hover:opacity-80"
            isAnimationActive={data.length < 50}
          />
        ))}
      </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const MetricBarChart = memo(MetricBarChartBase, (prevProps, nextProps) => {
  return (
    prevProps.data === nextProps.data &&
    prevProps.bars === nextProps.bars &&
    prevProps.isLoading === nextProps.isLoading &&
    prevProps.layout === nextProps.layout
  );
});

MetricBarChart.displayName = 'MetricBarChart';


// --- 3. Donut Chart (Optimized) ---

interface DonutChartProps extends BaseChartProps {
  data: any[];
  onSliceClick?: (data: any) => void;
}

const DonutChartBase: React.FC<DonutChartProps> = ({ data, height = 300, isLoading = false, onSliceClick }) => {
  const total = useMemo(() => 
    data?.reduce((sum, item) => sum + (item.value || 0), 0) || 0, 
    [data]
  );

  // Memoize accessibility description
  const ariaLabel = useMemo(() => {
    if (!data || data.length === 0) return 'Empty pie chart';
    const distribution = data.map(d => `${d.name}: ${d.value}`).join(', ');
    return `Pie chart showing distribution - ${distribution}. Total: ${total}`;
  }, [data, total]);

  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm" 
        style={{ height }}
        role="status"
      >
        No data available
      </div>
    );
  }

  const handleKeyDown = (e: React.KeyboardEvent, sliceData: any) => {
    if ((e.key === 'Enter' || e.key === ' ') && onSliceClick) {
      e.preventDefault();
      onSliceClick(sliceData);
    }
  };

  return (
    <div 
      className="relative flex items-center justify-center" 
      style={{ height }}
      role="img"
      aria-label={ariaLabel}
    >
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={height / 3.5}
            outerRadius={height / 2.5}
            paddingAngle={4}
            dataKey="value"
            onClick={onSliceClick}
            cursor={onSliceClick ? "pointer" : "default"}
            stroke="none"
            isAnimationActive={data.length < 20}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color || CHART_COLORS[index % CHART_COLORS.length]} 
                className="hover:opacity-80 transition-opacity"
                tabIndex={onSliceClick ? 0 : undefined}
                onKeyDown={onSliceClick ? (e: any) => handleKeyDown(e, entry) : undefined}
              />
            ))}
          </Pie>
          <Tooltip 
            content={<GlassTooltip />} 
            animationDuration={150}
            wrapperStyle={{ outline: 'none', zIndex: 1000 }}
          />
          <Legend 
            verticalAlign="bottom" 
            iconType="circle" 
            iconSize={8} 
            wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} 
          />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Center Text */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 -mt-4 text-center pointer-events-none">
        <span className="block text-2xl font-bold text-text-primary dark:text-white">
          {total >= 1000 ? `${(total/1000).toFixed(1)}k` : total}
        </span>
        <span className="text-[10px] text-text-tertiary dark:text-gray-400 font-semibold uppercase tracking-widest">
          Total
        </span>
      </div>
    </div>
  );
};

export const DonutChart = memo(DonutChartBase, (prevProps, nextProps) => {
  return (
    prevProps.data === nextProps.data &&
    prevProps.isLoading === nextProps.isLoading &&
    prevProps.height === nextProps.height
  );
});

DonutChart.displayName = 'DonutChart';


// --- 4. Skill Radar Chart (Optimized) ---

interface SkillRadarChartProps extends BaseChartProps {
  data: RadarMetric[];
}

const SkillRadarChartBase: React.FC<SkillRadarChartProps> = ({ data, height = 300, isLoading = false }) => {
  
  // Memoize accessibility description
  const ariaLabel = useMemo(() => {
    if (!data || data.length === 0) return 'Empty radar chart';
    const metrics = data.map(d => `${d.subject}: Agent ${d.A}, Team ${d.B}`).join(', ');
    return `Radar chart comparing performance metrics - ${metrics}`;
  }, [data]);

  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm" 
        style={{ height }}
        role="status"
      >
        No data available
      </div>
    );
  }

  return (
    <div 
      role="img"
      aria-label={ariaLabel}
    >
      <ResponsiveContainer 
        width="100%" 
        height={height}
      >
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
        <PolarGrid stroke="rgba(15,23,42,0.06)" />
        <PolarAngleAxis 
          dataKey="subject" 
          tick={{ fill: 'rgba(17, 24, 39, 0.5)', fontSize: 10, fontWeight: 600 }} 
        />
        <PolarRadiusAxis 
          angle={30} 
          domain={[0, 150]} 
          tick={false} 
          axisLine={false} 
        />
        
        <Radar
          name="Agent"
          dataKey="A"
          stroke={CHART_COLORS[0]}
          strokeWidth={2}
          fill={CHART_COLORS[0]}
          fillOpacity={0.3}
          isAnimationActive={false}
        />
        <Radar
          name="Team Avg"
          dataKey="B"
          stroke={CHART_COLORS[4]}
          strokeWidth={2}
          fill={CHART_COLORS[4]}
          fillOpacity={0.1}
          isAnimationActive={false}
        />
        <Tooltip 
          content={<GlassTooltip />} 
          animationDuration={150}
          wrapperStyle={{ outline: 'none', zIndex: 1000 }}
        />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
      </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const SkillRadarChart = memo(SkillRadarChartBase, (prevProps, nextProps) => {
  return (
    prevProps.data === nextProps.data &&
    prevProps.isLoading === nextProps.isLoading
  );
});

SkillRadarChart.displayName = 'SkillRadarChart';


// --- 5. Density Heatmap (Optimized) ---

interface DensityHeatmapProps extends BaseChartProps {
  data: HeatmapPoint[];
  xAxisLabels: string[];
  yAxisLabels: string[];
}

const DensityHeatmapBase: React.FC<DensityHeatmapProps> = ({ 
  data, 
  xAxisLabels, 
  yAxisLabels, 
  isLoading = false 
}) => {
  
  // 1. Optimize Data Access: Transform array to Map for O(1) access
  const dataMap = useMemo(() => {
    const map = new Map<string, number>();
    if (!data) return map;
    data.forEach(d => map.set(`${d.x}-${d.y}`, d.value));
    return map;
  }, [data]);

  // 2. Dynamic Scale: Calculate max value to determine relative intensity
  const maxValue = useMemo(() => {
    if (!data || data.length === 0) return 100;
    return Math.max(...data.map(d => d.value));
  }, [data]);

  // Memoize getValue function
  const getValue = useMemo(() => {
    return (x: string, y: string) => dataMap.get(`${x}-${y}`) || 0;
  }, [dataMap]);

  // 3. Dynamic Coloring: Assigns color based on percentage of max value (Quintiles)
  const getColor = useMemo(() => {
    return (value: number) => {
      if (value === 0) return 'bg-gray-50 dark:bg-slate-800';
      const percentage = value / maxValue;
      
      if (percentage < 0.2) return 'bg-primary/5';
      if (percentage < 0.4) return 'bg-primary/20';
      if (percentage < 0.6) return 'bg-primary/40';
      if (percentage < 0.8) return 'bg-primary/60';
      return 'bg-primary';
    };
  }, [maxValue]);

  if (isLoading) return <ChartSkeleton height={300} />;

  return (
    <div className="overflow-x-auto w-full" role="img" aria-label="Activity heatmap showing patterns across days and hours">
      <div className="min-w-[500px] flex flex-col">
        {/* X-Axis Labels */}
        <div className="flex mb-2 ml-12">
          {xAxisLabels.map(day => (
            <div 
              key={day} 
              className="flex-1 text-center text-[10px] font-semibold text-text-tertiary dark:text-gray-400 uppercase"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Grid */}
        <div className="flex flex-col gap-1" role="grid" aria-label="Activity Heatmap">
          {yAxisLabels.map(hour => (
            <div key={hour} className="flex items-center gap-1" role="row">
              {/* Y-Axis Label */}
              <div className="w-12 text-[10px] font-medium text-text-tertiary dark:text-gray-400 text-right pr-3">
                {hour}
              </div>
              {/* Cells */}
              {xAxisLabels.map(day => {
                const val = getValue(day, hour);
                return (
                  <div 
                    key={`${day}-${hour}`}
                    role="gridcell"
                    aria-label={`${day} ${hour}: ${val} Activity`}
                    tabIndex={0}
                    className={`flex-1 h-8 rounded-md transition-all hover:scale-105 hover:shadow-md relative group cursor-default outline-none focus:ring-2 focus:ring-primary/50 ${getColor(val)}`}
                  >
                    {/* Custom Tooltip for Grid Cell */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-slate-700 text-white text-[10px] rounded pointer-events-none whitespace-nowrap z-20 shadow-lg">
                      {day} {hour}: <span className="font-bold">{val}</span> Activity
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex items-center justify-end gap-2 mt-4 text-[10px] text-text-tertiary dark:text-gray-400">
        <span>Low</span>
        <div className="flex gap-1" aria-hidden="true">
           <div className="w-3 h-3 rounded bg-gray-50 dark:bg-slate-800 border border-gray-100 dark:border-slate-700"></div>
           <div className="w-3 h-3 rounded bg-primary/20"></div>
           <div className="w-3 h-3 rounded bg-primary/60"></div>
           <div className="w-3 h-3 rounded bg-primary"></div>
        </div>
        <span>High</span>
      </div>
    </div>
  );
};

export const DensityHeatmap = memo(DensityHeatmapBase, (prevProps, nextProps) => {
  return (
    prevProps.data === nextProps.data &&
    prevProps.xAxisLabels === nextProps.xAxisLabels &&
    prevProps.yAxisLabels === nextProps.yAxisLabels &&
    prevProps.isLoading === nextProps.isLoading
  );
});

DensityHeatmap.displayName = 'DensityHeatmap';


// --- Error Boundary Wrapped Exports ---

/**
 * Production-ready chart exports with error boundaries
 * Prevents chart failures from crashing the entire application
 */

export const SafeGradientAreaChart: React.FC<AreaTrendChartProps> = (props) => (
  <ChartErrorBoundary>
    <GradientAreaChart {...props} />
  </ChartErrorBoundary>
);

export const SafeMetricBarChart: React.FC<MetricBarChartProps> = (props) => (
  <ChartErrorBoundary>
    <MetricBarChart {...props} />
  </ChartErrorBoundary>
);

export const SafeDonutChart: React.FC<DonutChartProps> = (props) => (
  <ChartErrorBoundary>
    <DonutChart {...props} />
  </ChartErrorBoundary>
);

export const SafeSkillRadarChart: React.FC<SkillRadarChartProps> = (props) => (
  <ChartErrorBoundary>
    <SkillRadarChart {...props} />
  </ChartErrorBoundary>
);

export const SafeDensityHeatmap: React.FC<DensityHeatmapProps> = (props) => (
  <ChartErrorBoundary>
    <DensityHeatmap {...props} />
  </ChartErrorBoundary>
);
