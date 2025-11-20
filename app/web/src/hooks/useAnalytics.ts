import { useQuery } from '@tanstack/react-query';
import analyticsAPI from '@/services/api';
import type { FilterParams } from '@/shared/types';

const isDev = import.meta.env.DEV;

/**
 * Log query errors in development mode
 */
function logQueryError(queryName: string, error: unknown) {
  if (isDev) {
    console.error(`[useAnalytics] Error in ${queryName}:`, error);
    if (error instanceof Error) {
      console.error(`[useAnalytics] Error details:`, {
        message: error.message,
        stack: error.stack,
      });
    }
  }
}

/**
 * Hook for fetching revenue trends by period type
 */
export function useRevenueTrendsQuery(
  periodType: 'monthly' | 'quarterly' | 'yearly',
  filters?: FilterParams
) {
  return useQuery({
    queryKey: ['analytics', 'revenue', periodType, filters],
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getRevenueTrends(periodType, filters);
        if (isDev) {
          console.log(`[useAnalytics] Revenue trends loaded:`, {
            periodType,
            count: result.data?.length || 0,
          });
        }
        return result;
      } catch (error) {
        logQueryError('useRevenueTrendsQuery', error);
        throw error;
      }
    },
  });
}

/**
 * Hook for fetching monthly metrics summary
 */
export function useMonthlyMetricsQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'metrics', filters],
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getMonthlyMetrics(filters);
        if (isDev) {
          console.log(`[useAnalytics] Monthly metrics loaded:`, {
            count: result.data?.length || 0,
          });
        }
        return result;
      } catch (error) {
        logQueryError('useMonthlyMetricsQuery', error);
        throw error;
      }
    },
  });
}

/**
 * Hook for fetching activity heatmap data
 */
export function useHeatmapQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'heatmap', filters],
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getHeatmap(filters);
        if (isDev) {
          console.log(`[useAnalytics] Heatmap data loaded:`, {
            count: result.data?.length || 0,
          });
        }
        return result;
      } catch (error) {
        logQueryError('useHeatmapQuery', error);
        throw error;
      }
    },
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
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getSalesPersonPerformance(filters);
        if (isDev) {
          console.log(`[useAnalytics] Sales person performance loaded:`, {
            count: result.data?.length || 0,
            sample: result.data?.[0],
          });
        }
        return result;
      } catch (error) {
        logQueryError('useSalesPersonPerformanceQuery', error);
        throw error;
      }
    },
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

/**
 * Hook for fetching customer demographics
 */
export function useCustomerDemographicsQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'customer-demographics', filters],
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getCustomerDemographics(filters);
        if (isDev) {
          console.log(`[useAnalytics] Customer demographics loaded:`, {
            count: result.data?.length || 0,
          });
        }
        return result;
      } catch (error) {
        logQueryError('useCustomerDemographicsQuery', error);
        throw error;
      }
    },
  });
}

/**
 * Hook for fetching customer segments
 */
export function useCustomerSegmentsQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'customer-segments', filters],
    queryFn: () => analyticsAPI.getCustomerSegments(filters),
  });
}

/**
 * Hook for fetching job status distribution
 */
export function useJobStatusDistributionQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'job-status-distribution', filters],
    queryFn: () => analyticsAPI.getJobStatusDistribution(filters),
  });
}

/**
 * Hook for fetching job trends
 */
export function useJobTrendsQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'job-trends', filters],
    queryFn: () => analyticsAPI.getJobTrends(filters),
  });
}

/**
 * Hook for fetching lead sources
 */
export function useLeadSourcesQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'lead-sources', filters],
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getLeadSources(filters);
        if (isDev) {
          console.log(`[useAnalytics] Lead sources loaded:`, {
            count: result.data?.length || 0,
            sample: result.data?.[0],
            fields: result.data?.[0] ? Object.keys(result.data[0]) : [],
          });
        }
        return result;
      } catch (error) {
        logQueryError('useLeadSourcesQuery', error);
        throw error;
      }
    },
  });
}

/**
 * Hook for fetching operational efficiency
 */
export function useOperationalEfficiencyQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'operational-efficiency', filters],
    queryFn: () => analyticsAPI.getOperationalEfficiency(filters),
  });
}

/**
 * Hook for fetching forecast data
 */
export function useForecastQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'forecast', filters],
    queryFn: () => analyticsAPI.getForecast(filters),
  });
}

/**
 * Hook for fetching profitability analysis
 */
export function useProfitabilityQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'profitability', filters],
    queryFn: () => analyticsAPI.getProfitability(filters),
  });
}

/**
 * Hook for fetching geographic coverage
 */
export function useGeographicCoverageQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'geographic-coverage', filters],
    queryFn: () => analyticsAPI.getGeographicCoverage(filters),
  });
}

/**
 * Hook for fetching customer behavior
 */
export function useCustomerBehaviorQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'customer-behavior', filters],
    queryFn: () => analyticsAPI.getCustomerBehavior(filters),
  });
}

/**
 * Hook for fetching benchmarks
 */
export function useBenchmarksQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'benchmarks', filters],
    queryFn: () => analyticsAPI.getBenchmarks(filters),
  });
}

/**
 * Hook for fetching lead conversion funnel
 */
export function useLeadConversionQuery(filters?: FilterParams) {
  return useQuery({
    queryKey: ['analytics', 'lead-conversion', filters],
    queryFn: async () => {
      try {
        const result = await analyticsAPI.getLeadConversion(filters);
        if (isDev) {
          console.log(`[useAnalytics] Lead conversion loaded:`, {
            count: result.data?.length || 0,
          });
        }
        return result;
      } catch (error) {
        logQueryError('useLeadConversionQuery', error);
        throw error;
      }
    },
  });
}

