-- Customer Retention Rate Analysis
-- Calculates percentage of customers with repeat jobs (retention rate)
-- Compares one-time customers vs repeat customers

with customer_job_counts as (
    select
        c.id as customer_id,
        c.name as customer_name,
        count(j.id) as total_jobs
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.customer_id is not null
    group by
        c.id, c.name
),
retention_summary as (
    select
        count(*) filter (where total_jobs = 1) as one_time_customers,
        count(*) filter (where total_jobs > 1) as repeat_customers,
        count(*) as total_customers_with_jobs
    from
        customer_job_counts
)
select
    one_time_customers,
    repeat_customers,
    total_customers_with_jobs,
    round(repeat_customers::numeric / nullif(total_customers_with_jobs, 0) * 100, 2) as retention_rate_percent,
    round(one_time_customers::numeric / nullif(total_customers_with_jobs, 0) * 100, 2) as one_time_rate_percent
from
    retention_summary;

