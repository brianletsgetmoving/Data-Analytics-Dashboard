-- Module Relationship Matrix
-- Matrix showing all possible relationships between modules
-- Provides a comprehensive view of how data flows between different modules

with customer_to_jobs as (
    -- Customers linked to jobs (booked/closed only - customers, not leads)
    select
        'Customer → Jobs' as relationship,
        count(distinct c.id) as source_count,
        count(distinct j.id) as target_count,
        count(distinct j.customer_id) as linked_count
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
),
customer_to_bad_leads as (
    -- Customers linked to bad leads
    select
        'Customer → Bad Leads' as relationship,
        count(distinct c.id) as source_count,
        count(distinct bl.id) as target_count,
        count(distinct bl.customer_id) as linked_count
    from
        customers c
    left join
        bad_leads bl on c.id = bl.customer_id
),
customer_to_booked_opportunities as (
    -- Customers linked to booked opportunities
    select
        'Customer → Booked Opportunities' as relationship,
        count(distinct c.id) as source_count,
        count(distinct bo.id) as target_count,
        count(distinct bo.customer_id) as linked_count
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
),
lead_status_to_booked_opportunities as (
    -- LeadStatus linked to BookedOpportunities via quote_number
    select
        'LeadStatus → BookedOpportunities' as relationship,
        count(distinct ls.id) as source_count,
        count(distinct bo.id) as target_count,
        count(distinct ls.quote_number) filter (where bo.quote_number is not null) as linked_count
    from
        lead_status ls
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
),
lead_status_to_lost_leads as (
    -- LeadStatus linked to LostLeads via quote_number
    select
        'LeadStatus → Lost Leads' as relationship,
        count(distinct ls.id) as source_count,
        count(distinct ll.id) as target_count,
        count(distinct ls.quote_number) filter (where ll.quote_number is not null) as linked_count
    from
        lead_status ls
    left join
        lost_leads ll on ls.quote_number = ll.quote_number
),
lost_leads_to_booked_opportunities as (
    -- LostLeads linked to BookedOpportunities via quote_number
    select
        'Lost Leads → BookedOpportunities' as relationship,
        count(distinct ll.id) as source_count,
        count(distinct bo.id) as target_count,
        count(distinct ll.quote_number) filter (where bo.quote_number is not null) as linked_count
    from
        lost_leads ll
    left join
        booked_opportunities bo on ll.quote_number = bo.quote_number
),
booked_opportunities_to_customers as (
    -- BookedOpportunities linked to Customers
    select
        'BookedOpportunities → Customers' as relationship,
        count(distinct bo.id) as source_count,
        count(distinct c.id) as target_count,
        count(distinct bo.customer_id) as linked_count
    from
        booked_opportunities bo
    left join
        customers c on bo.customer_id = c.id
),
lead_status_to_customers_indirect as (
    -- LeadStatus linked to Customers indirectly via BookedOpportunities
    select
        'LeadStatus → Customers (via BookedOpportunities)' as relationship,
        count(distinct ls.id) as source_count,
        count(distinct c.id) as target_count,
        count(distinct ls.quote_number) filter (where c.id is not null) as linked_count
    from
        lead_status ls
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    left join
        customers c on bo.customer_id = c.id
),
bad_leads_to_customers as (
    -- BadLeads linked to Customers
    select
        'Bad Leads → Customers' as relationship,
        count(distinct bl.id) as source_count,
        count(distinct c.id) as target_count,
        count(distinct bl.customer_id) as linked_count
    from
        bad_leads bl
    left join
        customers c on bl.customer_id = c.id
),
all_relationships as (
    select * from customer_to_jobs
    union all
    select * from customer_to_bad_leads
    union all
    select * from customer_to_booked_opportunities
    union all
    select * from lead_status_to_booked_opportunities
    union all
    select * from lead_status_to_lost_leads
    union all
    select * from lost_leads_to_booked_opportunities
    union all
    select * from booked_opportunities_to_customers
    union all
    select * from lead_status_to_customers_indirect
    union all
    select * from bad_leads_to_customers
)
select
    relationship,
    source_count,
    target_count,
    linked_count,
    case
        when source_count > 0
        then round(linked_count::numeric / source_count * 100, 2)
        else 0
    end as linkage_percentage,
    case
        when linked_count > 0 then 'Linked'
        else 'Not Linked'
    end as relationship_status
from
    all_relationships
order by
    relationship;

