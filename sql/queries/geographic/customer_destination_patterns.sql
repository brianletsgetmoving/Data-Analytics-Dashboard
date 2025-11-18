-- Customer Destination Patterns
-- Customer destination preferences analysis

with customer_destinations as (
    select
        c.destination_city,
        c.destination_state,
        count(distinct c.id) as customer_count,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(distinct c.origin_city) as origin_cities_count,
        count(distinct c.origin_state) as origin_states_count
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.destination_city is not null
        and c.destination_state is not null
    group by
        c.destination_city,
        c.destination_state
)
select
    destination_city,
    destination_state,
    customer_count,
    total_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    origin_cities_count,
    origin_states_count,
    round((total_jobs::numeric / nullif(customer_count, 0)), 2) as jobs_per_customer,
    round((total_revenue / nullif(customer_count, 0))::numeric, 2) as revenue_per_customer
from
    customer_destinations
order by
    customer_count desc,
    total_revenue desc;

