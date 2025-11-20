import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import Layout from './components/layout/Layout';
import Overview from './pages/Overview';
import Revenue from './pages/Revenue';
import Customers from './pages/Customers';
import Jobs from './pages/Jobs';
import SalesPerformance from './pages/SalesPerformance';
import Leads from './pages/Leads';
import Operational from './pages/Operational';
import Geographic from './pages/Geographic';
import Profitability from './pages/Profitability';
import Forecasting from './pages/Forecasting';
import Benchmarking from './pages/Benchmarking';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/revenue" element={<Revenue />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/sales-performance" element={<SalesPerformance />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/operational" element={<Operational />} />
            <Route path="/geographic" element={<Geographic />} />
            <Route path="/profitability" element={<Profitability />} />
            <Route path="/forecasting" element={<Forecasting />} />
            <Route path="/benchmarking" element={<Benchmarking />} />
          </Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

export default App;

