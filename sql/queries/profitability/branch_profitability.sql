-- Branch Profitability Analysis
-- Profitability by branch with cost analysis and margin calculations

with branch_metrics as (
    select
        j.branch_name,
        count(*) as total_jobs,
        count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (where j.opportunity_status = 'BOOKED') as booked_revenue,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (where j.opportunity_status = 'CLOSED') as closed_revenue,
        sum(coalesce(j.total_estimated_cost, 0)) as total_estimated,
        sum(coalesce(j.total_actual_cost, 0)) as total_actual,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_per_job,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks_per_job
    from
        jobs j
    where
        j.is_duplicate = false
        and j.branch_name is not null
    group by
        j.branch_name
)
select
    branch_name,
    total_jobs,
    booked_jobs,
    closed_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(booked_revenue::numeric, 2) as booked_revenue,
    round(closed_revenue::numeric, 2) as closed_revenue,
    round(total_estimated::numeric, 2) as total_estimated,
    round(total_actual::numeric, 2) as total_actual,
    round((total_actual - total_estimated)::numeric, 2) as variance_amount,
    case
        when total_estimated > 0 then
            round(((total_actual - total_estimated)::numeric / total_estimated * 100), 2)
        else null
    end as variance_percent,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job,
    round((total_revenue / nullif(total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
    round((total_revenue / nullif(total_truck_hours, 0))::numeric, 2) as revenue_per_truck_hour,
    total_crew_hours,
    total_truck_hours,
    round(avg_crew_per_job::numeric, 2) as avg_crew_per_job,
    round(avg_trucks_per_job::numeric, 2) as avg_trucks_per_job
from
    branch_metrics
order by
    total_revenue desc;

