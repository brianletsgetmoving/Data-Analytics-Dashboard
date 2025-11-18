-- City to City Routes
-- Most popular city-to-city moving routes

select
    origin_city,
    origin_state,
    destination_city,
    destination_state,
    count(*) as route_count,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    round(count(*) filter (where opportunity_status = 'BOOKED')::numeric / nullif(count(*), 0) * 100, 2) as booking_rate_percent
from
    jobs
where
    is_duplicate = false
    and origin_city is not null
    and destination_city is not null
group by
    origin_city,
    origin_state,
    destination_city,
    destination_state
order by
    route_count desc
limit
    100;

