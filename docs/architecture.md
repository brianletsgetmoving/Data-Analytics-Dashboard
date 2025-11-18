# Architecture Documentation

## Data Flow Diagram

```
┌─────────────┐
│  CSV Files  │
│  (7 job +   │
│  6 other)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Data Cleaning      │
│  - Column normalize │
│  - Branch clean     │
│  - Test data filter │
│  - Date parse       │
│  - Email correct    │
│  - Phone normalize  │
│  - Address parse    │
│  - State normalize  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Great Expectations │
│  - Completeness     │
│  - Accuracy         │
│  - Consistency      │
│  - Uniqueness       │
│  - Timeliness       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Splink Entity      │
│  Resolution         │
│  - Blocking rules   │
│  - Comparison levels│
│  - EM algorithm     │
│  - Match predictions│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Customer           │
│  Unification        │
│  - Primary match    │
│  - Secondary match  │
│  - Tertiary match   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  PostgreSQL Import  │
│  - Staging tables    │
│  - Live tables      │
│  - Foreign keys     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  SmartMoving API    │
│  - Enrich customers │
│  - Push merged      │
│  - Two-way sync     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Continuous         │
│  Monitoring         │
│  - Post-import      │
│  - SLA alerts       │
│  - Weekly reports   │
└─────────────────────┘
```

## Component Interactions

### Data Cleaning Pipeline

The cleaning pipeline processes all CSV files through multiple stages:

1. **Column Normalization**: Converts headers to snake_case
2. **Branch Cleaning**: Removes emojis, standardizes names
3. **Test Data Filtering**: Rejects test records
4. **Date Parsing**: Converts M/D/YYYY to ISO 8601
5. **Email Correction**: Fixes common typos
6. **Phone Normalization**: Standardizes formats
7. **Address Parsing**: Extracts components
8. **State Normalization**: Converts abbreviations to full names

### Entity Resolution (Splink)

Splink uses probabilistic matching with:

- **Blocking Rules**: Reduces pairwise comparisons
  - Same origin_city AND destination_city
  - Exact phone match
  - Exact email match
  - Same last name (first 3 chars) AND origin_city
  - Same first name initial AND destination_city

- **Comparison Levels**: Match tiers for each field
  - Exact match
  - Fuzzy match (Jaro ≥ 0.85)
  - No match

- **Parameter Estimation**: EM algorithm learns match probabilities

- **Match Classification**:
  - >95%: Auto-merge
  - 75-95%: Manual review
  - <75%: Reject

### Customer Unification

Three-tier matching strategy:

1. **Primary**: Phone number (exact, >95%)
2. **Secondary**: Email address (exact, >95%)
3. **Tertiary**: Name + origin_city + destination_city (Splink >95%)

### Data Quality Monitoring

Continuous monitoring tracks:

- **Completeness**: Email, phone, address non-null rates
- **Accuracy**: Format validation
- **Uniqueness**: Duplicate rates
- **Timeliness**: Data freshness

SLA violations trigger automated alerts via email/Slack.

## Database Schema

### Core Models

1. **Job**: Unified job records (2019-2025)
2. **Customer**: Central unified customer model
3. **BadLead**: Bad lead records
4. **BookedOpportunity**: Booked opportunities
5. **LeadStatus**: Lead status tracking
6. **LostLead**: Lost lead records
7. **UserPerformance**: User call performance
8. **SalesPerformance**: Sales person performance
9. **CustomerDeduplicationLog**: Audit trail for merges

### Relationships

- Customer → Jobs (one-to-many)
- Customer → BadLeads (one-to-many)
- Customer → BookedOpportunities (one-to-many)
- Customer → CustomerDeduplicationLog (one-to-many)

## Performance Considerations

- **Connection Pooling**: Prisma Accelerate for production
- **Indexing**: Strategic indexes on foreign keys and frequently queried columns
- **Batch Processing**: Large imports processed in chunks
- **Rate Limiting**: API calls throttled to respect limits

## Security

- **RLS Policies**: Row-level security on sensitive tables
- **Audit Logging**: All Customer table changes logged
- **API Authentication**: Bearer token authentication for SmartMoving API
- **Environment Variables**: Sensitive data stored in .env (not committed)

