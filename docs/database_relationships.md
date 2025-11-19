# Database Relationships Documentation

## Overview

This document describes all relationships between database models as defined in the Prisma schema. The relationships are organized by model and include both direct foreign key relationships and indirect relationships via lookup tables.

## Entity Relationship Diagram

```
┌─────────────┐
│  Customer   │ (Central Model)
└──────┬──────┘
       │
       ├─────────────────┬──────────────────┐
       │                 │                  │
       ▼                 ▼                  ▼
┌──────────┐      ┌──────────────┐  ┌──────────────┐
│   Jobs   │      │  BadLeads    │  │Booked        │
│          │      │              │  │Opportunities │
└────┬─────┘      └──────┬───────┘  └──────┬───────┘
     │                   │                 │
     │                   │                 │
     ├───────────┐       │                 ├──────────────┐
     │           │       │                 │              │
     ▼           ▼       ▼                 ▼              ▼
┌──────────┐ ┌──────────┐ ┌─────────────┐ ┌─────────────┐
│SalesPerson│ │ Branch   │ │ LeadStatus │ │ LostLeads   │
│ (Lookup) │ │ (Lookup) │ │  (Central)  │ │             │
└──────────┘ └──────────┘ └──────┬──────┘ └─────────────┘
     │                            │
     │                            │
     ├────────────────────────────┘
     │
     ▼
┌──────────────┐      ┌──────────────┐
│UserPerformance│     │SalesPerformance│
└──────────────┘      └──────────────┘

┌──────────────┐
│ LeadSource   │
│  (Lookup)    │
└──────┬───────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
       ▼              ▼              ▼
[LeadStatus]    [BadLeads]    [LostLeads]
```

## Direct Relationships

### Customer Model

**Customer** is the central unified model that links to multiple entities:

1. **Customer → Jobs** (One-to-Many)
   - **Field**: `jobs.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Purpose**: Links jobs to customers. Only BOOKED and CLOSED jobs should typically be linked to customers.

2. **Customer → BadLeads** (One-to-Many)
   - **Field**: `bad_leads.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Purpose**: Links bad leads to customers.

3. **Customer → BookedOpportunities** (One-to-Many)
   - **Field**: `booked_opportunities.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Purpose**: Links booked opportunities to customers.

### Job Model

4. **Job → Customer** (Many-to-One)
   - **Field**: `jobs.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Index**: `@@index([customerId])`, `@@index([customerId, opportunityStatus])`

5. **Job → SalesPerson** (Many-to-One)
   - **Field**: `jobs.sales_person_id` → `sales_persons.id`
   - **Constraint**: `onDelete: SetNull`
   - **Index**: `@@index([salesPersonId])`

6. **Job → Branch** (Many-to-One)
   - **Field**: `jobs.branch_id` → `branches.id`
   - **Constraint**: `onDelete: SetNull`
   - **Index**: `@@index([branchId])`, `@@index([branchId, opportunityStatus, jobDate])`

### BadLead Model

7. **BadLead → Customer** (Many-to-One)
   - **Field**: `bad_leads.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Index**: `@@index([customerId])`

8. **BadLead → LeadStatus** (Many-to-One)
   - **Field**: `bad_leads.lead_status_id` → `lead_status.id`
   - **Constraint**: `onDelete: SetNull`
   - **Index**: `@@index([leadStatusId])`
   - **Purpose**: Links bad leads to lead status records for complete lead tracking.

9. **BadLead → LeadSource** (Many-to-One)
   - **Field**: `bad_leads.lead_source_id` → `lead_sources.id`
   - **Constraint**: `onDelete: SetNull`
   - **Index**: `@@index([leadSourceId])`

### BookedOpportunity Model

10. **BookedOpportunity → Customer** (Many-to-One)
    - **Field**: `booked_opportunities.customer_id` → `customers.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([customerId])`, `@@index([customerId, bookedDate])`, `@@index([customerId, branchId, bookedDate])`

11. **BookedOpportunity → SalesPerson** (Many-to-One)
    - **Field**: `booked_opportunities.sales_person_id` → `sales_persons.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([salesPersonId])`

12. **BookedOpportunity → Branch** (Many-to-One)
    - **Field**: `booked_opportunities.branch_id` → `branches.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([branchId])`

13. **BookedOpportunity → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.booked_opportunity_id` → `booked_opportunities.id`
    - **Constraint**: `onDelete: SetNull`
    - **Link Method**: Via `quote_number` matching (both have unique `quote_number` fields)
    - **Purpose**: Links lead status records to booked opportunities.

14. **BookedOpportunity → LostLead** (One-to-Many)
    - **Field**: `lost_leads.booked_opportunity_id` → `booked_opportunities.id`
    - **Constraint**: `onDelete: SetNull`
    - **Link Method**: Via `quote_number` matching (both have unique `quote_number` fields)
    - **Purpose**: Links lost leads to booked opportunities.

### LeadStatus Model

15. **LeadStatus → BookedOpportunity** (Many-to-One)
    - **Field**: `lead_status.booked_opportunity_id` → `booked_opportunities.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([bookedOpportunityId])`
    - **Link Method**: Via `quote_number` matching

16. **LeadStatus → SalesPerson** (Many-to-One)
    - **Field**: `lead_status.sales_person_id` → `sales_persons.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([salesPersonId])`

17. **LeadStatus → LeadSource** (Many-to-One)
    - **Field**: `lead_status.lead_source_id` → `lead_sources.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([leadSourceId])`, `@@index([leadSourceId, createdAt])`

18. **LeadStatus → Branch** (Many-to-One)
    - **Field**: `lead_status.branch_id` → `branches.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([branchId])`

19. **LeadStatus → BadLead** (One-to-Many)
    - **Field**: `bad_leads.lead_status_id` → `lead_status.id`
    - **Purpose**: Links bad leads to lead status records.

### LostLead Model

20. **LostLead → BookedOpportunity** (Many-to-One)
    - **Field**: `lost_leads.booked_opportunity_id` → `booked_opportunities.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([bookedOpportunityId])`
    - **Link Method**: Via `quote_number` matching

21. **LostLead → LeadSource** (Many-to-One)
    - **Field**: `lost_leads.lead_source_id` → `lead_sources.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([leadSourceId])`

### UserPerformance Model

22. **UserPerformance → SalesPerson** (Many-to-One)
    - **Field**: `user_performance.sales_person_id` → `sales_persons.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([salesPersonId])`
    - **Note**: `name` field is unique, used for matching to sales persons.

### SalesPerformance Model

23. **SalesPerformance → SalesPerson** (Many-to-One)
    - **Field**: `sales_performance.sales_person_id` → `sales_persons.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([salesPersonId])`
    - **Note**: `name` field is unique, used for matching to sales persons.

### SalesPerson Model (Lookup Table)

24. **SalesPerson → Jobs** (One-to-Many)
    - **Field**: `jobs.sales_person_id` → `sales_persons.id`
    - **Purpose**: Normalizes sales person names across all modules.

25. **SalesPerson → BookedOpportunities** (One-to-Many)
    - **Field**: `booked_opportunities.sales_person_id` → `sales_persons.id`

26. **SalesPerson → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.sales_person_id` → `sales_persons.id`

27. **SalesPerson → UserPerformance** (One-to-Many)
    - **Field**: `user_performance.sales_person_id` → `sales_persons.id`

28. **SalesPerson → SalesPerformance** (One-to-Many)
    - **Field**: `sales_performance.sales_person_id` → `sales_persons.id`

### LeadSource Model (Lookup Table)

29. **LeadSource → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.lead_source_id` → `lead_sources.id`
    - **Purpose**: Normalizes and categorizes lead sources.

30. **LeadSource → BadLeads** (One-to-Many)
    - **Field**: `bad_leads.lead_source_id` → `lead_sources.id`

31. **LeadSource → LostLeads** (One-to-Many)
    - **Field**: `lost_leads.lead_source_id` → `lead_sources.id`

### Branch Model (Lookup Table)

32. **Branch → Jobs** (One-to-Many)
    - **Field**: `jobs.branch_id` → `branches.id`
    - **Purpose**: Normalizes branch names across all modules.

33. **Branch → BookedOpportunities** (One-to-Many)
    - **Field**: `booked_opportunities.branch_id` → `branches.id`

34. **Branch → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.branch_id` → `branches.id`

## Indirect Relationships

### Quote Number Linking

**BookedOpportunity**, **LeadStatus**, and **LostLead** all have unique `quote_number` fields that are used for cross-table linking:

- **BookedOpportunity.quoteNumber** (unique)
- **LeadStatus.quoteNumber** (unique)
- **LostLead.quoteNumber** (unique)

These tables are linked via foreign keys (`booked_opportunity_id`), but the `quote_number` field provides an alternative linking mechanism and is used in scripts for establishing relationships.

### Customer Journey Tracking

The **Customer** model includes timeline fields for tracking the customer journey:

- **firstLeadDate**: Earliest date from LeadStatus, BadLead, or LostLead
- **conversionDate**: Earliest date from BookedOpportunity or Job (BOOKED/CLOSED)
- **mergeHistory**: JSONB field tracking merge operations with method, confidence, timestamp, and merged_by

## Common Join Patterns

### 1. Customer Complete Profile

```sql
select *
from customers c
left join jobs j on c.id = j.customer_id
left join bad_leads bl on c.id = bl.customer_id
left join booked_opportunities bo on c.id = bo.customer_id
left join lead_status ls on bo.quote_number = ls.quote_number
left join lost_leads ll on bo.quote_number = ll.quote_number
left join sales_persons sp on j.sales_person_id = sp.id
left join branches b on j.branch_id = b.id
left join lead_sources lsrc on ls.lead_source_id = lsrc.id
```

### 2. Lead to Customer Journey

```sql
select *
from lead_status ls
left join booked_opportunities bo on ls.booked_opportunity_id = bo.id
left join customers c on bo.customer_id = c.id
left join jobs j on c.id = j.customer_id
left join bad_leads bl on ls.id = bl.lead_status_id
left join branches b on ls.branch_id = b.id
left join lead_sources lsrc on ls.lead_source_id = lsrc.id
where c.first_lead_date is not null
  and c.conversion_date is not null
```

### 3. Sales Person Cross-Module Analysis

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

## Data Integrity Rules

1. **Jobs**: Only BOOKED and CLOSED jobs should typically have `customer_id` set (these represent actual customers, not leads).

2. **Quote Numbers**: Should be unique within each table (`BookedOpportunity`, `LeadStatus`, `LostLead`) and used for cross-table linking.

3. **Sales Person Names**: Normalized in `sales_persons` table via `normalizedName` field for consistent linking across modules.

4. **Branch Names**: Normalized in `branches` table via `normalizedName` field for consistent linking.

5. **Lead Sources**: Normalized in `lead_sources` table with optional `category` for classification.

6. **BadLead → LeadStatus**: All bad leads should link to LeadStatus when possible for complete lead tracking.

7. **Customer Timeline**: `first_lead_date` and `conversion_date` should be populated to track complete customer journey.

8. **Merge History**: All customer merges should be tracked in `merge_history` JSONB field.

## Performance Considerations

### Indexes

All foreign key columns are indexed for performance. Key composite indexes include:

- **Jobs**: `(customer_id, opportunity_status)`, `(opportunity_status, job_date, is_duplicate)`, `(branch_id, opportunity_status, job_date)`
- **BookedOpportunities**: `(customer_id, booked_date)`, `(customer_id, branch_id, booked_date)`
- **Customers**: `(first_lead_date, conversion_date)`
- **LeadStatus**: `(lead_source_id, created_at)`

### Query Optimization

- Use CTEs for complex multi-table joins
- Filter jobs by `opportunity_status` early (only BOOKED/CLOSED for customers)
- Use `quote_number` for efficient linking between LeadStatus, LostLead, and BookedOpportunity
- Use normalized names in lookup tables for consistent matching
- Leverage composite indexes for date range and status filtering

## Lookup Tables

### SalesPerson
- **Purpose**: Normalizes sales person names across Jobs, BookedOpportunities, LeadStatus, UserPerformance, and SalesPerformance
- **Key Fields**: `name` (unique), `normalizedName` (indexed)

### Branch
- **Purpose**: Normalizes branch names across Jobs, BookedOpportunities, and LeadStatus
- **Key Fields**: `name` (unique), `normalizedName` (indexed), `city`, `state`, `isActive`

### LeadSource
- **Purpose**: Normalizes and categorizes lead sources across LeadStatus, BadLeads, and LostLeads
- **Key Fields**: `name` (unique), `category` (indexed), `isActive` (indexed)

## Essential Scripts

The following scripts establish and maintain relationships:

1. **complete_quote_linkage.py**: Links LeadStatus and LostLead to BookedOpportunities via quote_number
2. **link_badlead_to_leadstatus.py**: Links BadLead to LeadStatus via customer matching
3. **populate_lead_sources.py**: Creates lead_sources lookup table and links records
4. **populate_branches.py**: Creates branches lookup table and links records
5. **populate_customer_timeline_fields.py**: Populates first_lead_date and conversion_date
6. **link_orphaned_performance_records.py**: Links orphaned UserPerformance and SalesPerformance records
7. **merge_sales_person_variations.py**: Merges sales person name variations
