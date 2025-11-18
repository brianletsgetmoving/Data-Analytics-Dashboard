-- Crew and Truck Utilization by Route Type
-- Resource utilization analysis by route type (local, intrastate, interstate)

with route_utilization as (
    select
        case
            when j.origin_city = j.destination_city then 'local'
            when j.origin_state = j.destination_state then 'intrastate'
            else 'interstate'
        end as route_type,
        j.job_type,
        j.branch_name,
        count(*) as total_jobs,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_per_job,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks_per_job,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.origin_city is not null
        and j.destination_city is not null
    group by
        case
            when j.origin_city = j.destination_city then 'local'
            when j.origin_state = j.destination_state then 'intrastate'
            else 'interstate'
        end,
        j.job_type,
        j.branch_name
)
select
    route_type,
    job_type,
    branch_name,
    total_jobs,
    total_crew_hours,
    total_truck_hours,
    round(avg_crew_per_job::numeric, 2) as avg_crew_per_job,
    round(avg_trucks_per_job::numeric, 2) as avg_trucks_per_job,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((total_revenue / nullif(total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
    round((total_revenue / nullif(total_truck_hours, 0))::numeric, 2) as revenue_per_truck_hour,
    round((total_crew_hours::numeric / nullif(total_jobs, 0)), 2) as crew_hours_per_job,
    round((total_truck_hours::numeric / nullif(total_jobs, 0)), 2) as truck_hours_per_job
from
    route_utilization
order by
    route_type,
    total_revenue desc;

