# Database Relationships Documentation

## Overview

This document describes all relationships between database models as defined in the Prisma schema. The relationships are organized by model and include both direct foreign key relationships and indirect relationships via lookup tables.

### Core Business Logic

**Customers are the central piece** of how we understand the entire database:
- All contact details are connected to customers
- All customers come from a larger pool of leads
- Jobs are connected to customers
- Leads are connected to customers

**Lead Flow**:
- **LeadStatus** is the central pool of all leads (BadLeads and LostLeads are compiled into this pool)
- All customers originate from this lead pool
- **BookedOpportunities** come from customers
- **BookedOpportunities flow into Jobs**

**Performance Tracking**:
- **SalesPerson** and **Branch** come from Jobs and BookedOpportunities
- **Branch** and **SalesPerson** flow into **UserPerformance** and **SalesPerformance**

**LeadSource**:
- Compiled lookup table from all sources: Jobs, BookedOpportunities, LeadStatus, BadLeads, and LostLeads

## Entity Relationship Diagrams

This section provides multiple views of the database relationships to support different understanding needs.

### 1. Overview Diagram (Customer-Centric View)

High-level view showing the central role of **Customer** and the main data flow:

```
┌─────────────────────────────────────────────────────────────────┐
│                        LEAD POOL                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ LeadStatus   │  │  BadLead     │  │  LostLead    │         │
│  │ (1)          │  │  (N)         │  │  (N)         │         │
│  │              │  │              │  │              │         │
│  │ All leads    │◄─┤ Linked to    │  │ Linked via   │         │
│  │ in pool      │  │ LeadStatus   │  │ quote_number │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                            │ All customers originate from leads │
│                            ▼                                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │
                    ┌───────▼────────┐
                    │   CUSTOMER     │ ◄─── CENTRAL HUB
                    │   (1)          │      All contact details
                    │                │      All relationships
                    │ - Contact info │      All understanding
                    │ - Timeline     │      flows through here
                    └───┬──────┬─────┘
                        │      │
        ┌───────────────┼──────┼───────────────┐
        │               │      │               │
        ▼               ▼      ▼               ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│BookedOpp     │ │   Job    │ │  BadLead     │
│(N)           │ │  (N)     │ │  (N)         │
│              │ │          │ │              │
│Flows to Jobs │ │BOOKED/   │ │Part of lead  │
│              │ │CLOSED    │ │pool          │
└──────┬───────┘ └────┬─────┘ └──────────────┘
       │              │
       └──────┬───────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌──────────┐      ┌──────────┐
│SalesPerson│      │  Branch  │
│(Lookup)  │      │ (Lookup) │
│          │      │          │
│From Jobs │      │From Jobs │
│& Booked  │      │& Booked   │
└────┬─────┘      └────┬─────┘
     │                 │
     └────────┬────────┘
              │
     ┌────────┴────────┐
     │                 │
     ▼                 ▼
┌──────────┐    ┌──────────────┐
│UserPerf  │    │SalesPerf     │
│(N)       │    │(N)           │
└──────────┘    └──────────────┘

┌─────────────────────────────────────┐
│         LeadSource (Lookup)         │
│         Compiled from ALL:          │
│         - Jobs, BookedOpps          │
│         - LeadStatus, BadLeads      │
│         - LostLeads                 │
└─────────────────────────────────────┘
```

**Legend:**
- `(1)` = One entity
- `(N)` = Many entities
- Solid lines = Direct foreign key relationships
- Dashed lines = Indirect relationships (quote_number matching)

### 2. Detailed Relationship Diagram

Complete view with all 11 models, explicit cardinalities, and relationship types:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORE ENTITIES                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐                    ┌──────────────┐
│ LeadStatus   │                    │  BadLead     │
│ (1)          │◄───────────────────┤ (N)          │
│              │ 1:N (lead_status_id)│              │
│ quote_number │                    │ customer_id  │
│              │                    │ lead_status_id│
└──────┬───────┘                    │ lead_source_id│
       │                            └──────┬───────┘
       │ 1:N (booked_opportunity_id)       │
       │ (via quote_number)                │ N:1 (customer_id)
       │                                    │
       ▼                                    │
┌──────────────┐                           │
│BookedOpp     │                           │
│ (1)          │                           │
│ quote_number │                           │
│ customer_id  │                           │
│ sales_person_id│                          │
│ branch_id    │                           │
└──────┬───────┘                           │
       │                                   │
       │ N:1 (customer_id)                │
       │                                   │
       │                                   │
       │                                   │
       ▼                                   ▼
┌──────────────────────────────────────────────────┐
│              CUSTOMER (1)                         │
│              ◄─── CENTRAL HUB                     │
│              - Contact details                    │
│              - Timeline tracking                  │
│              - Merge history                      │
└──────┬──────────────┬──────────────┬──────────────┘
       │              │              │
       │ 1:N          │ 1:N          │ 1:N
       │              │              │
       ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Job (N)     │ │BookedOpp (N) │ │ BadLead (N)  │
│               │ │              │ │              │
│ customer_id   │ │ customer_id  │ │ customer_id  │
│ sales_person_id│ │ sales_person_id│              │
│ branch_id     │ │ branch_id    │ │              │
└──────┬───────┘ └──────┬───────┘ └──────────────┘
       │                │
       │                │ 1:N (via quote_number)
       │                │
       │                ▼
       │        ┌──────────────┐
       │        │  LostLead    │
       │        │  (N)        │
       │        │  quote_number│
       │        │  booked_opportunity_id│
       │        │  lead_source_id│
       │        └──────────────┘
       │
       │ N:1 (sales_person_id)
       │ N:1 (branch_id)
       │
       ▼                ▼
┌──────────────┐ ┌──────────────┐
│SalesPerson   │ │   Branch     │
│ (1)          │ │  (1)         │
│              │ │              │
│ normalizedName│ │ normalizedName│
└──────┬───────┘ └──────┬───────┘
       │                │
       │ 1:N            │ 1:N
       │                │
       ▼                │
┌──────────────┐       │
│UserPerf (N)   │       │
│               │       │
│ sales_person_id│       │
└──────────────┘       │
                       │
                       │
┌──────────────┐       │
│SalesPerf (N) │       │
│              │       │
│ sales_person_id│      │
└──────────────┘       │

┌─────────────────────────────────────┐
│      LeadSource (1)                │
│      - Normalized lead sources     │
│      - Category classification     │
│                                    │
│  1:N relationships to:             │
│  - LeadStatus (lead_source_id)     │
│  - BadLead (lead_source_id)        │
│  - LostLead (lead_source_id)       │
└─────────────────────────────────────┘
```

**Relationship Types:**
- **Solid lines** = Direct foreign key relationships (FK constraints)
- **Dashed lines** = Indirect relationships (quote_number matching, derived relationships)
- **Cardinality notation**: `1:N` = One-to-Many, `N:1` = Many-to-One

### 3. Customer Journey Flow Diagram

Focused view of the complete customer journey from lead to job completion:

```
                    ┌─────────────────────┐
                    │   LeadStatus        │
                    │   (Lead Pool)       │
                    │                     │
                    │ - quote_number      │
                    │ - lead_source_id    │
                    │ - sales_person_id   │
                    │ - branch_id        │
                    └──────────┬──────────┘
                               │
                               │ [1] Lead enters system
                               │
                               ▼
                    ┌─────────────────────┐
                    │   BadLead           │
                    │   (Optional)        │
                    │                     │
                    │ - lead_status_id   │
                    │ - customer_id      │
                    │ - lead_source_id   │
                    └──────────┬──────────┘
                               │
                               │ [2] May link to customer
                               │
                               ▼
                    ┌─────────────────────┐
                    │   CUSTOMER           │
                    │   (Central Hub)       │
                    │                     │
                    │ - first_lead_date    │
                    │ - conversion_date   │
                    │ - merge_history     │
                    └──────────┬──────────┘
                               │
                               │ [3] Customer created
                               │
                               ▼
                    ┌─────────────────────┐
                    │ BookedOpportunity   │
                    │                     │
                    │ - quote_number      │
                    │ - customer_id      │
                    │ - booked_date      │
                    └──────────┬──────────┘
                               │
                               │ [4] Opportunity booked
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
        ┌──────────────────┐   ┌──────────────────┐
        │   Job (BOOKED)    │   │   LostLead       │
        │                   │   │   (Opportunity   │
        │ - customer_id    │   │    lost)         │
        │ - job_date       │   │                  │
        │ - opportunity_status│ │ - quote_number   │
        └──────────┬───────┘   │ - booked_opportunity_id│
                   │           └──────────────────┘
                   │
                   │ [5] Job completed
                   │
                   ▼
        ┌──────────────────┐
        │   Job (CLOSED)    │
        │                   │
        │ - total_actual_cost│
        │ - job_date       │
        └──────────────────┘

Journey Steps:
[1] Lead enters system via LeadStatus
[2] BadLead may be linked (if lead is marked bad)
[3] Customer record created (unified contact details)
[4] BookedOpportunity created when opportunity is booked
[5] Job created when work is completed (BOOKED → CLOSED)
```

### 4. Lookup Table Relationships

How lookup tables connect across the system:

```
┌─────────────────────────────────────────────────────────────┐
│                    SALESPERSON (Lookup)                    │
│                    - Normalizes sales person names         │
│                    - Used for matching across modules       │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         │ 1:N          │ 1:N          │ 1:N          │ 1:N
         │              │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  Job    │    │ Booked  │    │ Lead    │    │ User    │
    │         │    │ Opp     │    │ Status  │    │ Perf    │
    │ sales_  │    │ sales_  │    │ sales_  │    │ sales_  │
    │ person_ │    │ person_ │    │ person_ │    │ person_ │
    │ id      │    │ id      │    │ id      │    │ id      │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                      │
                                                      │
                                              ┌───────▼───────┐
                                              │ SalesPerf     │
                                              │ sales_person_ │
                                              │ id            │
                                              └───────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BRANCH (Lookup)                          │
│                    - Normalizes branch names                │
│                    - Geographic organization                 │
└─────────────────────────────────────────────────────────────┘
         │              │              │
         │ 1:N          │ 1:N          │ 1:N
         │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  Job    │    │ Booked  │    │ Lead    │
    │         │    │ Opp     │    │ Status  │
    │ branch_ │    │ branch_ │    │ branch_ │
    │ id      │    │ id      │    │ id      │
    └─────────┘    └─────────┘    └─────────┘

┌─────────────────────────────────────────────────────────────┐
│                    LEADSOURCE (Lookup)                      │
│                    - Compiled from ALL sources              │
│                    - Unified lead origin tracking            │
└─────────────────────────────────────────────────────────────┘
         │              │              │
         │ 1:N          │ 1:N          │ 1:N
         │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Lead    │    │ BadLead │    │ LostLead│
    │ Status  │    │         │    │         │
    │ lead_   │    │ lead_   │    │ lead_   │
    │ source_ │    │ source_ │    │ source_ │
    │ id      │    │ id      │    │ id      │
    └─────────┘    └─────────┘    └─────────┘
```

### 5. Relationship Matrix

Comprehensive table of all relationships with cardinalities, foreign keys, and purposes:

| Source Entity | Target Entity | Cardinality | Foreign Key Field | Constraint | Link Method | Purpose |
|--------------|--------------|-------------|-------------------|------------|-------------|---------|
| **Customer** | Job | 1:N | `jobs.customer_id` | SetNull | Direct FK | Links jobs to customers (BOOKED/CLOSED only) |
| **Customer** | BadLead | 1:N | `bad_leads.customer_id` | SetNull | Direct FK | Links bad leads to customers |
| **Customer** | BookedOpportunity | 1:N | `booked_opportunities.customer_id` | SetNull | Direct FK | Links booked opportunities to customers |
| **Job** | Customer | N:1 | `jobs.customer_id` | SetNull | Direct FK | Jobs belong to customers |
| **Job** | SalesPerson | N:1 | `jobs.sales_person_id` | SetNull | Direct FK | Normalizes sales person from jobs |
| **Job** | Branch | N:1 | `jobs.branch_id` | SetNull | Direct FK | Normalizes branch from jobs |
| **BadLead** | Customer | N:1 | `bad_leads.customer_id` | SetNull | Direct FK | Bad leads may link to customers |
| **BadLead** | LeadStatus | N:1 | `bad_leads.lead_status_id` | SetNull | Direct FK | Links bad leads to lead pool |
| **BadLead** | LeadSource | N:1 | `bad_leads.lead_source_id` | SetNull | Direct FK | Tracks lead source for bad leads |
| **BookedOpportunity** | Customer | N:1 | `booked_opportunities.customer_id` | SetNull | Direct FK | Opportunities belong to customers |
| **BookedOpportunity** | SalesPerson | N:1 | `booked_opportunities.sales_person_id` | SetNull | Direct FK | Normalizes sales person from opportunities |
| **BookedOpportunity** | Branch | N:1 | `booked_opportunities.branch_id` | SetNull | Direct FK | Normalizes branch from opportunities |
| **BookedOpportunity** | LeadStatus | 1:N | `lead_status.booked_opportunity_id` | SetNull | quote_number | Links leads to opportunities |
| **BookedOpportunity** | LostLead | 1:N | `lost_leads.booked_opportunity_id` | SetNull | quote_number | Links lost leads to opportunities |
| **LeadStatus** | BookedOpportunity | N:1 | `lead_status.booked_opportunity_id` | SetNull | quote_number | Leads may convert to opportunities |
| **LeadStatus** | SalesPerson | N:1 | `lead_status.sales_person_id` | SetNull | Direct FK | Sales person from lead tracking |
| **LeadStatus** | LeadSource | N:1 | `lead_status.lead_source_id` | SetNull | Direct FK | Lead source from lead pool |
| **LeadStatus** | Branch | N:1 | `lead_status.branch_id` | SetNull | Direct FK | Branch from lead tracking |
| **LeadStatus** | BadLead | 1:N | `bad_leads.lead_status_id` | SetNull | Direct FK | Bad leads are part of lead pool |
| **LostLead** | BookedOpportunity | N:1 | `lost_leads.booked_opportunity_id` | SetNull | quote_number | Lost leads link to opportunities |
| **LostLead** | LeadSource | N:1 | `lost_leads.lead_source_id` | SetNull | Direct FK | Tracks lead source for lost leads |
| **UserPerformance** | SalesPerson | N:1 | `user_performance.sales_person_id` | SetNull | Direct FK | Performance metrics for sales person |
| **SalesPerformance** | SalesPerson | N:1 | `sales_performance.sales_person_id` | SetNull | Direct FK | Sales metrics for sales person |
| **SalesPerson** | Job | 1:N | `jobs.sales_person_id` | SetNull | Direct FK | Sales person has many jobs |
| **SalesPerson** | BookedOpportunity | 1:N | `booked_opportunities.sales_person_id` | SetNull | Direct FK | Sales person has many opportunities |
| **SalesPerson** | LeadStatus | 1:N | `lead_status.sales_person_id` | SetNull | Direct FK | Sales person has many leads |
| **SalesPerson** | UserPerformance | 1:N | `user_performance.sales_person_id` | SetNull | Direct FK | Sales person has performance metrics |
| **SalesPerson** | SalesPerformance | 1:N | `sales_performance.sales_person_id` | SetNull | Direct FK | Sales person has sales metrics |
| **LeadSource** | LeadStatus | 1:N | `lead_status.lead_source_id` | SetNull | Direct FK | Lead source has many leads |
| **LeadSource** | BadLead | 1:N | `bad_leads.lead_source_id` | SetNull | Direct FK | Lead source has many bad leads |
| **LeadSource** | LostLead | 1:N | `lost_leads.lead_source_id` | SetNull | Direct FK | Lead source has many lost leads |
| **Branch** | Job | 1:N | `jobs.branch_id` | SetNull | Direct FK | Branch has many jobs |
| **Branch** | BookedOpportunity | 1:N | `booked_opportunities.branch_id` | SetNull | Direct FK | Branch has many opportunities |
| **Branch** | LeadStatus | 1:N | `lead_status.branch_id` | SetNull | Direct FK | Branch has many leads |

**Notes:**
- **Direct FK**: Relationship uses foreign key constraint in database
- **quote_number**: Relationship established via matching unique `quote_number` fields (used in scripts)
- **SetNull**: On delete, foreign key is set to NULL (no cascade delete)

## Enhanced Business Logic Flow

### Step-by-Step Customer Journey

The database tracks the complete customer journey from initial lead to completed job. Here's the detailed flow:

#### Stage 1: Lead Entry (Lead Pool)
1. **Lead enters system** → `LeadStatus` record created
   - Contains: `quote_number`, `lead_source_id`, `sales_person_id`, `branch_id`
   - Represents: Initial contact or inquiry
   - Status: Active lead in the pool

2. **Lead may be marked as bad** → `BadLead` record created (optional)
   - Links to: `LeadStatus` via `lead_status_id`
   - Contains: Reason for being marked bad
   - May link to: `Customer` if customer record exists

3. **Lead may be lost** → `LostLead` record created (optional, after opportunity)
   - Links to: `BookedOpportunity` via `quote_number` matching
   - Contains: Reason for loss, lost date
   - Represents: Opportunity that didn't convert to job

#### Stage 2: Customer Creation (Central Hub)
4. **Customer record created** → `Customer` record
   - Triggered by: First contact, booking, or job creation
   - Contains: Unified contact details (name, email, phone)
   - Timeline fields: `first_lead_date`, `conversion_date`
   - Purpose: Single source of truth for all customer information

#### Stage 3: Opportunity Booking
5. **Opportunity booked** → `BookedOpportunity` record created
   - Links to: `Customer` via `customer_id`
   - Links to: `LeadStatus` via `quote_number` matching
   - Contains: Booking details, estimated amount, service date
   - Status: Opportunity is booked but not yet completed

#### Stage 4: Job Completion
6. **Job created** → `Job` record created
   - Links to: `Customer` via `customer_id`
   - Status: `BOOKED` (work scheduled) or `CLOSED` (work completed)
   - Contains: Actual costs, crew/truck counts, job dates
   - Note: Only BOOKED/CLOSED jobs should have `customer_id` set

#### Stage 5: Performance Tracking
7. **Lookup tables populated** → `SalesPerson`, `Branch`, `LeadSource`
   - Extracted from: Jobs, BookedOpportunities, LeadStatus
   - Purpose: Normalize names for consistent tracking
   - Used for: Performance metrics and analytics

8. **Performance metrics created** → `UserPerformance`, `SalesPerformance`
   - Links to: `SalesPerson` via `sales_person_id`
   - Contains: Call metrics, sales metrics, performance data
   - Purpose: Track individual and team performance

### Data Flow Summary

```
LeadStatus (Lead Pool)
    │
    ├─→ BadLead (optional, if lead is bad)
    │       │
    │       └─→ Customer (if customer exists)
    │
    ├─→ Customer (all customers originate from leads)
    │       │
    │       ├─→ BookedOpportunity
    │       │       │
    │       │       ├─→ Job (BOOKED/CLOSED)
    │       │       │       │
    │       │       │       ├─→ SalesPerson (lookup)
    │       │       │       │       └─→ UserPerformance
    │       │       │       │       └─→ SalesPerformance
    │       │       │       │
    │       │       │       └─→ Branch (lookup)
    │       │       │
    │       │       └─→ LostLead (if opportunity lost)
    │       │
    │       └─→ BadLead (if linked to customer)
    │
    └─→ LeadSource (lookup, tracks all lead origins)
```

### Key Principles

1. **Customer-Centric Design**: All business understanding flows through the `Customer` model
   - All contact details are unified in `Customer`
   - All relationships (jobs, opportunities, leads) link to `Customer`
   - Timeline tracking (`first_lead_date`, `conversion_date`) provides complete journey view

2. **Lead Pool Concept**: `LeadStatus` is the central pool of all leads
   - `BadLead` and `LostLead` are part of this pool (linked to `LeadStatus`)
   - All customers originate from this lead pool
   - Provides complete lead tracking and conversion analysis

3. **Quote Number Linking**: Enables cross-table relationships
   - `BookedOpportunity`, `LeadStatus`, and `LostLead` all have unique `quote_number`
   - Used for linking records that may not have direct FK relationships
   - Tracks the journey: Lead → Opportunity → Job or Loss

4. **Lookup Table Normalization**: Ensures consistent data across modules
   - `SalesPerson`: Normalizes sales person names from Jobs, BookedOpportunities, LeadStatus
   - `Branch`: Normalizes branch names from Jobs, BookedOpportunities, LeadStatus
   - `LeadSource`: Compiled from ALL sources (Jobs, BookedOpportunities, LeadStatus, BadLeads, LostLeads)

5. **Performance Tracking**: Flows from operational data to metrics
   - Jobs and BookedOpportunities → SalesPerson/Branch → Performance metrics
   - Enables cross-module analysis and performance benchmarking

## Direct Relationships

### Customer Model

**Customer** is the central unified model - all business understanding flows through customers. All customers originate from the lead pool (LeadStatus).

**Key Principle**: All contact details, relationships, and business understanding are connected to customers.

1. **Customer → Jobs** (One-to-Many)
   - **Field**: `jobs.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Purpose**: Links jobs to customers. Only BOOKED and CLOSED jobs should typically be linked to customers.
   - **Business Logic**: Jobs represent completed work for customers (not leads).

2. **Customer → BadLeads** (One-to-Many)
   - **Field**: `bad_leads.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Purpose**: Links bad lead records to customers when they're identified as the same person (via email/phone matching).
   - **Business Logic**: BadLeads are part of the lead pool (LeadStatus). When a bad lead is matched to a customer (same email/phone), we link them to track the complete journey: Bad Lead → Customer. This allows analysis of customers who had bad leads before converting, or tracking multiple bad lead records for the same person.
   - **Important Note**: This is a **matching/linking relationship**, not a creation relationship. BadLeads originate from the lead pool (LeadStatus), not from customers. The relationship exists for historical tracking and journey analysis - it shows that a person who became a customer had bad lead records earlier in their journey.

3. **Customer → BookedOpportunities** (One-to-Many)
   - **Field**: `booked_opportunities.customer_id` → `customers.id`
   - **Constraint**: `onDelete: SetNull`
   - **Purpose**: Links booked opportunities to customers. Booked opportunities flow into jobs.
   - **Business Logic**: BookedOpportunities → Jobs (the conversion path from opportunity to completed work).

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
   - **Business Logic**: BadLeads are matched to Customers via email/phone matching. This link tracks the journey from bad lead to customer conversion. A person may have multiple bad lead records that all link to the same customer record when they convert.

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

### LeadStatus Model (Central Lead Pool)

**LeadStatus is the central pool of all leads**. BadLeads and LostLeads are compiled into this pool. All customers originate from this lead pool.

15. **LeadStatus → BookedOpportunity** (Many-to-One)
    - **Field**: `lead_status.booked_opportunity_id` → `booked_opportunities.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([bookedOpportunityId])`
    - **Link Method**: Via `quote_number` matching
    - **Business Logic**: Leads in LeadStatus may convert to BookedOpportunities, which then flow to Jobs

16. **LeadStatus → SalesPerson** (Many-to-One)
    - **Field**: `lead_status.sales_person_id` → `sales_persons.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([salesPersonId])`
    - **Business Logic**: Sales person from lead tracking (before conversion to customer)

17. **LeadStatus → LeadSource** (Many-to-One)
    - **Field**: `lead_status.lead_source_id` → `lead_sources.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([leadSourceId])`, `@@index([leadSourceId, createdAt])`
    - **Business Logic**: Lead source tracking for all leads in the pool

18. **LeadStatus → Branch** (Many-to-One)
    - **Field**: `lead_status.branch_id` → `branches.id`
    - **Constraint**: `onDelete: SetNull`
    - **Index**: `@@index([branchId])`
    - **Business Logic**: Branch from lead tracking (before conversion to customer)

19. **LeadStatus → BadLead** (One-to-Many)
    - **Field**: `bad_leads.lead_status_id` → `lead_status.id`
    - **Purpose**: Links bad leads to lead status records.
    - **Business Logic**: BadLeads are part of the lead pool (LeadStatus) - they represent leads that didn't convert

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

**SalesPerson comes from Jobs and BookedOpportunities**, then flows into performance metrics.

24. **SalesPerson → Jobs** (One-to-Many)
    - **Field**: `jobs.sales_person_id` → `sales_persons.id`
    - **Purpose**: Normalizes sales person names from jobs.
    - **Business Logic**: Sales person is extracted from jobs (where actual work happens)

25. **SalesPerson → BookedOpportunities** (One-to-Many)
    - **Field**: `booked_opportunities.sales_person_id` → `sales_persons.id`
    - **Business Logic**: Sales person is also tracked in booked opportunities (before conversion to jobs)

26. **SalesPerson → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.sales_person_id` → `sales_persons.id`
    - **Business Logic**: Sales person from lead tracking (earliest stage)

27. **SalesPerson → UserPerformance** (One-to-Many)
    - **Field**: `user_performance.sales_person_id` → `sales_persons.id`
    - **Business Logic**: Sales person flows into user performance metrics

28. **SalesPerson → SalesPerformance** (One-to-Many)
    - **Field**: `sales_performance.sales_person_id` → `sales_persons.id`
    - **Business Logic**: Sales person flows into sales performance metrics

### LeadSource Model (Lookup Table)

**LeadSource is compiled from ALL sources**: Jobs, BookedOpportunities, LeadStatus, BadLeads, and LostLeads. It provides a unified view of where leads originate across the entire system.

29. **LeadSource → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.lead_source_id` → `lead_sources.id`
    - **Purpose**: Normalizes and categorizes lead sources from the lead pool.

30. **LeadSource → BadLeads** (One-to-Many)
    - **Field**: `bad_leads.lead_source_id` → `lead_sources.id`
    - **Business Logic**: Lead source for bad leads (part of the lead pool)

31. **LeadSource → LostLeads** (One-to-Many)
    - **Field**: `lost_leads.lead_source_id` → `lead_sources.id`
    - **Business Logic**: Lead source for lost leads (part of the lead pool)

**Note**: LeadSource can also be derived from Jobs and BookedOpportunities through their referral_source fields, providing a complete picture of lead origins across all stages of the customer journey.

### Branch Model (Lookup Table)

**Branch comes from Jobs and BookedOpportunities**, then flows into performance metrics.

32. **Branch → Jobs** (One-to-Many)
    - **Field**: `jobs.branch_id` → `branches.id`
    - **Purpose**: Normalizes branch names from jobs.
    - **Business Logic**: Branch is extracted from jobs (where actual work happens)

33. **Branch → BookedOpportunities** (One-to-Many)
    - **Field**: `booked_opportunities.branch_id` → `branches.id`
    - **Business Logic**: Branch is also tracked in booked opportunities (before conversion to jobs)

34. **Branch → LeadStatus** (One-to-Many)
    - **Field**: `lead_status.branch_id` → `branches.id`
    - **Business Logic**: Branch from lead tracking (earliest stage)

## Indirect Relationships

### Lead Pool Composition

**LeadStatus is the central pool** that compiles all leads:
- **LeadStatus** contains all active leads
- **BadLeads** are linked to LeadStatus (via `lead_status_id`) - they're part of the pool but marked as bad
- **LostLeads** are linked to LeadStatus (via BookedOpportunity → LeadStatus) - they're part of the pool but marked as lost

**All customers originate from this lead pool** - there are no customers that didn't start as leads.

**BadLead → Customer Matching**:
- BadLeads are leads in the pool that are marked as "bad" (invalid, duplicate, etc.)
- When a bad lead is matched to a customer (via email/phone), the `customer_id` is set
- This allows tracking: a person had bad lead records, then later became a customer
- Multiple bad lead records can link to the same customer (same person, multiple bad lead entries)
- The relationship is for **historical tracking and journey analysis**, not because customers create bad leads

### Quote Number Linking

**BookedOpportunity**, **LeadStatus**, and **LostLead** all have unique `quote_number` fields that are used for cross-table linking:

- **BookedOpportunity.quoteNumber** (unique)
- **LeadStatus.quoteNumber** (unique)
- **LostLead.quoteNumber** (unique)

These tables are linked via foreign keys (`booked_opportunity_id`), but the `quote_number` field provides an alternative linking mechanism and is used in scripts for establishing relationships.

**Business Logic**: Quote numbers track the journey from lead (LeadStatus) → opportunity (BookedOpportunity) → job (Job) or loss (LostLead).

### Customer Journey Tracking

The **Customer** model includes timeline fields for tracking the customer journey:

- **firstLeadDate**: Earliest date from LeadStatus, BadLead, or LostLead (when they entered the lead pool)
- **conversionDate**: Earliest date from BookedOpportunity or Job (BOOKED/CLOSED) (when they became a customer)
- **mergeHistory**: JSONB field tracking merge operations with method, confidence, timestamp, and merged_by

**Business Logic**: This tracks the complete journey: Lead (LeadStatus) → Customer → BookedOpportunity → Job

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
- **Purpose**: Normalizes sales person names extracted from Jobs and BookedOpportunities
- **Flow**: Jobs & BookedOpportunities → SalesPerson → UserPerformance & SalesPerformance
- **Key Fields**: `name` (unique), `normalizedName` (indexed)
- **Business Logic**: Sales person information comes from where work happens (jobs) and opportunities (booked opportunities), then flows into performance metrics

### Branch
- **Purpose**: Normalizes branch names extracted from Jobs and BookedOpportunities
- **Flow**: Jobs & BookedOpportunities → Branch → Performance metrics
- **Key Fields**: `name` (unique), `normalizedName` (indexed), `city`, `state`, `isActive`
- **Business Logic**: Branch information comes from where work happens (jobs) and opportunities (booked opportunities), then flows into performance metrics

### LeadSource
- **Purpose**: Compiled lookup table from ALL sources across the entire system
- **Sources**: Jobs, BookedOpportunities, LeadStatus, BadLeads, LostLeads
- **Key Fields**: `name` (unique), `category` (indexed), `isActive` (indexed)
- **Business Logic**: Provides unified view of lead origins across all stages: from initial lead (LeadStatus) through conversion (BookedOpportunities) to completion (Jobs), including non-conversions (BadLeads, LostLeads)

## Essential Scripts

The following scripts establish and maintain relationships:

1. **complete_quote_linkage.py**: Links LeadStatus and LostLead to BookedOpportunities via quote_number
2. **link_badlead_to_leadstatus.py**: Links BadLead to LeadStatus via customer matching
3. **populate_lead_sources.py**: Creates lead_sources lookup table and links records
4. **populate_branches.py**: Creates branches lookup table and links records
5. **populate_customer_timeline_fields.py**: Populates first_lead_date and conversion_date
6. **link_orphaned_performance_records.py**: Links orphaned UserPerformance and SalesPerformance records
7. **merge_sales_person_variations.py**: Merges sales person name variations
