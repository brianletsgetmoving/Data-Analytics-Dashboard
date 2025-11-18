-- Job Type Geographic Profitability
-- Job type profitability analysis by geographic region

with geographic_profitability as (
    select
        j.job_type,
        j.origin_state,
        j.destination_state,
        j.branch_name,
        count(*) as total_jobs,
        count(distinct j.customer_id) as customer_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(j.total_estimated_cost, 0)) as total_estimated,
        sum(coalesce(j.total_actual_cost, 0)) as total_actual,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_size,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.job_type is not null
        and j.origin_state is not null
    group by
        j.job_type,
        j.origin_state,
        j.destination_state,
        j.branch_name
)
select
    job_type,
    origin_state,
    destination_state,
    branch_name,
    total_jobs,
    customer_count,
    round(total_revenue::numeric, 2) as total_revenue,
    round(total_estimated::numeric, 2) as total_estimated,
    round(total_actual::numeric, 2) as total_actual,
    round((total_actual - total_estimated)::numeric, 2) as variance_amount,
    round(((total_actual - total_estimated) / nullif(total_estimated, 0) * 100)::numeric, 2) as variance_percent,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(avg_crew_size::numeric, 2) as avg_crew_size,
    round(avg_trucks::numeric, 2) as avg_trucks,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job
from
    geographic_profitability
order by
    total_revenue desc;

