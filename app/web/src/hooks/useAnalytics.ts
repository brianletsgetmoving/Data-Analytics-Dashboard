import { useQuery } from '@tanstack/react-query';
import analyticsAPI from '@/services/api';
import type { FilterParams } from '@/shared/types';

/**
 * Hook for fetching revenue trends by period type
 */
export function useRevenueTrendsQuery(periodType: 'monthly' | 'quarterly' | 'yearly') {
  return useQuery({
    queryKey: ['analytics', 'revenue', periodType],
    queryFn: () => analyticsAPI.getRevenueTrends(periodType),
  });
}

/**
 * Hook for fetching monthly metrics summary
 */
export function useMonthlyMetricsQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'metrics', filters],
    queryFn: () => analyticsAPI.getMonthlyMetrics(filters),
  });
}

/**
 * Hook for fetching activity heatmap data
 */
export function useHeatmapQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'heatmap', filters],
    queryFn: () => analyticsAPI.getHeatmap(filters),
  });
}

/**
 * Hook for fetching radar chart data
 */
export function useRadarChartQuery(
  dimension: 'customer' | 'salesperson' | 'branch',
  filters?: FilterParams
) {
  return useQuery({
    queryKey: ['analytics', 'radar', dimension, filters],
    queryFn: () => analyticsAPI.getRadar(dimension, filters),
  });
}

/**
 * Hook for fetching sales person performance
 */
export function useSalesPersonPerformanceQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'salesperson-performance', filters],
    queryFn: () => analyticsAPI.getSalesPersonPerformance(filters),
  });
}

/**
 * Hook for fetching branch performance
 */
export function useBranchPerformanceQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'branch-performance', filters],
    queryFn: () => analyticsAPI.getBranchPerformance(filters),
  });
}

