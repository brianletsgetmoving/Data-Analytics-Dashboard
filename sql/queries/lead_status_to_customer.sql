-- Lead Status to Customer Linkage
-- Links LeadStatus to Customers via BookedOpportunity using quote_number
-- Shows the conversion path from lead status to customer

with lead_status_with_bookings as (
    -- Link lead_status to booked_opportunities via quote_number
    select
        ls.id as lead_status_id,
        ls.quote_number,
        ls.status as lead_status,
        ls.sales_person as lead_status_sales_person,
        ls.branch_name as lead_status_branch_name,
        ls.referral_source as lead_status_referral_source,
        ls.time_to_contact,
        bo.id as booked_opportunity_id,
        bo.status as booked_opportunity_status,
        bo.customer_id,
        bo.booked_date,
        bo.sales_person as booked_opportunity_sales_person,
        bo.branch_name as booked_opportunity_branch_name,
        bo.referral_source as booked_opportunity_referral_source
    from
        lead_status ls
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
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
    lswb.lead_status_id,
    lswb.quote_number,
    lswb.lead_status,
    lswb.lead_status_sales_person,
    lswb.lead_status_branch_name,
    lswb.lead_status_referral_source,
    lswb.time_to_contact,
    -- Booked opportunity information
    lswb.booked_opportunity_id,
    lswb.booked_opportunity_status,
    lswb.booked_date,
    lswb.booked_opportunity_sales_person,
    lswb.booked_opportunity_branch_name,
    lswb.booked_opportunity_referral_source,
    -- Customer information
    lswb.customer_id,
    cjs.customer_name,
    cjs.email,
    cjs.phone,
    cjs.total_customer_jobs,
    cjs.total_customer_revenue,
    cjs.first_customer_job_date,
    cjs.last_customer_job_date,
    -- Conversion analysis
    case
        when cjs.total_customer_jobs > 0 then 'Converted to Customer'
        when lswb.customer_id is not null then 'Booked (Not Yet Customer)'
        when lswb.booked_opportunity_id is not null then 'Booked Opportunity'
        else 'Active Lead'
    end as conversion_status,
    -- Time to conversion
    case
        when cjs.first_customer_job_date is not null
        and lswb.booked_date is not null
        then cjs.first_customer_job_date - lswb.booked_date
        else null
    end as days_from_booking_to_customer
from
    lead_status_with_bookings lswb
left join
    customer_job_summary cjs on lswb.customer_id = cjs.customer_id
order by
    total_customer_revenue desc nulls last,
    booked_date desc nulls last,
    quote_number;

