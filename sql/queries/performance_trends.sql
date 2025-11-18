-- Performance Trends
-- Performance trends over time for sales and users

with monthly_sales_performance as (
    select
        date_trunc('month', j.job_date) as month,
        j.sales_person_name,
        count(*) as jobs_handled,
        count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue
    from
        jobs j
    where
        j.is_duplicate = false
        and j.sales_person_name is not null
        and j.job_date is not null
    group by
        date_trunc('month', j.job_date),
        j.sales_person_name
)
select
    'sales' as performance_type,
    month,
    sales_person_name as performer_name,
    jobs_handled,
    booked_jobs,
    revenue,
    round(booked_jobs::numeric / nullif(jobs_handled, 0) * 100, 2) as booking_rate_percent
from
    monthly_sales_performance
order by
    month desc,
    revenue desc;

