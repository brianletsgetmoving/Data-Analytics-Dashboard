-- Repeat Customers Analysis
-- Detailed analysis of customers with 2+ jobs including their job counts and revenue

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
        count(distinct j.job_type) as job_types_used,
        count(distinct date_trunc('year', j.job_date)) as years_active
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.customer_id is not null
    group by
        c.id, c.name, c.email, c.phone
    having
        count(j.id) > 1
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
    total_revenue,
    avg_job_value,
    branches_used,
    job_types_used,
    years_active,
    -- Categorize by job frequency
    case
        when total_jobs = 2 then '2 jobs'
        when total_jobs between 3 and 5 then '3-5 jobs'
        when total_jobs between 6 and 10 then '6-10 jobs'
        else '10+ jobs'
    end as customer_segment
from
    customer_jobs
order by
    total_jobs desc,
    total_revenue desc;

