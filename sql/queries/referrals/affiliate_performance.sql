-- Affiliate Performance Analysis
-- affiliateName performance metrics

with affiliate_jobs as (
    select
        j.affiliate_name,
        count(distinct j.id) as total_jobs,
        count(distinct j.customer_id) as customer_count,
        count(distinct j.branch_id) as branches_used,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date
    from
        jobs j
    where
        j.is_duplicate = false
        and j.affiliate_name is not null
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        j.affiliate_name
)
select
    affiliate_name,
    total_jobs,
    customer_count,
    branches_used,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    booked_jobs,
    closed_jobs,
    round((booked_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as booking_rate,
    round((closed_jobs::numeric / nullif(booked_jobs, 0) * 100), 2) as completion_rate,
    round((total_revenue / nullif(customer_count, 0))::numeric, 2) as revenue_per_customer,
    first_job_date,
    last_job_date
from
    affiliate_jobs
order by
    total_revenue desc;

