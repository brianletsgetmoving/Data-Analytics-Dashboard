-- Routing Efficiency Analysis
-- Geographic routing optimization opportunities

with route_analysis as (
    select
        j.origin_city,
        j.origin_state,
        j.destination_city,
        j.destination_state,
        j.branch_name,
        count(*) as route_frequency,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        -- Calculate distance estimate (simplified - would need actual coordinates for real distance)
        case
            when j.origin_city = j.destination_city then 'local'
            when j.origin_state = j.destination_state then 'intrastate'
            else 'interstate'
        end as route_type,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_size,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.origin_city is not null
        and j.destination_city is not null
    group by
        j.origin_city,
        j.origin_state,
        j.destination_city,
        j.destination_state,
        j.branch_name
)
select
    origin_city,
    origin_state,
    destination_city,
    destination_state,
    branch_name,
    route_frequency,
    route_type,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(avg_crew_size::numeric, 2) as avg_crew_size,
    round(avg_trucks::numeric, 2) as avg_trucks,
    first_job_date,
    last_job_date,
    round((total_revenue / nullif(route_frequency, 0))::numeric, 2) as revenue_per_trip,
    case
        when route_frequency >= 10 then 'high_frequency'
        when route_frequency >= 5 then 'medium_frequency'
        when route_frequency >= 2 then 'low_frequency'
        else 'one_time'
    end as frequency_category
from
    route_analysis
order by
    route_frequency desc,
    total_revenue desc;

