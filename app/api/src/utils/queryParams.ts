/**
 * Query Parameter Normalization Utility
 * 
 * Maps camelCase query parameters from frontend to snake_case format
 * expected by backend FilterParams interface.
 */

/**
 * Normalize query parameters from camelCase to snake_case
 * 
 * Maps frontend query params to backend FilterParams format:
 * - dateFrom → date_from
 * - dateTo → date_to
 * - branchId → branch_id
 * - branchName → branch_name
 * - salesPersonId → sales_person_id
 * - salesPersonName → sales_person_name
 * - customerId → customer_id
 * - opportunityStatus → opportunity_status
 * - leadSourceId → lead_source_id
 * - periodType → period_type
 */
export function normalizeQueryParams(query: Record<string, unknown>): Record<string, unknown> {
  const normalized: Record<string, unknown> = {};

  // Map camelCase to snake_case
  const paramMap: Record<string, string> = {
    dateFrom: 'date_from',
    dateTo: 'date_to',
    branchId: 'branch_id',
    branchName: 'branch_name',
    salesPersonId: 'sales_person_id',
    salesPersonName: 'sales_person_name',
    customerId: 'customer_id',
    opportunityStatus: 'opportunity_status',
    leadSourceId: 'lead_source_id',
    periodType: 'period_type',
  };

  for (const [key, value] of Object.entries(query)) {
    // If key exists in map, use mapped name; otherwise keep original
    const normalizedKey = paramMap[key] || key;
    normalized[normalizedKey] = value;
  }

  return normalized;
}

