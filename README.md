# Data Analytics V5

PostgreSQL-based data analytics project with comprehensive database schema, relationship management, and SQL analytics queries.

## Project Overview

This project provides a clean foundation for data analytics with:
- **PostgreSQL 16** database with Prisma schema management
- **Comprehensive data model** with 11 interconnected models
- **SQL analytics queries** for business intelligence
- **Relationship management scripts** for data integrity
- **Multi-agent development workflow** with specialized agents

## Project Structure

```
.
├── prisma/
│   └── schema.prisma          # Database schema (Prisma format)
├── data/
│   ├── raw/                   # Raw input data files (CSV, Excel)
│   ├── processed/             # Processed data files (Parquet)
│   └── manual_mappings/       # Manual data mapping files
├── sql/
│   └── queries/               # SQL analytics queries (129 queries)
├── scripts/                   # Essential relationship/import scripts
│   ├── relationships/         # Relationship establishment scripts
│   │   ├── complete_quote_linkage.py
│   │   └── link_badlead_to_leadstatus.py
│   ├── lookup/               # Lookup table population scripts
│   │   ├── populate_lead_sources.py
│   │   ├── populate_branches.py
│   │   └── merge_sales_person_variations.py
│   ├── timeline/             # Timeline and performance scripts
│   │   ├── populate_customer_timeline_fields.py
│   │   └── link_orphaned_performance_records.py
│   └── README.md             # Scripts documentation
├── config/                     # Configuration files
│   ├── .agent-config.json     # Multi-agent configuration
│   ├── .agent-*.id            # Agent identification files (4 files)
│   ├── .cursorrules*.md       # Cursor rules (7 files)
│   ├── docker-compose.yml     # PostgreSQL service configuration
│   └── README.md              # Configuration documentation
├── docs/                       # Documentation
│   ├── api/                   # API documentation
│   │   └── public-api-v1.json
│   ├── database_relationships.md
│   ├── architecture.md
│   ├── agent-coordination.md
│   ├── sql_queries_index.md
│   └── PROJECT_STRUCTURE.md   # Project structure documentation
├── tools/                      # Utility scripts and tools
│   ├── auto-commit.sh         # Auto-commit script
│   ├── manage-auto-commit.sh  # Auto-commit management
│   └── README.md              # Tools documentation
├── requirements.txt            # Python dependencies
└── pyproject.toml             # Python project configuration
```

## Database Schema

The database consists of 11 models organized around a central **Customer** model. All business understanding flows through customers.

### Business Logic Flow

1. **LeadStatus** = Central pool of all leads (BadLeads and LostLeads are compiled into this pool)
2. **Leads → Customers** = All customers originate from the lead pool
3. **Customers → BookedOpportunities** = Customers have booked opportunities
4. **BookedOpportunities → Jobs** = Booked opportunities flow into jobs
5. **Jobs & BookedOpportunities → SalesPerson & Branch** = Sales person and branch come from jobs and booked opportunities
6. **SalesPerson & Branch → Performance** = Flows into user performance and sales performance
7. **LeadSource** = Compiled lookup from all sources (jobs, booked opportunities, lead status, bad leads, lost leads)

### Core Models
- **Customer**: Central unified customer model - all contact details, relationships, and business understanding flow through customers
- **LeadStatus**: Central pool of all leads (BadLeads and LostLeads compiled here)
- **BookedOpportunity**: Booked opportunities that come from customers and flow into jobs
- **Job**: Job records (2019-2025) - only BOOKED/CLOSED jobs are linked to customers
- **BadLead**: Bad lead records (part of the lead pool)
- **LostLead**: Lost lead records (part of the lead pool)

### Performance Models
- **UserPerformance**: User call performance metrics (from SalesPerson & Branch)
- **SalesPerformance**: Sales person performance metrics (from SalesPerson & Branch)

### Lookup Tables
- **SalesPerson**: Normalized sales person names (extracted from Jobs & BookedOpportunities)
- **Branch**: Normalized branch names (extracted from Jobs & BookedOpportunities)
- **LeadSource**: Compiled from ALL sources (Jobs, BookedOpportunities, LeadStatus, BadLeads, LostLeads)

See `docs/database_relationships.md` for complete relationship documentation and the entity relationship diagram.

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 16 (via Docker)

### 1. Start PostgreSQL Database

```bash
# Start PostgreSQL container
docker-compose -f config/docker-compose.yml up -d

# Verify database is running
docker-compose -f config/docker-compose.yml ps
```

The database will be available at `localhost:5432` with:
- Database: `data_analytics`
- User: `buyer`
- Password: `postgres` (or set `POSTGRES_PASSWORD` environment variable)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database Schema

```bash
# Generate Prisma client
cd prisma
prisma generate

# Create initial migration from schema
prisma migrate dev --name init

# Apply migration to database
prisma migrate deploy
```

### 4. Environment Variables

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://buyer:postgres@localhost:5432/data_analytics
DIRECT_DATABASE_URL=postgresql://buyer:postgres@localhost:5432/data_analytics
```

## Essential Scripts

Scripts are organized by purpose in subdirectories. See `scripts/README.md` for detailed documentation.

### Relationships (`scripts/relationships/`)
Establish relationships between core models:
```bash
# Link LeadStatus and LostLead to BookedOpportunities
python scripts/relationships/complete_quote_linkage.py --execute

# Link BadLead to LeadStatus
python scripts/relationships/link_badlead_to_leadstatus.py --execute
```

### Lookup Tables (`scripts/lookup/`)
Populate and maintain lookup tables:
```bash
# Populate lead sources
python scripts/lookup/populate_lead_sources.py --execute

# Populate branches
python scripts/lookup/populate_branches.py --execute

# Merge sales person variations
python scripts/lookup/merge_sales_person_variations.py --execute
```

### Timeline (`scripts/timeline/`)
Populate timeline and performance data:
```bash
# Populate customer timeline fields
python scripts/timeline/populate_customer_timeline_fields.py --execute

# Link orphaned performance records
python scripts/timeline/link_orphaned_performance_records.py --execute
```

**Note**: All scripts support `--dry-run` mode (default) and `--execute` flag. Run in dry-run mode first to review changes.

## SQL Queries

The `sql/queries/` directory contains 129 SQL queries organized by category:

- **Analytics**: Customer segmentation, revenue analysis, heatmaps
- **Benchmarking**: Branch performance, sales person benchmarking
- **Customer Behavior**: Cohort analysis, lifetime value, retention
- **Forecasting**: Revenue forecasts, trend analysis
- **Geographic**: City-to-city routes, geographic distribution
- **Operational**: Capacity planning, efficiency metrics
- **Profitability**: ROI analysis, cost efficiency
- **And more...**

See `docs/sql_queries_index.md` for a complete index of all queries.

## Multi-Agent Development

This project uses a multi-agent development workflow with 4 specialized agents:

1. **Agent 1**: Frontend UI/UX Design Expert
2. **Agent 2**: Backend Specialist
3. **Agent 3**: Database/Scripts Specialist
4. **Agent 4**: Full-Stack Engineer

See `docs/agent-coordination.md` for coordination protocols and `.agent-config.json` for agent configuration.

## Documentation

- **`docs/database_relationships.md`**: Complete documentation of all database relationships
- **`docs/architecture.md`**: System architecture and data flow
- **`docs/agent-coordination.md`**: Multi-agent coordination protocols
- **`docs/sql_queries_index.md`**: Index of all SQL queries

## Data Files

- **`data/raw/`**: Raw input data files (CSV, Excel)
- **`data/processed/`**: Processed data files (Parquet format)
- **`data/manual_mappings/`**: Manual data mapping and review files

## Database Migrations

Migrations are managed through Prisma. To create a new migration:

```bash
cd prisma
prisma migrate dev --name <migration_name>
```

To apply migrations to production:

```bash
cd prisma
prisma migrate deploy
```

## Key Relationships

### Customer as Central Model
**All business understanding flows through customers:**
- Links to Jobs (one-to-many) - completed work for customers
- Links to BadLeads (one-to-many) - bad leads from the lead pool
- Links to BookedOpportunities (one-to-many) - opportunities that flow into jobs
- All contact details are connected to customers
- All customers originate from the lead pool (LeadStatus)

### Lead Flow
- **LeadStatus** = Central pool of all leads (BadLeads and LostLeads compiled here)
- **Leads → Customers** = All customers come from the lead pool
- **BookedOpportunities → Jobs** = Booked opportunities flow into jobs

### Quote Number Linking
- BookedOpportunity, LeadStatus, and LostLead all use `quote_number` for cross-table linking
- Tracks the journey: Lead (LeadStatus) → Opportunity (BookedOpportunity) → Job or Loss

### Lookup Tables
- **SalesPerson**: Extracted from Jobs & BookedOpportunities, flows into UserPerformance & SalesPerformance
- **Branch**: Extracted from Jobs & BookedOpportunities, flows into performance metrics
- **LeadSource**: Compiled from ALL sources (Jobs, BookedOpportunities, LeadStatus, BadLeads, LostLeads)

See `docs/database_relationships.md` for complete relationship details and the entity relationship diagram.

## Performance Considerations

- All foreign key columns are indexed
- Composite indexes on frequently queried combinations
- Use CTEs for complex multi-table joins
- Filter by status early (e.g., only BOOKED/CLOSED jobs for customers)

## License

Proprietary - Internal Use Only

