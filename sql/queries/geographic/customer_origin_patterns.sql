-- Customer Origin Patterns
-- Customer origin city/state analysis

with customer_origins as (
    select
        c.origin_city,
        c.origin_state,
        count(distinct c.id) as customer_count,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.origin_city is not null
        and c.origin_state is not null
    group by
        c.origin_city,
        c.origin_state
)
select
    origin_city,
    origin_state,
    customer_count,
    total_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((total_jobs::numeric / nullif(customer_count, 0)), 2) as jobs_per_customer,
    round((total_revenue / nullif(customer_count, 0))::numeric, 2) as revenue_per_customer,
    first_job_date,
    last_job_date
from
    customer_origins
order by
    customer_count desc,
    total_revenue desc;

