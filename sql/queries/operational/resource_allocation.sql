-- Resource Allocation Analysis
-- Optimal resource allocation by branch/region

with branch_resource_usage as (
    select
        j.branch_name,
        date_trunc('month', j.job_date) as month,
        count(*) as total_jobs,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_per_job,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks_per_job,
        count(distinct date_trunc('day', j.job_date)) as active_days,
        count(distinct j.job_type) as job_types_handled
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.job_date is not null
        and j.branch_name is not null
    group by
        j.branch_name,
        date_trunc('month', j.job_date)
),
resource_efficiency as (
    select
        branch_name,
        month,
        total_jobs,
        total_crew_hours,
        total_truck_hours,
        round(total_revenue::numeric, 2) as total_revenue,
        round(avg_crew_per_job::numeric, 2) as avg_crew_per_job,
        round(avg_trucks_per_job::numeric, 2) as avg_trucks_per_job,
        active_days,
        job_types_handled,
        round((total_jobs::numeric / nullif(active_days, 0)), 2) as jobs_per_day,
        round((total_crew_hours::numeric / nullif(active_days, 0)), 2) as crew_hours_per_day,
        round((total_truck_hours::numeric / nullif(active_days, 0)), 2) as truck_hours_per_day,
        round((total_revenue / nullif(total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
        round((total_revenue / nullif(total_truck_hours, 0))::numeric, 2) as revenue_per_truck_hour,
        round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job
    from
        branch_resource_usage
)
select
    branch_name,
    month,
    total_jobs,
    total_crew_hours,
    total_truck_hours,
    total_revenue,
    avg_crew_per_job,
    avg_trucks_per_job,
    active_days,
    job_types_handled,
    jobs_per_day,
    crew_hours_per_day,
    truck_hours_per_day,
    revenue_per_crew_hour,
    revenue_per_truck_hour,
    revenue_per_job,
    -- Resource utilization scores (assuming 8 hours per day per resource)
    round((crew_hours_per_day / 8 * 100)::numeric, 2) as crew_utilization_percent,
    round((truck_hours_per_day / 8 * 100)::numeric, 2) as truck_utilization_percent,
    case
        when crew_hours_per_day > 6 and truck_hours_per_day > 6 then 'high_utilization'
        when crew_hours_per_day > 4 and truck_hours_per_day > 4 then 'medium_utilization'
        else 'low_utilization'
    end as utilization_category
from
    resource_efficiency
order by
    month desc,
    branch_name,
    total_revenue desc;

