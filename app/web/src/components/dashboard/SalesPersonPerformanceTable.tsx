import { useSalesPersonPerformanceQuery } from '@/hooks/useAnalytics';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import type { SalesPersonPerformance } from '@/shared/types';

function SalesPersonPerformanceTable() {
  const { data, isLoading, error } = useSalesPersonPerformanceQuery();

  const formatCurrency = (value: number | null): string => {
    if (value === null) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (error) {
    return (
      <div className="neo-card">
        <p className="text-red-500">Error loading sales person performance data</p>
      </div>
    );
  }

  const performanceData = data?.data || [];

  return (
    <div className="neo-card">
      <h2 className="text-xl font-bold neo-text-primary mb-4">Sales Person Performance</h2>
      
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <SkeletonLoader key={i} height={60} variant="card" />
          ))}
        </div>
      ) : performanceData.length === 0 ? (
        <p className="neo-text-muted text-center py-8">No performance data available</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left p-3 text-sm font-semibold neo-text-secondary">Sales Person</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Total Jobs</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Total Revenue</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Avg Job Value</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Booked Revenue</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Closed Revenue</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Booked Jobs</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Closed Jobs</th>
                <th className="text-right p-3 text-sm font-semibold neo-text-secondary">Customers</th>
              </tr>
            </thead>
            <tbody>
              {performanceData.map((person: SalesPersonPerformance, index: number) => (
                <tr
                  key={index}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="p-3 text-sm font-medium neo-text-primary">
                    {person.sales_person_name || 'Unknown'}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {person.total_jobs.toLocaleString()}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-primary font-semibold">
                    {formatCurrency(person.total_revenue)}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {formatCurrency(person.avg_job_value)}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {formatCurrency(person.booked_revenue)}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {formatCurrency(person.closed_revenue)}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {person.booked_jobs.toLocaleString()}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {person.closed_jobs.toLocaleString()}
                  </td>
                  <td className="p-3 text-sm text-right neo-text-secondary">
                    {person.unique_customers.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default SalesPersonPerformanceTable;

