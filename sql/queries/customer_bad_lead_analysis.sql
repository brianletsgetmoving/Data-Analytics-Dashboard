-- Customer Bad Lead Analysis
-- Analyzes customers who have bad leads and their job/booking history
-- Helps understand if bad leads eventually convert to customers

with customer_bad_leads as (
    -- Get all bad leads with customer information
    select
        bl.id as bad_lead_id,
        bl.provider,
        bl.customer_name,
        bl.customer_email,
        bl.customer_phone,
        bl.move_date,
        bl.date_lead_received,
        bl.lead_bad_reason,
        bl.customer_id
    from
        bad_leads bl
    where
        bl.customer_id is not null
),
customer_job_history as (
    -- Get job history for customers with bad leads
    select
        c.id as customer_id,
        count(j.id) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as total_customer_jobs,
        count(j.id) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(j.id) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
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
        c.id
),
customer_booked_opportunities as (
    -- Get booked opportunities for customers with bad leads
    select
        c.id as customer_id,
        count(bo.id) as booked_opportunity_count,
        sum(coalesce(bo.invoiced_amount, bo.estimated_amount, 0)) as total_opportunity_value,
        min(bo.booked_date) as first_booking_date
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
    group by
        c.id
),
bad_lead_to_lead_status as (
    -- Attempt to link bad leads to lead_status via quote_number matching
    -- This helps understand the full lead journey
    select
        bl.id as bad_lead_id,
        ls.quote_number,
        ls.status as lead_status,
        ls.sales_person,
        ls.branch_name
    from
        bad_leads bl
    left join
        booked_opportunities bo on bl.customer_email = bo.email
        or bl.customer_phone = bo.phone_number
    left join
        lead_status ls on bo.quote_number = ls.quote_number
)
select
    cbl.bad_lead_id,
    cbl.provider,
    cbl.customer_name,
    cbl.customer_email,
    cbl.customer_phone,
    cbl.move_date,
    cbl.date_lead_received,
    cbl.lead_bad_reason,
    cbl.customer_id,
    -- Customer conversion metrics
    coalesce(cjh.total_customer_jobs, 0) as total_customer_jobs,
    coalesce(cjh.booked_jobs, 0) as booked_jobs,
    coalesce(cjh.closed_jobs, 0) as closed_jobs,
    coalesce(cjh.total_customer_revenue, 0) as total_customer_revenue,
    cjh.first_customer_job_date,
    cjh.last_customer_job_date,
    -- Booked opportunity metrics
    coalesce(cbo.booked_opportunity_count, 0) as booked_opportunity_count,
    coalesce(cbo.total_opportunity_value, 0) as total_opportunity_value,
    cbo.first_booking_date,
    -- Lead status linkage
    bltls.quote_number as linked_quote_number,
    bltls.lead_status as linked_lead_status,
    bltls.sales_person as linked_sales_person,
    bltls.branch_name as linked_branch_name,
    -- Conversion analysis
    case
        when coalesce(cjh.total_customer_jobs, 0) > 0 then 'Converted to Customer'
        when coalesce(cbo.booked_opportunity_count, 0) > 0 then 'Booked (Not Yet Customer)'
        else 'Still a Bad Lead'
    end as conversion_status,
    -- Time analysis
    case
        when cjh.first_customer_job_date is not null
        and cbl.date_lead_received is not null
        then cjh.first_customer_job_date - cbl.date_lead_received::timestamp
        else null
    end as days_to_conversion
from
    customer_bad_leads cbl
left join
    customer_job_history cjh on cbl.customer_id = cjh.customer_id
left join
    customer_booked_opportunities cbo on cbl.customer_id = cbo.customer_id
left join
    bad_lead_to_lead_status bltls on cbl.bad_lead_id = bltls.bad_lead_id
order by
    total_customer_revenue desc nulls last,
    total_customer_jobs desc nulls last,
    date_lead_received desc;

