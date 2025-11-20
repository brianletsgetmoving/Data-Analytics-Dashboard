import { describe, it, expect } from 'vitest';
import {
  transformRevenueMetricsToChartData,
  calculateKPIsFromMetrics,
  formatPeriod,
} from '@/utils/dataTransform';
import { RevenueMetrics, MonthlyMetrics } from '@/shared/types';

describe('dataTransform utilities', () => {
  describe('transformRevenueMetricsToChartData', () => {
    it('transforms revenue metrics to chart format', () => {
      const metrics: RevenueMetrics[] = [
        {
          period_type: 'monthly',
          period: '2024-01-01',
          job_count: 10,
          revenue: 1000,
          booked_revenue: 800,
          closed_revenue: 600,
          previous_period_revenue: 900,
          period_over_period_change_percent: 11.1,
        },
      ];

      const result = transformRevenueMetricsToChartData(metrics);
      expect(result).toHaveLength(1);
      expect(result[0].revenue).toBe(1000);
      expect(result[0].previousRevenue).toBe(900);
    });
  });

  describe('calculateKPIsFromMetrics', () => {
    it('calculates KPIs from monthly metrics', () => {
      const metrics: MonthlyMetrics[] = [
        {
          month: '2024-01-01',
          year: 2024,
          month_number: 1,
          total_jobs: 100,
          quoted_jobs: 80,
          booked_jobs: 60,
          closed_jobs: 50,
          lost_jobs: 20,
          cancelled_jobs: 0,
          total_revenue: 100000,
          avg_job_value: 2000,
          unique_customers: 50,
          active_branches: 5,
          active_sales_people: 10,
          booking_rate_percent: 75,
        },
      ];

      const kpis = calculateKPIsFromMetrics(metrics);
      expect(kpis).toHaveLength(4);
      expect(kpis[0].label).toBe('Total Revenue');
    });
  });

  describe('formatPeriod', () => {
    it('formats monthly periods', () => {
      const date = new Date('2024-01-15');
      const result = formatPeriod(date, 'monthly');
      expect(result).toContain('Jan');
      expect(result).toContain('2024');
    });

    it('formats quarterly periods', () => {
      const date = new Date('2024-02-15');
      const result = formatPeriod(date, 'quarterly');
      expect(result).toContain('Q1');
    });

    it('formats yearly periods', () => {
      const date = new Date('2024-06-15');
      const result = formatPeriod(date, 'yearly');
      expect(result).toBe('2024');
    });
  });
});

