-- Revenue by Geographic Region
-- Revenue by origin and destination cities/states

with origin_revenue as (
    select
        origin_city,
        origin_state,
        'origin' as region_type,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value
    from
        jobs
    where
        is_duplicate = false
        and origin_city is not null
    group by
        origin_city,
        origin_state
),
destination_revenue as (
    select
        destination_city,
        destination_state,
        'destination' as region_type,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value
    from
        jobs
    where
        is_duplicate = false
        and destination_city is not null
    group by
        destination_city,
        destination_state
)
select
    region_type,
    origin_city as city,
    origin_state as state,
    job_count,
    total_revenue,
    avg_job_value
from
    origin_revenue
union all
select
    region_type,
    destination_city as city,
    destination_state as state,
    job_count,
    total_revenue,
    avg_job_value
from
    destination_revenue
order by
    total_revenue desc;

