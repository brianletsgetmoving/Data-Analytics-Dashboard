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

  /**
   * Get detailed error information for debugging
   */
  getDetails(): Record<string, unknown> {
    return {
      message: this.message,
      status: this.status,
      response: this.response,
      stack: this.stack,
    };
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  const isDev = import.meta.env.DEV;
  
  if (isDev) {
    console.log(`[API] Fetching: ${url}`, options);
  }
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new ApiError(
      errorData.error || `API Error: ${response.statusText}`,
      response.status,
      errorData
    );
    
    if (isDev) {
      console.error(`[API] Error ${response.status} on ${url}:`, errorData);
    }
    
    throw error;
  }

  const data = await response.json();
  
  if (isDev) {
    console.log(`[API] Response from ${url}:`, {
      status: response.status,
      dataCount: Array.isArray(data.data) ? data.data.length : 'N/A',
      dataKeys: Array.isArray(data.data) && data.data.length > 0 
        ? Object.keys(data.data[0] || {})
        : 'No data',
      metadata: data.metadata,
      error: data.error,
    });
    
    // Log first item structure if array
    if (Array.isArray(data.data) && data.data.length > 0) {
      console.log(`[API] First item structure:`, data.data[0]);
    }
  }

  return data;
}

export const analyticsAPI = {
  /**
   * Get revenue trends by period type
   */
  async getRevenueTrends(
    periodType: 'monthly' | 'quarterly' | 'yearly',
    filters?: FilterParams
  ): Promise<AnalyticsResponse<RevenueMetrics[]>> {
    const params = new URLSearchParams();
    params.append('period_type', periodType);
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    return fetchApi<AnalyticsResponse<RevenueMetrics[]>>(
      `/api/v1/analytics/revenue?${params.toString()}`
    );
  },

  /**
   * Get monthly metrics summary
   */
  async getMonthlyMetrics(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<MonthlyMetrics[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    if (filters?.branch_name) params.append('branch_name', filters.branch_name);
    if (filters?.sales_person_id) params.append('sales_person_id', filters.sales_person_id);
    if (filters?.sales_person_name) params.append('sales_person_name', filters.sales_person_name);
    
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
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    if (filters?.branch_name) params.append('branch_name', filters.branch_name);
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
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
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
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
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.sales_person_id) params.append('sales_person_id', filters.sales_person_id);
    if (filters?.sales_person_name) params.append('sales_person_name', filters.sales_person_name);
    
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
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    if (filters?.branch_name) params.append('branch_name', filters.branch_name);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<BranchPerformance[]>>(
      `/api/v1/analytics/branch-performance${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get customer demographics
   */
  async getCustomerDemographics(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/customer-demographics${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get customer segments
   */
  async getCustomerSegments(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/customer-segments${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get job status distribution
   */
  async getJobStatusDistribution(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.opportunity_status) params.append('opportunity_status', filters.opportunity_status);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/job-status-distribution${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get job trends
   */
  async getJobTrends(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/job-trends${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get lead sources
   */
  async getLeadSources(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.lead_source_id) params.append('lead_source_id', filters.lead_source_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/lead-sources${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get operational efficiency metrics
   */
  async getOperationalEfficiency(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/operational-efficiency${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get forecast data
   */
  async getForecast(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/forecast${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get profitability analysis
   */
  async getProfitability(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/profitability${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get geographic coverage
   */
  async getGeographicCoverage(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/geographic-coverage${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get customer behavior analysis
   */
  async getCustomerBehavior(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.customer_id) params.append('customer_id', filters.customer_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/customer-behavior${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get benchmarks
   */
  async getBenchmarks(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/benchmarks${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get lead conversion funnel
   */
  async getLeadConversion(
    filters?: FilterParams
  ): Promise<AnalyticsResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.lead_source_id) params.append('lead_source_id', filters.lead_source_id);
    
    const queryString = params.toString();
    return fetchApi<AnalyticsResponse<any[]>>(
      `/api/v1/analytics/lead-conversion${queryString ? `?${queryString}` : ''}`
    );
  },
};

export { ApiError };
export default analyticsAPI;

