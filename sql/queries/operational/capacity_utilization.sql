-- Capacity Utilization Analysis
-- Crew and truck capacity analysis by branch, job type, and time period

with capacity_metrics as (
    select
        j.branch_name,
        j.job_type,
        date_trunc('month', j.job_date) as month,
        count(*) as total_jobs,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_per_job,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks_per_job,
        max(coalesce(j.actual_number_crew, 0)) as max_crew_per_job,
        max(coalesce(j.actual_number_trucks, 0)) as max_trucks_per_job,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        count(distinct date_trunc('day', j.job_date)) as active_days
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.job_date is not null
    group by
        j.branch_name,
        j.job_type,
        date_trunc('month', j.job_date)
)
select
    branch_name,
    job_type,
    month,
    total_jobs,
    total_crew_hours,
    total_truck_hours,
    round(avg_crew_per_job::numeric, 2) as avg_crew_per_job,
    round(avg_trucks_per_job::numeric, 2) as avg_trucks_per_job,
    max_crew_per_job,
    max_trucks_per_job,
    round(total_revenue::numeric, 2) as total_revenue,
    active_days,
    round((total_jobs::numeric / nullif(active_days, 0)), 2) as jobs_per_day,
    round((total_crew_hours::numeric / nullif(active_days, 0)), 2) as crew_hours_per_day,
    round((total_truck_hours::numeric / nullif(active_days, 0)), 2) as truck_hours_per_day,
    round((total_revenue / nullif(total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
    round((total_revenue / nullif(total_truck_hours, 0))::numeric, 2) as revenue_per_truck_hour,
    -- Capacity utilization score (assuming 8 crew hours per day per crew member and 8 truck hours per day per truck)
    round((total_crew_hours::numeric / nullif(active_days * 8, 0) * 100), 2) as crew_utilization_percent,
    round((total_truck_hours::numeric / nullif(active_days * 8, 0) * 100), 2) as truck_utilization_percent
from
    capacity_metrics
order by
    month desc,
    branch_name,
    total_revenue desc;

