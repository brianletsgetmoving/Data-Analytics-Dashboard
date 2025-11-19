import OverviewDashboard from '@/components/dashboard/OverviewDashboard';
import ActivityHeatmap from '@/components/dashboard/ActivityHeatmap';
import PerformanceRadar from '@/components/dashboard/PerformanceRadar';
import SalesPersonPerformanceTable from '@/components/dashboard/SalesPersonPerformanceTable';
import BranchPerformanceTable from '@/components/dashboard/BranchPerformanceTable';

function Dashboard() {
  return (
    <div className="space-y-6">
      <OverviewDashboard />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityHeatmap />
        <PerformanceRadar />
      </div>
      <div className="grid grid-cols-1 gap-6">
        <SalesPersonPerformanceTable />
        <BranchPerformanceTable />
      </div>
    </div>
  );
}

export default Dashboard;

