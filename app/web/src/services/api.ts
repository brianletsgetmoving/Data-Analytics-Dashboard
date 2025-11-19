import type {
  AnalyticsResponse,
  RevenueMetrics,
  MonthlyMetrics,
  ActivityHeatmap,
  SalesRadar,
  SalesPersonPerformance,
  BranchPerformance,
  FilterParams,
} from '@/shared/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.error || `API Error: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

export const analyticsAPI = {
  /**
   * Get revenue trends by period type
   */
  async getRevenueTrends(
    periodType: 'monthly' | 'quarterly' | 'yearly'
  ): Promise<AnalyticsResponse<RevenueMetrics[]>> {
    return fetchApi<AnalyticsResponse<RevenueMetrics[]>>(
      `/api/v1/analytics/revenue?periodType=${periodType}`
    );
  },

  /**
   * Get monthly metrics summary
   */
  async getMonthlyMetrics(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<MonthlyMetrics[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('dateFrom', filters.date_from);
    if (filters?.date_to) params.append('dateTo', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<MonthlyMetrics[]>>(
      `/api/v1/analytics/metrics${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get activity heatmap data
   */
  async getHeatmap(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<ActivityHeatmap[]>> {
    const params = new URLSearchParams();
    if (filters?.branch_id) params.append('branchId', filters.branch_id);
    if (filters?.date_from) params.append('dateFrom', filters.date_from);
    if (filters?.date_to) params.append('dateTo', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<ActivityHeatmap[]>>(
      `/api/v1/analytics/heatmap${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get radar chart data
   */
  async getRadar(
    dimension: 'customer' | 'salesperson' | 'branch',
    filters?: FilterParams
  ): Promise<AnalyticsResponse<SalesRadar[]>> {
    const params = new URLSearchParams();
    params.append('dimension', dimension);
    if (filters?.date_from) params.append('dateFrom', filters.date_from);
    if (filters?.date_to) params.append('dateTo', filters.date_to);
    
    return fetchApi<AnalyticsResponse<SalesRadar[]>>(
      `/api/v1/analytics/radar?${params.toString()}`
    );
  },

  /**
   * Get sales person performance
   */
  async getSalesPersonPerformance(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<SalesPersonPerformance[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('dateFrom', filters.date_from);
    if (filters?.date_to) params.append('dateTo', filters.date_to);
    if (filters?.sales_person_id) params.append('salesPersonId', filters.sales_person_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<SalesPersonPerformance[]>>(
      `/api/v1/analytics/salesperson-performance${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get branch performance
   */
  async getBranchPerformance(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<BranchPerformance[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('dateFrom', filters.date_from);
    if (filters?.date_to) params.append('dateTo', filters.date_to);
    if (filters?.branch_id) params.append('branchId', filters.branch_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<BranchPerformance[]>>(
      `/api/v1/analytics/branch-performance${queryString ? `?${queryString}` : ''}`
    );
  },
};

export { ApiError };
export default analyticsAPI;

