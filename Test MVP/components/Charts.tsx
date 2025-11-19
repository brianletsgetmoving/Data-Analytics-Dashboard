import React, { useState, useCallback, useMemo, memo } from 'react';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend, AreaChart, Area,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  TooltipProps
} from 'recharts';
import { CHART_COLORS } from '../constants'; // Ensure this exists in your project
import { HeatmapPoint, RadarMetric } from '../types'; // Ensure this exists in your project

// --- Types ---

interface BaseChartProps {
  height?: number;
  isLoading?: boolean;
  className?: string;
}

// --- Shared Components ---

/**
 * Reusable Skeleton Loader
 * Mimics the container size with a subtle pulse animation
 */
const ChartSkeleton: React.FC<{ height: number }> = ({ height }) => (
  <div 
    className="w-full bg-gray-50/50 rounded-xl animate-pulse relative overflow-hidden border border-gray-100"
    style={{ height }}
  >
    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
    <div className="absolute bottom-8 left-8 right-8 top-8 flex items-end gap-4 opacity-20">
      <div className="h-[40%] w-full bg-gray-300 rounded-t-md" />
      <div className="h-[70%] w-full bg-gray-300 rounded-t-md" />
      <div className="h-[50%] w-full bg-gray-300 rounded-t-md" />
      <div className="h-[80%] w-full bg-gray-300 rounded-t-md" />
    </div>
  </div>
);

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

/**
 * Shared Glassmorphism Tooltip
 * Handles both Multi-series and Single-series filtering
 */
interface GlassTooltipProps extends TooltipProps<any, any> {
  filterByKey?: string | null;
}

const GlassTooltip = ({ active, payload, label, filterByKey }: GlassTooltipProps) => {
  if (!active || !payload || payload.length === 0) return null;

  // If a specific key is focused (for Area chart specific hover), filter the payload
  const displayPayload = filterByKey 
    ? payload.filter((entry) => entry.dataKey === filterByKey)
    : payload;

  if (displayPayload.length === 0) return null;

  return (
    <div 
      role="status"
      className="bg-white/80 backdrop-blur-xl p-4 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-white/50 z-50 min-w-[180px]"
    >
      {label && (
        <p className="text-xs font-bold text-text-tertiary uppercase tracking-wider mb-2">
          {label}
        </p>
      )}
      {displayPayload.map((entry: any, index: number) => (
        <div 
          key={index} 
          className="flex items-center justify-between gap-4 mb-1.5 last:mb-0 group"
        >
          <div className="flex items-center gap-2">
            <div 
              className="w-2 h-2 rounded-full shadow-sm ring-2 ring-white" 
              style={{ backgroundColor: entry.color || entry.fill }} 
            />
            <span className="text-xs font-medium text-text-secondary">{entry.name}</span>
          </div>
          <span className="font-mono text-sm font-bold text-text-primary tabular-nums">
            {typeof entry.value === 'number' 
              ? entry.value.toLocaleString(undefined, { maximumFractionDigits: 1 }) 
              : entry.value}
            {entry.unit && <span className="text-[10px] text-text-tertiary ml-0.5">{entry.unit}</span>}
          </span>
        </div>
      ))}
    </div>
  );
};

// --- 1. Gradient Area Chart ---

interface AreaTrendChartProps extends BaseChartProps {
  data: any[];
  xKey: string;
  areas: { key: string; name: string; color: string }[];
  onPointClick?: (data: any) => void;
  tooltipMode?: 'shared' | 'single';
}

export const GradientAreaChart: React.FC<AreaTrendChartProps> = ({ 
  data, 
  xKey, 
  areas, 
  height = 300, 
  isLoading = false,
  onPointClick,
  tooltipMode = 'single'
}) => {
  const [activeDataKey, setActiveDataKey] = useState<string | null>(null);

  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) return <div className="flex items-center justify-center text-gray-400 text-sm" style={{ height }}>No data available</div>;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart 
        data={data} 
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
          trigger="hover"
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
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
};

// --- 2. Metric Bar Chart ---

interface MetricBarChartProps extends BaseChartProps {
  data: any[];
  xKey: string;
  bars: { key: string; name: string; color: string }[];
  layout?: 'vertical' | 'horizontal';
  onBarClick?: (data: any) => void;
}

export const MetricBarChart: React.FC<MetricBarChartProps> = ({ 
  data, xKey, bars, height = 300, layout = 'horizontal', isLoading = false, onBarClick 
}) => {
  
  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) return <div className="flex items-center justify-center text-gray-400 text-sm" style={{ height }}>No data available</div>;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart 
        data={data} 
        layout={layout}
        margin={layout === 'vertical' ? { left: 20, right: 30 } : { left: -20, right: 0 }}
        barSize={layout === 'vertical' ? 12 : 32}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={layout === 'horizontal'} vertical={layout === 'vertical'} stroke="rgba(15,23,42,0.04)" />
        
        {layout === 'horizontal' ? (
          <>
            <XAxis dataKey={xKey} axisLine={false} tickLine={false} tick={{ fill: 'rgba(17, 24, 39, 0.4)', fontSize: 10, fontWeight: 600 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'rgba(17, 24, 39, 0.4)', fontSize: 10, fontWeight: 600 }} tickFormatter={(val) => val >= 1000 ? `${val/1000}k` : val} />
          </>
        ) : (
          <>
            <XAxis type="number" hide />
            <YAxis dataKey={xKey} type="category" axisLine={false} tickLine={false} width={80} tick={{ fill: 'rgba(17, 24, 39, 0.6)', fontSize: 11, fontWeight: 500 }} />
          </>
        )}

        <Tooltip 
          content={<GlassTooltip />} 
          cursor={{ fill: 'rgba(109,91,255, 0.04)' }} 
          trigger="hover"
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
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
};

// --- 3. Donut Chart ---

interface DonutChartProps extends BaseChartProps {
  data: any[];
  onSliceClick?: (data: any) => void;
}

export const DonutChart: React.FC<DonutChartProps> = ({ data, height = 300, isLoading = false, onSliceClick }) => {
  const total = useMemo(() => data?.reduce((sum, item) => sum + item.value, 0) || 0, [data]);

  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) return <div className="flex items-center justify-center text-gray-400 text-sm" style={{ height }}>No data available</div>;

  return (
    <div className="relative flex items-center justify-center" style={{ height }}>
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
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color || CHART_COLORS[index % CHART_COLORS.length]} className="hover:opacity-80 transition-opacity" />
            ))}
          </Pie>
          <Tooltip 
            content={<GlassTooltip />} 
            trigger="hover"
            animationDuration={150}
            wrapperStyle={{ outline: 'none', zIndex: 1000 }}
          />
          <Legend verticalAlign="bottom" iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
        </PieChart>
      </ResponsiveContainer>
      {/* Center Text */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 -mt-4 text-center pointer-events-none">
        <span className="block text-2xl font-bold text-text-primary">{total >= 1000 ? `${(total/1000).toFixed(1)}k` : total}</span>
        <span className="text-[10px] text-text-tertiary font-semibold uppercase tracking-widest">Total</span>
      </div>
    </div>
  );
};

// --- 4. Skill Radar Chart ---

interface SkillRadarChartProps extends BaseChartProps {
  data: RadarMetric[];
}

export const SkillRadarChart: React.FC<SkillRadarChartProps> = ({ data, height = 300, isLoading = false }) => {
  
  if (isLoading) return <ChartSkeleton height={height} />;
  if (!data || data.length === 0) return <div className="flex items-center justify-center text-gray-400 text-sm" style={{ height }}>No data available</div>;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
        <PolarGrid stroke="rgba(15,23,42,0.06)" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(17, 24, 39, 0.5)', fontSize: 10, fontWeight: 600 }} />
        <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
        
        <Radar
          name="Agent"
          dataKey="A"
          stroke={CHART_COLORS[0]}
          strokeWidth={2}
          fill={CHART_COLORS[0]}
          fillOpacity={0.3}
        />
        <Radar
          name="Team Avg"
          dataKey="B"
          stroke={CHART_COLORS[4]}
          strokeWidth={2}
          fill={CHART_COLORS[4]}
          fillOpacity={0.1}
        />
        <Tooltip 
          content={<GlassTooltip />} 
          trigger="hover"
          animationDuration={150}
          wrapperStyle={{ outline: 'none', zIndex: 1000 }}
        />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
      </RadarChart>
    </ResponsiveContainer>
  );
};

// --- 5. Density Heatmap (Optimized) ---

interface DensityHeatmapProps extends BaseChartProps {
  data: HeatmapPoint[];
  xAxisLabels: string[];
  yAxisLabels: string[];
}

export const DensityHeatmap: React.FC<DensityHeatmapProps> = ({ 
  data, xAxisLabels, yAxisLabels, isLoading = false 
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

  const getValue = (x: string, y: string) => dataMap.get(`${x}-${y}`) || 0;

  // 3. Dynamic Coloring: Assigns color based on percentage of max value (Quintiles)
  const getColor = (value: number) => {
    if (value === 0) return 'bg-gray-50';
    const percentage = value / maxValue;
    
    if (percentage < 0.2) return 'bg-primary/5';
    if (percentage < 0.4) return 'bg-primary/20';
    if (percentage < 0.6) return 'bg-primary/40';
    if (percentage < 0.8) return 'bg-primary/60';
    return 'bg-primary';
  };

  if (isLoading) return <ChartSkeleton height={300} />;

  return (
    <div className="overflow-x-auto w-full">
      <div className="min-w-[500px] flex flex-col">
        {/* X-Axis Labels */}
        <div className="flex mb-2 ml-12">
          {xAxisLabels.map(day => (
            <div key={day} className="flex-1 text-center text-[10px] font-semibold text-text-tertiary uppercase">
              {day}
            </div>
          ))}
        </div>

        {/* Grid */}
        <div className="flex flex-col gap-1" role="grid" aria-label="Activity Heatmap">
          {yAxisLabels.map(hour => (
            <div key={hour} className="flex items-center gap-1" role="row">
              {/* Y-Axis Label */}
              <div className="w-12 text-[10px] font-medium text-text-tertiary text-right pr-3">
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
                    tabIndex={0} // Make keyboard accessible
                    className={`flex-1 h-8 rounded-md transition-all hover:scale-105 hover:shadow-md relative group cursor-default outline-none focus:ring-2 focus:ring-primary/50 ${getColor(val)}`}
                  >
                    {/* Custom Tooltip for Grid Cell */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-[10px] rounded pointer-events-none whitespace-nowrap z-20 shadow-lg">
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
      <div className="flex items-center justify-end gap-2 mt-4 text-[10px] text-text-tertiary">
        <span>Low</span>
        <div className="flex gap-1" aria-hidden="true">
           <div className="w-3 h-3 rounded bg-gray-50 border border-gray-100"></div>
           <div className="w-3 h-3 rounded bg-primary/20"></div>
           <div className="w-3 h-3 rounded bg-primary/60"></div>
           <div className="w-3 h-3 rounded bg-primary"></div>
        </div>
        <span>High</span>
      </div>
    </div>
  );
};