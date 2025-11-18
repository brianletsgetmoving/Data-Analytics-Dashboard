-- Origin-Destination Correlations
-- Common origin-destination pairs and route patterns

with route_patterns as (
    select
        c.origin_city,
        c.origin_state,
        c.destination_city,
        c.destination_state,
        count(distinct c.id) as customer_count,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        case
            when c.origin_city = c.destination_city then 'local'
            when c.origin_state = c.destination_state then 'intrastate'
            else 'interstate'
        end as route_type
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.origin_city is not null
        and c.destination_city is not null
    group by
        c.origin_city,
        c.origin_state,
        c.destination_city,
        c.destination_state
)
select
    origin_city,
    origin_state,
    destination_city,
    destination_state,
    route_type,
    customer_count,
    total_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((total_jobs::numeric / nullif(customer_count, 0)), 2) as jobs_per_customer
from
    route_patterns
order by
    customer_count desc,
    total_revenue desc;

