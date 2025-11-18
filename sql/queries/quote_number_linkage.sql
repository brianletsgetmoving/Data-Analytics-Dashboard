-- Quote Number Linkage Analysis
-- Analyzes quote_number matches between LeadStatus, LostLead, and BookedOpportunity
-- This helps understand the relationship between these modules via quote_number

with lead_status_quotes as (
    -- All quote numbers from lead_status (central hub)
    select
        ls.quote_number,
        ls.id as lead_status_id,
        ls.status,
        ls.sales_person,
        ls.branch_name,
        ls.referral_source,
        ls.time_to_contact,
        'lead_status' as source_table
    from
        lead_status ls
),
booked_opportunity_quotes as (
    -- All quote numbers from booked_opportunities
    select
        bo.quote_number,
        bo.id as booked_opportunity_id,
        bo.status,
        bo.sales_person,
        bo.branch_name,
        bo.referral_source,
        bo.customer_id,
        bo.booked_date,
        'booked_opportunity' as source_table
    from
        booked_opportunities bo
),
lost_lead_quotes as (
    -- All quote numbers from lost_leads
    select
        ll.quote_number,
        ll.id as lost_lead_id,
        ll.name,
        ll.lost_date,
        ll.move_date,
        ll.reason,
        ll.date_received,
        ll.time_to_first_contact,
        'lost_lead' as source_table
    from
        lost_leads ll
),
quote_number_matches as (
    -- Find matches across all three tables
    select
        coalesce(lsq.quote_number, boq.quote_number, llq.quote_number) as quote_number,
        -- Lead status information
        lsq.lead_status_id,
        lsq.status as lead_status_status,
        lsq.sales_person as lead_status_sales_person,
        lsq.branch_name as lead_status_branch_name,
        lsq.referral_source as lead_status_referral_source,
        lsq.time_to_contact,
        -- Booked opportunity information
        boq.booked_opportunity_id,
        boq.status as booked_opportunity_status,
        boq.sales_person as booked_opportunity_sales_person,
        boq.branch_name as booked_opportunity_branch_name,
        boq.referral_source as booked_opportunity_referral_source,
        boq.customer_id,
        boq.booked_date,
        -- Lost lead information
        llq.lost_lead_id,
        llq.name as lost_lead_name,
        llq.lost_date,
        llq.move_date,
        llq.reason as lost_reason,
        llq.date_received,
        llq.time_to_first_contact,
        -- Match analysis
        case
            when lsq.quote_number is not null and boq.quote_number is not null and llq.quote_number is not null
            then 'All Three'
            when lsq.quote_number is not null and boq.quote_number is not null
            then 'LeadStatus + BookedOpportunity'
            when lsq.quote_number is not null and llq.quote_number is not null
            then 'LeadStatus + LostLead'
            when boq.quote_number is not null and llq.quote_number is not null
            then 'BookedOpportunity + LostLead'
            when lsq.quote_number is not null
            then 'LeadStatus Only'
            when boq.quote_number is not null
            then 'BookedOpportunity Only'
            when llq.quote_number is not null
            then 'LostLead Only'
        end as match_type
    from
        lead_status_quotes lsq
    full outer join
        booked_opportunity_quotes boq on lsq.quote_number = boq.quote_number
    full outer join
        lost_lead_quotes llq on coalesce(lsq.quote_number, boq.quote_number) = llq.quote_number
)
select
    quote_number,
    match_type,
    -- Lead status fields
    lead_status_id,
    lead_status_status,
    lead_status_sales_person,
    lead_status_branch_name,
    lead_status_referral_source,
    time_to_contact,
    -- Booked opportunity fields
    booked_opportunity_id,
    booked_opportunity_status,
    booked_opportunity_sales_person,
    booked_opportunity_branch_name,
    booked_opportunity_referral_source,
    customer_id,
    booked_date,
    -- Lost lead fields
    lost_lead_id,
    lost_lead_name,
    lost_date,
    move_date,
    lost_reason,
    date_received,
    time_to_first_contact,
    -- Journey analysis
    case
        when booked_opportunity_id is not null and customer_id is not null then 'Converted to Customer'
        when lost_lead_id is not null then 'Lost Lead'
        when lead_status_id is not null and booked_opportunity_id is null and lost_lead_id is null then 'Active Lead'
        else 'Unknown Status'
    end as journey_status
from
    quote_number_matches
order by
    match_type,
    booked_date desc nulls last,
    lost_date desc nulls last,
    quote_number;

