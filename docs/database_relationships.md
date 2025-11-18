# Database Relationships Documentation

## Overview

This document describes all relationships between database modules, providing a comprehensive view of how data flows through the system.

## Business Logic & Data Categorization

### Key Definitions

- **Customers**: People who have booked or closed jobs (actual customers)
- **Leads**: Users that have NOT booked a job yet (potential customers)
- **Bad Leads**: Leads that are marked as bad, should be related to LeadStatus module
- **Lost Leads**: Leads that were lost, should be related to LeadStatus module
- **Lead Status**: Central module providing complete picture of all total leads
- **Jobs**: Only booked and closed jobs come from customers (not leads)
- **Lost Jobs**: Different from closed jobs

### Critical Insights

- All customers were leads at some point
- Total customer base = customers + leads (to understand conversion percentage)
- LeadStatus is the central hub for understanding all leads
- Need to track conversion: leads → customers

## Entity Relationship Diagram

```
┌─────────────┐
│  Customer   │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────┐      ┌──────────────┐
│   Jobs   │      │ Bad Leads    │
│(BOOKED/  │      │              │
│ CLOSED)  │      └──────────────┘
└──────────┘
       │
       │
┌──────────────┐
│Booked        │
│Opportunities │
└──────┬───────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│ Lead Status │  │ Lost Leads  │
│  (Central)  │  │             │
└─────────────┘  └─────────────┘

┌──────────────┐
│Sales Person  │
│  (Lookup)    │
└──────┬───────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │
       ▼              ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   Jobs   │  │Booked        │  │Lead      │  │Sales     │  │User      │
│          │  │Opportunities │  │Status    │  │Performance│ │Performance│
└──────────┘  └──────────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Direct Relationships

### Customer Relationships

1. **Customer → Jobs** (One-to-Many)
   - **Field**: `jobs.customer_id` → `customers.id`
   - **Constraint**: Only BOOKED and CLOSED jobs are linked (customers, not leads)
   - **Purpose**: Track jobs completed by customers

2. **Customer → BadLeads** (One-to-Many)
   - **Field**: `bad_leads.customer_id` → `customers.id`
   - **Purpose**: Track bad leads associated with customers
   - **Note**: Bad leads should also link to LeadStatus for complete picture

3. **Customer → BookedOpportunities** (One-to-Many)
   - **Field**: `booked_opportunities.customer_id` → `customers.id`
   - **Purpose**: Track booked opportunities for customers

### Quote Number Relationships

4. **LeadStatus → BookedOpportunity** (Many-to-One)
   - **Field**: `lead_status.booked_opportunity_id` → `booked_opportunities.id`
   - **Link Method**: Via `quote_number` matching
   - **Purpose**: Connect lead status records to booked opportunities

5. **LostLead → BookedOpportunity** (Many-to-One)
   - **Field**: `lost_leads.booked_opportunity_id` → `booked_opportunities.id`
   - **Link Method**: Via `quote_number` matching
   - **Purpose**: Connect lost leads to booked opportunities

### Sales Person Relationships

6. **SalesPerson → Jobs** (One-to-Many)
   - **Field**: `jobs.sales_person_id` → `sales_persons.id`
   - **Link Method**: Name matching (normalized)
   - **Purpose**: Track which sales person handled each job

7. **SalesPerson → BookedOpportunities** (One-to-Many)
   - **Field**: `booked_opportunities.sales_person_id` → `sales_persons.id`
   - **Link Method**: Name matching (normalized)
   - **Purpose**: Track which sales person handled each booked opportunity

8. **SalesPerson → LeadStatus** (One-to-Many)
   - **Field**: `lead_status.sales_person_id` → `sales_persons.id`
   - **Link Method**: Name matching (normalized)
   - **Purpose**: Track which sales person handled each lead

9. **SalesPerson → SalesPerformance** (One-to-One)
   - **Field**: `sales_performance.sales_person_id` → `sales_persons.id`
   - **Link Method**: Name matching (normalized)
   - **Purpose**: Link sales performance metrics to sales person

10. **SalesPerson → UserPerformance** (One-to-One)
    - **Field**: `user_performance.sales_person_id` → `sales_persons.id`
    - **Link Method**: Name matching (normalized)
    - **Purpose**: Link user performance metrics to sales person

## Indirect Relationships

### LeadStatus as Central Hub

**LeadStatus** serves as the central module for understanding all leads:

- **LeadStatus ↔ BookedOpportunity**: Direct link via `quote_number`
- **LeadStatus ↔ LostLead**: Indirect link via `quote_number` (both reference BookedOpportunity)
- **LeadStatus ↔ Customer**: Indirect link via BookedOpportunity → Customer
- **LeadStatus ↔ BadLead**: Should be linked (via customer matching or quote_number)

### Customer Conversion Path

The typical conversion path:

1. **Lead** → Created in LeadStatus
2. **Lead → BookedOpportunity** → Via quote_number
3. **BookedOpportunity → Customer** → Via customer_id
4. **Customer → Jobs** → Via customer_id (BOOKED/CLOSED only)

## Join Patterns

### Common Query Patterns

#### 1. Customer Complete Profile
```sql
select *
from customers c
left join jobs j on c.id = j.customer_id and j.opportunity_status in ('BOOKED', 'CLOSED')
left join bad_leads bl on c.id = bl.customer_id
left join booked_opportunities bo on c.id = bo.customer_id
left join lead_status ls on bo.quote_number = ls.quote_number
left join lost_leads ll on bo.quote_number = ll.quote_number
```

#### 2. Lead to Customer Journey
```sql
select *
from lead_status ls
left join booked_opportunities bo on ls.quote_number = bo.quote_number
left join customers c on bo.customer_id = c.id
left join jobs j on c.id = j.customer_id and j.opportunity_status in ('BOOKED', 'CLOSED')
```

#### 3. Sales Person Cross-Module
```sql
select *
from sales_persons sp
left join jobs j on sp.id = j.sales_person_id
left join booked_opportunities bo on sp.id = bo.sales_person_id
left join lead_status ls on sp.id = ls.sales_person_id
left join sales_performance spf on sp.id = spf.sales_person_id
```

## Data Integrity Rules

1. **Jobs**: Only BOOKED and CLOSED jobs should have `customer_id` set (these are customers, not leads)
2. **LeadStatus**: Central hub - all leads should have a record here
3. **Quote Numbers**: Should be unique within each table, used for cross-table linking
4. **Sales Person Names**: Normalized in `sales_persons` table for consistent linking

## Performance Considerations

### Indexes

All foreign key columns are indexed for performance:
- `jobs.customer_id`
- `jobs.sales_person_id`
- `booked_opportunities.customer_id`
- `booked_opportunities.sales_person_id`
- `lead_status.booked_opportunity_id`
- `lead_status.sales_person_id`
- `lost_leads.booked_opportunity_id`
- `sales_performance.sales_person_id`
- `user_performance.sales_person_id`

### Query Optimization

- Use CTEs for complex multi-table joins
- Filter jobs by `opportunity_status` early (only BOOKED/CLOSED for customers)
- Use `quote_number` for efficient linking between LeadStatus, LostLead, and BookedOpportunity
- Use normalized sales person names for consistent matching

## Migration Notes

The following migrations establish these relationships:

1. **20251117185005_add_sales_person_table**: Creates `sales_persons` lookup table
2. **20251117185006_add_quote_number_foreign_keys**: Adds foreign key columns
3. **20251117185007_populate_sales_person_links**: Populates lookup table and establishes links

## New Relationships (Latest Updates)

### Branch Relationships

11. **Branch → Jobs** (One-to-Many)
    - **Field**: `jobs.branch_id` → `branches.id`
    - **Link Method**: Name matching (normalized)
    - **Purpose**: Normalize branch names and link jobs to branches

12. **Branch → BookedOpportunities** (One-to-Many)
    - **Field**: `booked_opportunities.branch_id` → `branches.id`
    - **Link Method**: Name matching (normalized)
    - **Purpose**: Link booked opportunities to branches

13. **Branch → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.branch_id` → `branches.id`
    - **Link Method**: Name matching (normalized)
    - **Purpose**: Link lead status records to branches

### Lead Source Relationships

14. **LeadSource → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.lead_source_id` → `lead_sources.id`
    - **Link Method**: Normalized referral_source matching
    - **Purpose**: Track and categorize lead sources

15. **LeadSource → BadLead** (One-to-Many)
    - **Field**: `bad_leads.lead_source_id` → `lead_sources.id`
    - **Link Method**: Normalized referral_source matching
    - **Purpose**: Track lead sources for bad leads

16. **LeadSource → LostLead** (One-to-Many)
    - **Field**: `lost_leads.lead_source_id` → `lead_sources.id`
    - **Link Method**: Normalized referral_source matching
    - **Purpose**: Track lead sources for lost leads

### BadLead Relationships

17. **BadLead → LeadStatus** (Many-to-One)
    - **Field**: `bad_leads.lead_status_id` → `lead_status.id`
    - **Link Method**: Customer matching (email, phone, or customer_id)
    - **Purpose**: Connect bad leads to lead status for complete lead picture
    - **Status**: ✅ Implemented

### Customer Timeline Tracking

18. **Customer Timeline Fields**
    - **first_lead_date**: Earliest date from LeadStatus, BadLead, or LostLead
    - **conversion_date**: Earliest date from BookedOpportunity or Job (BOOKED/CLOSED)
    - **merge_history**: JSONB field tracking merge operations with method, confidence, timestamp, and merged_by
    - **Purpose**: Track complete customer journey from lead to conversion

## Updated Entity Relationship Diagram

```
┌─────────────┐
│  Customer   │ (with first_lead_date, conversion_date, merge_history)
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────┐      ┌──────────────┐
│   Jobs   │      │ Bad Leads    │──┐
│(BOOKED/  │      │              │  │
│ CLOSED)  │      └──────────────┘  │
└──────┬───┘                        │
       │                            │
       │                            │
┌──────────────┐                    │
│Booked        │                    │
│Opportunities │                    │
└──────┬───────┘                    │
       │                            │
       ├──────────────┐             │
       │              │             │
       ▼              ▼             │
┌─────────────┐  ┌─────────────┐   │
│ Lead Status │◄─┼─ Bad Leads  │───┘
│  (Central)  │  │             │
└──────┬──────┘  └─────────────┘
       │
       ▼
┌─────────────┐
│ Lost Leads  │
└─────────────┘

┌──────────────┐      ┌──────────────┐
│Sales Person  │      │   Branch     │
│  (Lookup)    │      │  (Lookup)    │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └─────────┬───────────┘
                 │
       ┌─────────┼─────────┐
       │         │         │
       ▼         ▼         ▼
   [Jobs, BO, LS]    [Jobs, BO, LS]

┌──────────────┐
│ Lead Source  │
│  (Lookup)    │
└──────┬───────┘
       │
       └─────────┬─────────┐
                 │         │
                 ▼         ▼
         [LS, BL, LL]  [LeadStatus, BadLead, LostLead]
```

## Updated Join Patterns

### 1. Customer Complete Profile (Enhanced)
```sql
select *
from customers c
left join jobs j on c.id = j.customer_id and j.opportunity_status in ('BOOKED', 'CLOSED')
left join bad_leads bl on c.id = bl.customer_id
left join lead_status ls on bl.lead_status_id = ls.id
left join booked_opportunities bo on c.id = bo.customer_id
left join lead_status ls2 on bo.quote_number = ls2.quote_number
left join lost_leads ll on bo.quote_number = ll.quote_number
left join branches b on j.branch_id = b.id
left join lead_sources lsrc on ls2.lead_source_id = lsrc.id
```

### 2. Lead to Customer Journey (Enhanced)
```sql
select *
from lead_status ls
left join booked_opportunities bo on ls.quote_number = bo.quote_number
left join customers c on bo.customer_id = c.id
left join jobs j on c.id = j.customer_id and j.opportunity_status in ('BOOKED', 'CLOSED')
left join bad_leads bl on ls.id = bl.lead_status_id
left join branches b on ls.branch_id = b.id
left join lead_sources lsrc on ls.lead_source_id = lsrc.id
where c.first_lead_date is not null
  and c.conversion_date is not null
```

### 3. Sales Person Cross-Module (Enhanced)
```sql
select *
from sales_persons sp
left join jobs j on sp.id = j.sales_person_id
left join booked_opportunities bo on sp.id = bo.sales_person_id
left join lead_status ls on sp.id = ls.sales_person_id
left join sales_performance spf on sp.id = spf.sales_person_id
left join user_performance up on sp.id = up.sales_person_id
```

### 4. Branch Performance Analysis
```sql
select 
    b.name as branch_name,
    count(distinct j.id) as job_count,
    count(distinct bo.id) as booked_opportunities,
    count(distinct ls.id) as leads,
    sum(j.total_actual_cost) as revenue
from branches b
left join jobs j on b.id = j.branch_id
left join booked_opportunities bo on b.id = bo.branch_id
left join lead_status ls on b.id = ls.branch_id
group by b.name
```

### 5. Lead Source Performance
```sql
select 
    lsrc.name as lead_source,
    lsrc.category,
    count(distinct ls.id) as total_leads,
    count(distinct bo.id) as conversions,
    count(distinct c.id) as customers
from lead_sources lsrc
left join lead_status ls on lsrc.id = ls.lead_source_id
left join booked_opportunities bo on ls.booked_opportunity_id = bo.id
left join customers c on bo.customer_id = c.id
group by lsrc.name, lsrc.category
```

## Updated Data Integrity Rules

1. **Jobs**: Only BOOKED and CLOSED jobs should have `customer_id` set (these are customers, not leads)
2. **LeadStatus**: Central hub - all leads should have a record here
3. **Quote Numbers**: Should be unique within each table, used for cross-table linking
4. **Sales Person Names**: Normalized in `sales_persons` table for consistent linking
5. **Branch Names**: Normalized in `branches` table for consistent linking
6. **Lead Sources**: Normalized in `lead_sources` table with categories
7. **BadLead → LeadStatus**: All bad leads should link to LeadStatus when possible
8. **Customer Timeline**: `first_lead_date` and `conversion_date` should be populated for complete journey tracking
9. **Merge History**: All customer merges should be tracked in `merge_history` JSONB field

## Updated Performance Considerations

### New Indexes

- **Composite Indexes**:
  - `jobs(customer_id, opportunity_status)` - Optimizes customer job queries
  - `booked_opportunities(customer_id, booked_date)` - Optimizes customer timeline queries

- **Branch Indexes**:
  - `jobs.branch_id`
  - `booked_opportunities.branch_id`
  - `lead_status.branch_id`
  - `branches.normalized_name`

- **Lead Source Indexes**:
  - `lead_status.lead_source_id`
  - `bad_leads.lead_source_id`
  - `lost_leads.lead_source_id`
  - `lead_sources.category`

- **Customer Timeline Indexes**:
  - `customers.first_lead_date`
  - `customers.conversion_date`

- **BadLead Linkage**:
  - `bad_leads.lead_status_id`

## Updated Migration Notes

The following migrations establish these relationships:

1. **20251117185005_add_sales_person_table**: Creates `sales_persons` lookup table
2. **20251117185006_add_quote_number_foreign_keys**: Adds foreign key columns
3. **20251117185007_populate_sales_person_links**: Populates lookup table and establishes links
4. **complete_schema_updates** (Latest):
   - Adds `lead_status_id` to BadLead
   - Adds `lead_source_id` to LeadStatus, BadLead, LostLead
   - Creates `lead_sources` lookup table
   - Creates `branches` lookup table
   - Adds `branch_id` to Jobs, BookedOpportunities, LeadStatus
   - Adds `first_lead_date` and `conversion_date` to Customer
   - Adds `merge_history` JSONB to Customer
   - Creates composite indexes for performance

## Data Population Scripts

The following scripts populate the new relationships:

1. **complete_quote_linkage.py**: Links LeadStatus and LostLead to BookedOpportunities via quote_number
2. **link_badlead_to_leadstatus.py**: Links BadLead to LeadStatus via customer matching
3. **populate_lead_sources.py**: Creates lead_sources and links records
4. **populate_branches.py**: Creates branches and links records
5. **populate_customer_timeline_fields.py**: Populates first_lead_date and conversion_date
6. **link_orphaned_performance_records.py**: Links orphaned UserPerformance and SalesPerformance records

## Integrity Monitoring

Automated integrity checks monitor:

1. **Orphaned Records**: UserPerformance and SalesPerformance without sales_person_id
2. **Linkage Rates**:
   - Job-Customer linkage (threshold: 95%)
   - LeadStatus-BookedOpportunity linkage (threshold: 80%)
   - BadLead-LeadStatus linkage (threshold: 70%)
3. **Historical Tracking**: Results stored in `integrity_check_history` table

Run integrity checks:
```bash
python scripts/setup_integrity_monitoring.py --setup --execute
python scripts/setup_integrity_monitoring.py --execute
```

## Future Enhancements

1. ✅ **BadLead → LeadStatus**: Direct link implemented
2. ✅ **Fuzzy Matching**: Enhanced sales person name matching with Levenshtein distance
3. ✅ **Lead Source Tracking**: Normalized lead_sources lookup table
4. ✅ **Conversion Analytics**: Customer timeline fields for journey tracking
5. ✅ **Branch Normalization**: Branches lookup table for consistent linking
6. ✅ **Merge History Tracking**: JSONB field for customer merge operations
7. **Automated Alerts**: Email/Slack notifications for integrity check failures
8. **Data Quality Dashboard**: Visual representation of linkage rates and orphaned records

