-- Customer Lifetime Value Analysis
-- Calculates total revenue, job counts, and lifetime duration per customer
-- Filters out duplicate jobs and only includes customers with multiple jobs

with customer_jobs as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(j.id) as total_jobs,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        max(j.job_date) - min(j.job_date) as customer_lifetime_days,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost)) as avg_job_value,
        count(distinct j.branch_name) as branches_used,
        count(distinct date_trunc('year', j.job_date)) as years_active,
        -- Revenue by status
        sum(case when j.opportunity_status = 'BOOKED' 
            then coalesce(j.total_actual_cost, j.total_estimated_cost, 0) else 0 end) as booked_revenue,
        sum(case when j.opportunity_status = 'CLOSED' 
            then coalesce(j.total_actual_cost, j.total_estimated_cost, 0) else 0 end) as closed_revenue,
        -- Job counts by status
        count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        count(*) filter (where j.opportunity_status = 'LOST') as lost_jobs,
        count(*) filter (where j.opportunity_status = 'QUOTED') as quoted_jobs
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.customer_id is not null
    group by
        c.id, c.name, c.email, c.phone
)
select
    customer_id,
    customer_name,
    email,
    phone,
    total_jobs,
    first_job_date,
    last_job_date,
    customer_lifetime_days,
    round(extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 365.0, 2) as customer_lifetime_years,
    total_revenue as customer_lifetime_value,
    avg_job_value,
    branches_used,
    years_active,
    booked_revenue,
    closed_revenue,
    booked_jobs,
    closed_jobs,
    lost_jobs,
    quoted_jobs,
    -- Additional metrics
    round(total_revenue / nullif(extract(epoch from customer_lifetime_days)::numeric / 86400.0, 0) * 365, 2) as annual_revenue_rate,
    round(avg_job_value, 2) as average_job_value
from
    customer_jobs
where
    total_jobs > 1
order by
    total_revenue desc,
    total_jobs desc;

