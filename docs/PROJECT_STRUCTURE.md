# Project Structure

This document describes the organized structure of the Data Analytics V5 project.

## Directory Organization

```
Data Analytics V5/
│
├── config/                     # Configuration files
│   ├── .agent-config.json     # Multi-agent configuration
│   ├── .agent-*.id            # Agent identification files (4 files)
│   ├── .cursorrules           # Global cursor rules
│   ├── .cursorrules*.md       # Cursor rules for agents (6 files)
│   ├── docker-compose.yml     # PostgreSQL service configuration
│   └── README.md              # Configuration documentation
├── .gitignore                 # Git ignore patterns
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Main project documentation
│
├── prisma/
│   └── schema.prisma          # Database schema (Prisma format)
│
├── data/
│   ├── raw/                   # Raw input data files (CSV, Excel)
│   ├── processed/             # Processed data files (Parquet)
│   └── manual_mappings/        # Manual data mapping files
│
├── sql/
│   └── queries/               # SQL analytics queries
│       ├── analytics/         # Analytics queries
│       ├── benchmarking/      # Benchmarking queries
│       ├── customer_behavior/ # Customer behavior queries
│       ├── data_quality/      # Data quality queries
│       ├── demographics/      # Demographics queries
│       ├── forecasting/       # Forecasting queries
│       ├── geographic/       # Geographic queries
│       ├── leads/            # Lead-related queries
│       ├── operational/      # Operational queries
│       ├── profitability/   # Profitability queries
│       └── referrals/        # Referral queries
│
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
│
├── docs/                      # Documentation
│   ├── api/                   # API documentation
│   │   └── public-api-v1.json
│   ├── database_relationships.md
│   ├── architecture.md
│   ├── agent-coordination.md
│   ├── sql_queries_index.md
│   └── PROJECT_STRUCTURE.md   # This file
│
└── tools/                     # Utility scripts and tools
    ├── auto-commit.sh         # Auto-commit script
    ├── manage-auto-commit.sh  # Auto-commit management
    ├── auto-commit.log        # Auto-commit log file
    ├── auto-commit.pid        # Auto-commit process ID
    └── README.md              # Tools documentation
```

## Organization Principles

### 1. Root Directory
- Contains only essential project files and top-level documentation
- Configuration files moved to `config/` directory for better organization
- Main `README.md` provides project overview
- Python dependencies (`requirements.txt`, `pyproject.toml`) remain at root

### 2. Scripts Organization
Scripts are organized by purpose:
- **`relationships/`**: Scripts that establish relationships between core models
- **`lookup/`**: Scripts that populate and maintain lookup tables
- **`timeline/`**: Scripts that populate timeline and performance data

### 3. Documentation Organization
- **`docs/`**: Main documentation directory
- **`docs/api/`**: API documentation files
- Each major component has its own documentation file

### 4. Tools Organization
- **`tools/`**: Utility scripts and maintenance tools
- Keeps root directory clean
- Auto-commit tools grouped together

### 5. Data Organization
- **`data/raw/`**: Original input data
- **`data/processed/`**: Processed/cleaned data
- **`data/manual_mappings/`**: Manual review and mapping files

### 6. SQL Queries Organization
- Organized by functional category in subdirectories
- Makes it easy to find queries by purpose

## File Naming Conventions

- **Python scripts**: `snake_case.py`
- **Documentation**: `kebab-case.md`
- **Configuration**: `.kebab-case.json` or `.kebab-case.md`
- **Data files**: Original names preserved

## Access Patterns

### Running Scripts
```bash
# Relationships
python scripts/relationships/complete_quote_linkage.py --execute

# Lookup tables
python scripts/lookup/populate_lead_sources.py --execute

# Timeline
python scripts/timeline/populate_customer_timeline_fields.py --execute
```

### Accessing Documentation
- Main docs: `docs/*.md`
- API docs: `docs/api/public-api-v1.json`
- Scripts docs: `scripts/README.md`
- Tools docs: `tools/README.md`
- Config docs: `config/README.md`

### Accessing Configuration
- Agent config: `config/.agent-config.json`
- Agent IDs: `config/.agent-*.id`
- Cursor rules: `config/.cursorrules*.md`
- Docker compose: `config/docker-compose.yml`

### Accessing Data
- Raw data: `data/raw/`
- Processed data: `data/processed/`
- Manual mappings: `data/manual_mappings/`

## Benefits of This Organization

1. **Clear Separation**: Each type of file has its place
2. **Easy Navigation**: Logical grouping makes files easy to find
3. **Scalability**: Structure supports growth without clutter
4. **Maintainability**: Related files are grouped together
5. **Documentation**: Each major section has its own README

