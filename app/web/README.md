# Analytics Web Frontend

React + Vite frontend application for the Data Analytics Dashboard.

## Technology Stack

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety
- **TanStack Query** - Server state management
- **Recharts** - Data visualization
- **Tailwind CSS** - Utility-first CSS
- **Neo-morphic Design System** - Custom design system with soft gradients and glass effects

## Project Structure

```
app/web/
├── src/
│   ├── components/
│   │   ├── dashboard/      # Dashboard components
│   │   ├── layout/        # Layout components (Header, Layout)
│   │   └── ui/            # Reusable UI components (SkeletonLoader)
│   ├── hooks/             # Custom React hooks (useAnalytics)
│   ├── pages/             # Page components (Dashboard)
│   ├── services/          # API client (api.ts)
│   └── styles/            # CSS files (neomorphic.css, index.css)
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file:
   ```bash
   VITE_API_URL=http://localhost:3001
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Features

### Overview Dashboard
- Revenue trends chart (monthly/quarterly/yearly)
- KPI cards (Total Jobs, Total Revenue, Booking Rate, Avg Job Value)
- Period selector with Neo-morphic styling

### Activity Heatmap
- Branch-month activity matrix
- Color-coded revenue visualization
- Scrollable table layout

### Performance Radar
- Multi-dimensional performance comparison
- Supports customer, salesperson, and branch dimensions
- Interactive dimension selector

## Design System

The application uses a custom Neo-morphic design system with:
- Soft gradients and shadows
- Glass morphism effects
- Consistent spacing and typography
- Responsive design (mobile-first)

See `src/styles/neomorphic.css` for design system classes.

## Type Safety

All types are imported from `shared/types.ts` to ensure consistency between frontend and backend:
- `RevenueMetrics`
- `MonthlyMetrics`
- `ActivityHeatmap`
- `SalesRadar`
- `SalesPersonPerformance`
- `BranchPerformance`
- `FilterParams`
- `AnalyticsResponse<T>`

## API Integration

The API client (`src/services/api.ts`) provides type-safe methods for all analytics endpoints:
- `getRevenueTrends(periodType)`
- `getMonthlyMetrics(filters?)`
- `getHeatmap(filters?)`
- `getRadar(dimension, filters?)`
- `getSalesPersonPerformance(filters?)`
- `getBranchPerformance(filters?)`

All methods return `AnalyticsResponse<T>` wrapped data.

## Development

- **Linting**: `npm run lint`
- **Build**: `npm run build`
- **Preview**: `npm run preview`

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:3001`)

