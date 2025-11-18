-- Customer Relationship Summary
-- Overview of all customer relationships across jobs, bad leads, and booked opportunities
-- This query provides a comprehensive view of each customer's interactions across all modules

with customer_jobs_summary as (
    -- Aggregate job data for each customer
    -- Only includes booked and closed jobs (customers, not leads)
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(j.id) as total_jobs,
        count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_job_revenue,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id, c.name, c.email, c.phone
),
customer_bad_leads_summary as (
    -- Count bad leads associated with customers
    select
        c.id as customer_id,
        count(bl.id) as bad_lead_count,
        array_agg(distinct bl.lead_bad_reason) filter (where bl.lead_bad_reason is not null) as bad_lead_reasons
    from
        customers c
    left join
        bad_leads bl on c.id = bl.customer_id
    group by
        c.id
),
customer_booked_opportunities_summary as (
    -- Count booked opportunities for each customer
    select
        c.id as customer_id,
        count(bo.id) as booked_opportunity_count,
        sum(coalesce(bo.invoiced_amount, bo.estimated_amount, 0)) as total_opportunity_value,
        min(bo.booked_date) as first_booking_date,
        max(bo.booked_date) as last_booking_date
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
    group by
        c.id
)
select
    cjs.customer_id,
    cjs.customer_name,
    cjs.email,
    cjs.phone,
    -- Job metrics (customers only)
    coalesce(cjs.total_jobs, 0) as total_jobs,
    coalesce(cjs.booked_jobs, 0) as booked_jobs,
    coalesce(cjs.closed_jobs, 0) as closed_jobs,
    coalesce(cjs.total_job_revenue, 0) as total_job_revenue,
    cjs.first_job_date,
    cjs.last_job_date,
    -- Bad lead metrics
    coalesce(cbls.bad_lead_count, 0) as bad_lead_count,
    cbls.bad_lead_reasons,
    -- Booked opportunity metrics
    coalesce(cbos.booked_opportunity_count, 0) as booked_opportunity_count,
    coalesce(cbos.total_opportunity_value, 0) as total_opportunity_value,
    cbos.first_booking_date,
    cbos.last_booking_date,
    -- Customer classification
    case
        when coalesce(cjs.total_jobs, 0) > 0 then 'Customer'
        when coalesce(cbos.booked_opportunity_count, 0) > 0 then 'Customer (Booked Opportunity)'
        when coalesce(cbls.bad_lead_count, 0) > 0 then 'Lead (Bad Lead)'
        else 'Lead (No Activity)'
    end as customer_type
from
    customer_jobs_summary cjs
full outer join
    customer_bad_leads_summary cbls on cjs.customer_id = cbls.customer_id
full outer join
    customer_booked_opportunities_summary cbos on coalesce(cjs.customer_id, cbls.customer_id) = cbos.customer_id
full outer join
    customers c on coalesce(cjs.customer_id, cbls.customer_id, cbos.customer_id) = c.id
where
    coalesce(cjs.total_jobs, 0) > 0
    or coalesce(cbls.bad_lead_count, 0) > 0
    or coalesce(cbos.booked_opportunity_count, 0) > 0
order by
    total_job_revenue desc nulls last,
    total_jobs desc nulls last;

