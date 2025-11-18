# Data Analytics Platform - Full Stack Implementation

Complete analytics platform with PostgreSQL → FastAPI → Next.js stack, featuring a comprehensive dashboard with mobile-first design, dark mode UI, and interactive data visualizations.

## Architecture

```
PostgreSQL 16 → FastAPI Backend → Next.js 14 Frontend
```

### Components

1. **Database Layer**: PostgreSQL 16 with Prisma ORM
2. **Backend API**: FastAPI with comprehensive analytics endpoints
3. **Frontend Dashboard**: Next.js 14 with React, Tailwind CSS, and Recharts

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Manual Setup

#### Backend

```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL="postgresql://buyer@localhost:5432/data_analytics"
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with API URL
npm run dev
```

## Features

### Backend API

- **Analytics Overview**: KPIs, trends, overview metrics
- **Customer Analytics**: Demographics, segmentation, gender breakdown, lifetime value, retention
- **Job Analytics**: Metrics, volume trends, status/type distribution, seasonal patterns, crew utilization
- **Revenue Analytics**: Trends, by branch/region/source, forecasts, by segment
- **Lead Analytics**: Demographics, conversion funnel, response time, source performance
- **Sales Performance**: Performance metrics, rankings, trends, comparison, efficiency

### Frontend Dashboard

- **Dark Mode UI**: Modern dark theme with high contrast
- **Mobile-First Design**: Responsive layout optimized for all screen sizes
- **Interactive Charts**: Recharts with hover tooltips and breakdowns
- **Universal Filtering**: Filter all analytics by branch, date range, sales person, etc.
- **Real-Time Data**: TanStack Query for efficient data fetching and caching
- **Sidebar Navigation**: Collapsible sidebar with octopus icon

### Dashboard Pages

- `/overview` - Dashboard overview with KPIs and summary charts
- `/customers` - Customer analytics hub
- `/customers/demographics` - Detailed customer demographics
- `/customers/segmentation` - Customer value segmentation
- `/customers/gender` - Gender breakdown analysis
- `/jobs` - Job metrics and analysis
- `/revenue` - Revenue trends and forecasts
- `/leads` - Lead conversion funnel
- `/sales` - Sales performance dashboard

## API Endpoints

All endpoints support universal filtering via query parameters:

- `branch_id`, `branch_name` - Filter by branch
- `date_from`, `date_to` - Date range filter (ISO format)
- `sales_person_id`, `sales_person_name` - Filter by sales person
- `job_status` - Comma-separated job statuses
- `aggregation_period` - daily, weekly, monthly, quarterly, yearly
- `limit`, `offset` - Pagination

### Example API Calls

```bash
# Get overview KPIs
curl "http://localhost:8000/api/v1/analytics/overview?aggregation_period=monthly"

# Get customer demographics
curl "http://localhost:8000/api/v1/customers/demographics?branch_name=NORTH%20YORK"

# Get revenue trends
curl "http://localhost:8000/api/v1/revenue/trends?date_from=2024-01-01&date_to=2024-12-31"
```

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── utils/       # Utility functions
│   │   └── main.py      # FastAPI app
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/             # App router pages
│   ├── components/      # React components
│   ├── lib/             # Utilities and API client
│   └── store/           # Zustand state management
├── prisma/              # Database schema
├── sql/queries/         # SQL analytics queries
└── docker-compose.yml   # Docker orchestration
```

## Development

### Backend Development

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests (when implemented)
pytest
```

### Frontend Development

```bash
cd frontend
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

## Environment Variables

### Backend

```bash
DATABASE_URL=postgresql://buyer@localhost:5432/data_analytics
DIRECT_DATABASE_URL=postgresql://buyer@localhost:5432/data_analytics
```

### Frontend

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Technology Stack

### Backend
- FastAPI 0.104+
- PostgreSQL 16
- psycopg2-binary
- Pydantic 2.0+

### Frontend
- Next.js 14 (App Router)
- React 19
- TypeScript
- Tailwind CSS 4
- Shadcn/ui
- Recharts
- TanStack Query
- Zustand

## Performance Considerations

- **API Response Time**: < 500ms target
- **Chart Rendering**: < 1 second for large datasets
- **Pagination**: Automatic for datasets > 50 items
- **Caching**: TanStack Query with 1-minute stale time
- **Database**: Connection pooling with 2-10 connections

## Mobile Optimization

- Touch-friendly interactions (44px minimum targets)
- Responsive charts that reflow for mobile
- Simplified navigation for small screens
- Optimized data loading for mobile networks

## Documentation

- Backend API: http://localhost:8000/docs (Swagger UI)
- Backend ReDoc: http://localhost:8000/redoc
- Frontend README: `frontend/README.md`
- Backend README: `backend/README.md`

## License

Proprietary - Internal Use Only

