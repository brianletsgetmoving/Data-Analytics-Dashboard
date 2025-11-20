# Analytics Dashboard - Frontend

A comprehensive analytics dashboard built with React, TypeScript, and Tailwind CSS, integrated with the Data Analytics V5 backend API.

## Features

### 11 Analytics Views
- **Overview**: High-level KPIs, revenue trends, top performers, lead sources, activity heatmap
- **Revenue**: Revenue performance, trends by period, branch revenue breakdown
- **Customers**: Customer demographics, segmentation, geographic distribution
- **Jobs**: Job volume trends, status distribution, recent jobs
- **Sales Performance**: Sales leaderboard, team skill gap analysis, performance metrics
- **Leads**: Lead conversion funnel, lead sources, conversion metrics
- **Operational**: Operational efficiency, resource utilization, scheduling metrics
- **Geographic**: Geographic coverage, top origin cities, route analysis
- **Profitability**: Profitability trends, margins, ROI analysis
- **Forecasting**: Revenue and job volume forecasts
- **Benchmarking**: Performance vs industry benchmarks

### Key Components

#### Navigation
- **Sidebar**: Collapsible sidebar with 11 views organized by category
- **Breadcrumbs**: Navigation breadcrumbs for drill-down views
- **View Switcher**: Quick view navigation with search
- **Mobile Menu**: Full-screen mobile navigation menu
- **Keyboard Shortcuts**: Ctrl+1-5 for quick navigation

#### Data Visualization
- **GradientAreaChart**: Area charts with gradient fills and LTTB downsampling
- **MetricBarChart**: Horizontal/vertical bar charts
- **DonutChart**: Donut charts with center totals
- **SkillRadarChart**: Radar charts for multi-dimensional comparisons
- **DensityHeatmap**: Activity heatmaps for time-based patterns

#### Filtering & Search
- **DateRangeFilter**: Preset and custom date range selection
- **AdvancedFilterPanel**: Comprehensive filter panel with all filter options
- **Global Filter Store**: Zustand store for managing filter state across views

#### Tables
- **DataTable**: Sortable, searchable, paginated data tables with CSV export

#### UI Components
- **KPICard**: Reusable KPI display with trends and badges
- **ErrorBoundary**: Error boundaries for graceful error handling
- **EmptyState**: Empty state components for no data scenarios
- **SkeletonLoader**: Loading skeleton components

### Technical Stack

- **React 19**: Latest React with hooks
- **TypeScript**: Full type safety
- **Tailwind CSS 4**: Utility-first styling with custom design tokens
- **React Router**: Client-side routing
- **TanStack Query**: Data fetching and caching
- **Zustand**: Lightweight state management
- **Recharts**: Chart library
- **Lucide React**: Icon library
- **Vitest**: Testing framework

### Project Structure

```
app/web/src/
├── components/
│   ├── charts/          # Chart components
│   ├── filters/         # Filter components
│   ├── layout/          # Layout components (Sidebar, Header, Layout)
│   ├── navigation/     # Navigation components (Breadcrumbs, ViewSwitcher)
│   ├── responsive/      # Mobile/responsive components
│   ├── tables/          # Table components
│   ├── ui/              # Reusable UI components
│   └── accessibility/   # Accessibility components
├── context/             # React contexts (ThemeContext)
├── hooks/               # Custom React hooks
├── pages/               # Page components (11 views)
├── services/            # API service layer
├── store/               # Zustand stores
├── utils/               # Utility functions
└── __tests__/           # Test files
```

### Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run tests with UI
npm run test:ui
```

### Environment Variables

Create a `.env` file in `app/web/`:

```env
VITE_API_URL=http://localhost:3001
```

### API Integration

The frontend integrates with the backend API at `/api/v1/analytics/`:

- `/revenue` - Revenue trends
- `/metrics` - Monthly metrics
- `/heatmap` - Activity heatmap
- `/radar` - Performance radar
- `/salesperson-performance` - Sales person metrics
- `/branch-performance` - Branch metrics
- `/customer-demographics` - Customer geography
- `/customer-segments` - Customer segmentation
- `/job-status-distribution` - Job status breakdown
- `/job-trends` - Job volume trends
- `/lead-sources` - Lead source performance
- `/lead-conversion` - Lead conversion funnel
- `/operational-efficiency` - Operational metrics
- `/forecast` - Forecasting data
- `/profitability` - Profitability analysis
- `/geographic-coverage` - Geographic data
- `/customer-behavior` - Customer behavior analysis
- `/benchmarks` - Benchmarking data

### Features

#### Dark Mode
Full dark mode support with system preference detection and manual toggle.

#### Responsive Design
- Mobile-first design
- Tablet optimization
- Desktop layouts
- Touch-friendly interactions

#### Performance
- LTTB downsampling for large datasets
- React Query caching
- Memoized components
- Code splitting

#### Accessibility
- Keyboard navigation
- Screen reader support
- ARIA labels
- Skip links
- Focus management

### Development

The app uses:
- **Vite** for fast development and building
- **TypeScript** for type safety
- **ESLint** for code quality
- **Vitest** for testing

### Testing

Tests are located in `src/__tests__/`:
- Component tests
- Hook tests
- Utility function tests

Run tests with:
```bash
npm test
```

### Building

```bash
npm run build
```

Outputs to `dist/` directory.
