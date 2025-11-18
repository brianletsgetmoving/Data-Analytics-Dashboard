-- Geographic Coverage
-- Geographic coverage analysis by state/province

with origin_coverage as (
    select
        origin_state as state,
        'origin' as coverage_type,
        count(*) as job_count,
        count(distinct origin_city) as cities_served,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue
    from
        jobs
    where
        is_duplicate = false
        and origin_state is not null
    group by
        origin_state
),
destination_coverage as (
    select
        destination_state as state,
        'destination' as coverage_type,
        count(*) as job_count,
        count(distinct destination_city) as cities_served,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue
    from
        jobs
    where
        is_duplicate = false
        and destination_state is not null
    group by
        destination_state
)
select
    state,
    coverage_type,
    job_count,
    cities_served,
    unique_customers,
    total_revenue
from
    origin_coverage
union all
select
    state,
    coverage_type,
    job_count,
    cities_served,
    unique_customers,
    total_revenue
from
    destination_coverage
order by
    state,
    coverage_type,
    job_count desc;

