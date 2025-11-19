/**
 * FilterBuilder utility for safe SQL parameter injection
 * 
 * Prevents SQL injection by using parameterized queries.
 * Builds WHERE clause conditions from FilterParams interface.
 */

import { FilterParams } from '@shared/types';

export class FilterBuilder {
  private conditions: string[] = [];
  private parameters: unknown[] = [];
  private paramIndex = 1;

  /**
   * Add date range filter
   */
  addDateRange(dateFrom?: string, dateTo?: string): this {
    if (dateFrom) {
      this.conditions.push(`j.job_date >= $${this.paramIndex}`);
      this.parameters.push(dateFrom);
      this.paramIndex++;
    }
    if (dateTo) {
      this.conditions.push(`j.job_date <= $${this.paramIndex}`);
      this.parameters.push(dateTo);
      this.paramIndex++;
    }
    return this;
  }

  /**
   * Add branch filter
   */
  addBranchFilter(branchId?: string, branchName?: string): this {
    if (branchId) {
      this.conditions.push(`j.branch_id = $${this.paramIndex}`);
      this.parameters.push(branchId);
      this.paramIndex++;
    } else if (branchName) {
      this.conditions.push(`b.name = $${this.paramIndex}`);
      this.parameters.push(branchName);
      this.paramIndex++;
    }
    return this;
  }

  /**
   * Add sales person filter
   */
  addSalesPersonFilter(salesPersonId?: string, salesPersonName?: string): this {
    if (salesPersonId) {
      this.conditions.push(`j.sales_person_id = $${this.paramIndex}`);
      this.parameters.push(salesPersonId);
      this.paramIndex++;
    } else if (salesPersonName) {
      this.conditions.push(`sp.name = $${this.paramIndex}`);
      this.parameters.push(salesPersonName);
      this.paramIndex++;
    }
    return this;
  }

  /**
   * Add customer filter
   */
  addCustomerFilter(customerId?: string): this {
    if (customerId) {
      this.conditions.push(`j.customer_id = $${this.paramIndex}`);
      this.parameters.push(customerId);
      this.paramIndex++;
    }
    return this;
  }

  /**
   * Add opportunity status filter
   */
  addOpportunityStatusFilter(status?: FilterParams['opportunity_status']): this {
    if (status) {
      this.conditions.push(`j.opportunity_status = $${this.paramIndex}`);
      this.parameters.push(status);
      this.paramIndex++;
    }
    return this;
  }

  /**
   * Add lead source filter
   */
  addLeadSourceFilter(leadSourceId?: string): this {
    if (leadSourceId) {
      this.conditions.push(`ls.lead_source_id = $${this.paramIndex}`);
      this.parameters.push(leadSourceId);
      this.paramIndex++;
    }
    return this;
  }

  /**
   * Build WHERE clause from all conditions
   */
  buildWhereClause(): { clause: string; parameters: unknown[] } {
    if (this.conditions.length === 0) {
      return { clause: '', parameters: [] };
    }
    return {
      clause: `AND ${this.conditions.join(' AND ')}`,
      parameters: this.parameters,
    };
  }

  /**
   * Build WHERE clause from FilterParams
   */
  static buildFromParams(params: FilterParams): { clause: string; parameters: unknown[] } {
    const builder = new FilterBuilder();
    builder
      .addDateRange(params.date_from, params.date_to)
      .addBranchFilter(params.branch_id, params.branch_name)
      .addSalesPersonFilter(params.sales_person_id, params.sales_person_name)
      .addCustomerFilter(params.customer_id)
      .addOpportunityStatusFilter(params.opportunity_status)
      .addLeadSourceFilter(params.lead_source_id);
    return builder.buildWhereClause();
  }

  /**
   * Reset builder state
   */
  reset(): this {
    this.conditions = [];
    this.parameters = [];
    this.paramIndex = 1;
    return this;
  }
}

