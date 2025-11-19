/**
 * Analytics API Routes
 * 
 * Endpoints for analytics dashboard data:
 * - Revenue trends
 * - Monthly metrics
 * - Activity heatmap
 * - Performance radar
 * - Sales person performance
 * - Branch performance
 */

import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { QueryService } from '../services/QueryService';
import { normalizeQueryParams } from '../utils/queryParams';
import {
  RevenueMetrics,
  MonthlyMetrics,
  ActivityHeatmap,
  SalesRadar,
  SalesPersonPerformance,
  BranchPerformance,
  FilterParams,
  AnalyticsResponse,
} from '@shared/types';

const router = Router();

// Validation schemas
const periodTypeSchema = z.enum(['monthly', 'quarterly', 'yearly']);
const dimensionSchema = z.enum(['customer', 'salesperson', 'branch']);
const dateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);

const filterParamsSchema = z.object({
  date_from: dateSchema.optional(),
  date_to: dateSchema.optional(),
  branch_id: z.string().uuid().optional(),
  branch_name: z.string().optional(),
  sales_person_id: z.string().uuid().optional(),
  sales_person_name: z.string().optional(),
  customer_id: z.string().uuid().optional(),
  opportunity_status: z.enum(['QUOTED', 'BOOKED', 'LOST', 'CANCELLED', 'CLOSED']).optional(),
  lead_source_id: z.string().uuid().optional(),
  period_type: periodTypeSchema.optional(),
});

export function createAnalyticsRouter(queryService: QueryService): Router {
  /**
   * GET /api/v1/analytics/revenue
   * Revenue trends by period (monthly, quarterly, yearly)
   */
  router.get('/revenue', async (req: Request, res: Response<AnalyticsResponse<RevenueMetrics[]>>) => {
    try {
      const normalizedQuery = normalizeQueryParams(req.query);
      const periodType = periodTypeSchema.parse(normalizedQuery.period_type || 'monthly');
      
      const results = await queryService.executeQuery<RevenueMetrics>(
        'revenue_trends.sql'
      );

      // Filter by period_type
      const filtered = results.filter((r) => r.period_type === periodType);

      res.json({
        data: filtered,
        metadata: {
          count: filtered.length,
          filters_applied: { period_type: periodType },
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          data: [] as RevenueMetrics[],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        data: [] as RevenueMetrics[],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  /**
   * GET /api/v1/analytics/metrics
   * Monthly metrics summary
   */
  router.get('/metrics', async (req: Request, res: Response<AnalyticsResponse<MonthlyMetrics[]>>) => {
    try {
      const normalizedQuery = normalizeQueryParams(req.query);
      const filters = filterParamsSchema.parse(normalizedQuery);

      const results = await queryService.executeQuery<MonthlyMetrics>(
        'monthly_metrics_summary.sql',
        filters
      );

      res.json({
        data: results,
        metadata: {
          count: results.length,
          filters_applied: filters,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          data: [] as MonthlyMetrics[],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        data: [] as MonthlyMetrics[],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  /**
   * GET /api/v1/analytics/heatmap
   * Activity heatmap (branch-month matrix)
   */
  router.get('/heatmap', async (req: Request, res: Response<AnalyticsResponse<ActivityHeatmap[]>>) => {
    try {
      const normalizedQuery = normalizeQueryParams(req.query);
      const filters = filterParamsSchema.parse(normalizedQuery);

      const results = await queryService.executeQuery<ActivityHeatmap>(
        'analytics/heatmap_revenue_by_branch_month.sql',
        filters
      );

      res.json({
        data: results,
        metadata: {
          count: results.length,
          filters_applied: filters,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          data: [] as ActivityHeatmap[],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        data: [] as ActivityHeatmap[],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  /**
   * GET /api/v1/analytics/radar
   * Performance radar chart data
   */
  router.get('/radar', async (req: Request, res: Response<AnalyticsResponse<SalesRadar[]>>) => {
    try {
      const normalizedQuery = normalizeQueryParams(req.query);
      const dimension = dimensionSchema.parse(normalizedQuery.dimension || req.query.dimension || 'customer');
      const filters = filterParamsSchema.parse(normalizedQuery);

      let results: SalesRadar[];

      if (dimension === 'customer') {
        results = await queryService.executeQuery<SalesRadar>(
          'analytics/customer_segmentation_radar.sql',
          filters
        );
      } else if (dimension === 'salesperson') {
        // Aggregate sales person data into radar format
        const salesPersonData = await queryService.executeQuery<SalesPersonPerformance>(
          'revenue_by_sales_person.sql',
          filters
        );
        
        // Transform to radar format (simplified - would need actual aggregation logic)
        results = salesPersonData.map((sp) => ({
          subject: sp.sales_person_name || 'Unknown',
          value: sp.total_revenue,
          full_mark: null,
        }));
      } else {
        // Branch dimension
        const branchData = await queryService.executeQuery<BranchPerformance>(
          'revenue_by_branch.sql',
          filters
        );
        
        results = branchData.map((b) => ({
          subject: b.branch_name || 'Unknown',
          value: b.total_revenue,
          full_mark: null,
        }));
      }

      res.json({
        data: results,
        metadata: {
          count: results.length,
          filters_applied: { ...filters, dimension } as FilterParams & { dimension?: string },
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          data: [] as SalesRadar[],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        data: [] as SalesRadar[],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  /**
   * GET /api/v1/analytics/salesperson-performance
   * Sales person performance metrics
   */
  router.get('/salesperson-performance', async (req: Request, res: Response<AnalyticsResponse<SalesPersonPerformance[]>>) => {
    try {
      const normalizedQuery = normalizeQueryParams(req.query);
      const filters = filterParamsSchema.parse(normalizedQuery);

      const results = await queryService.executeQuery<SalesPersonPerformance>(
        'revenue_by_sales_person.sql',
        filters
      );

      res.json({
        data: results,
        metadata: {
          count: results.length,
          filters_applied: filters,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          data: [] as SalesPersonPerformance[],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        data: [] as SalesPersonPerformance[],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  /**
   * GET /api/v1/analytics/branch-performance
   * Branch performance metrics
   */
  router.get('/branch-performance', async (req: Request, res: Response<AnalyticsResponse<BranchPerformance[]>>) => {
    try {
      const normalizedQuery = normalizeQueryParams(req.query);
      const filters = filterParamsSchema.parse(normalizedQuery);

      const results = await queryService.executeQuery<BranchPerformance>(
        'revenue_by_branch.sql',
        filters
      );

      res.json({
        data: results,
        metadata: {
          count: results.length,
          filters_applied: filters,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          data: [] as BranchPerformance[],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        data: [] as BranchPerformance[],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  return router;
}

