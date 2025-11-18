-- Job Type Profitability Analysis
-- Profitability analysis by job type

with job_type_metrics as (
    select
        j.job_type,
        count(*) as total_jobs,
        count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(j.total_estimated_cost, 0)) as total_estimated,
        sum(coalesce(j.total_actual_cost, 0)) as total_actual,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as median_job_value,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours
    from
        jobs j
    where
        j.is_duplicate = false
        and j.job_type is not null
    group by
        j.job_type
    having
        count(*) > 0
)
select
    job_type,
    total_jobs,
    booked_jobs,
    closed_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(total_estimated::numeric, 2) as total_estimated,
    round(total_actual::numeric, 2) as total_actual,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value,
    round((total_actual - total_estimated)::numeric, 2) as variance_amount,
    case
        when total_estimated > 0 then
            round(((total_actual - total_estimated)::numeric / total_estimated * 100), 2)
        else null
    end as variance_percent,
    total_crew_hours,
    total_truck_hours,
    round((total_revenue / nullif(total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
    round((total_revenue / nullif(total_truck_hours, 0))::numeric, 2) as revenue_per_truck_hour
from
    job_type_metrics
order by
    total_revenue desc;

