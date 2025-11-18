-- Lost Lead to Customer Linkage
-- Links LostLead to Customers via BookedOpportunity using quote_number
-- Shows if lost leads eventually converted to customers

with lost_leads_with_bookings as (
    -- Link lost_leads to booked_opportunities via quote_number
    select
        ll.id as lost_lead_id,
        ll.quote_number,
        ll.name as lost_lead_name,
        ll.lost_date,
        ll.move_date,
        ll.reason,
        ll.date_received,
        ll.time_to_first_contact,
        bo.id as booked_opportunity_id,
        bo.status as booked_opportunity_status,
        bo.customer_id,
        bo.booked_date,
        bo.sales_person,
        bo.branch_name,
        bo.referral_source
    from
        lost_leads ll
    left join
        booked_opportunities bo on ll.quote_number = bo.quote_number
),
lost_leads_with_lead_status as (
    -- Also link to lead_status for complete picture
    select
        llwb.*,
        ls.id as lead_status_id,
        ls.status as lead_status_status,
        ls.sales_person as lead_status_sales_person,
        ls.branch_name as lead_status_branch_name,
        ls.time_to_contact
    from
        lost_leads_with_bookings llwb
    left join
        lead_status ls on llwb.quote_number = ls.quote_number
),
customer_job_summary as (
    -- Get customer job information for those who converted
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(j.id) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as total_customer_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (
            where j.opportunity_status in ('BOOKED', 'CLOSED')
        ) as total_customer_revenue,
        min(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as first_customer_job_date,
        max(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as last_customer_job_date
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
    group by
        c.id, c.name, c.email, c.phone
)
select
    llwls.lost_lead_id,
    llwls.quote_number,
    llwls.lost_lead_name,
    llwls.lost_date,
    llwls.move_date,
    llwls.reason,
    llwls.date_received,
    llwls.time_to_first_contact,
    -- Lead status information
    llwls.lead_status_id,
    llwls.lead_status_status,
    llwls.lead_status_sales_person,
    llwls.lead_status_branch_name,
    llwls.time_to_contact,
    -- Booked opportunity information
    llwls.booked_opportunity_id,
    llwls.booked_opportunity_status,
    llwls.booked_date,
    llwls.sales_person as booked_opportunity_sales_person,
    llwls.branch_name as booked_opportunity_branch_name,
    llwls.referral_source as booked_opportunity_referral_source,
    -- Customer information
    llwls.customer_id,
    cjs.customer_name,
    cjs.email,
    cjs.phone,
    cjs.total_customer_jobs,
    cjs.total_customer_revenue,
    cjs.first_customer_job_date,
    cjs.last_customer_job_date,
    -- Conversion analysis
    case
        when cjs.total_customer_jobs > 0 then 'Lost Lead → Converted to Customer'
        when llwls.customer_id is not null then 'Lost Lead → Booked (Not Yet Customer)'
        when llwls.booked_opportunity_id is not null then 'Lost Lead → Booked Opportunity'
        else 'Lost Lead (No Conversion)'
    end as conversion_status,
    -- Time analysis
    case
        when llwls.lost_date is not null
        and llwls.date_received is not null
        then llwls.lost_date - llwls.date_received::date
        else null
    end as days_to_lost,
    case
        when cjs.first_customer_job_date is not null
        and llwls.lost_date is not null
        then cjs.first_customer_job_date - llwls.lost_date::timestamp
        else null
    end as days_from_lost_to_customer
from
    lost_leads_with_lead_status llwls
left join
    customer_job_summary cjs on llwls.customer_id = cjs.customer_id
order by
    total_customer_revenue desc nulls last,
    lost_date desc nulls last,
    quote_number;

