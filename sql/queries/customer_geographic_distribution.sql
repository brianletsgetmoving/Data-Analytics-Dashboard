-- Customer Geographic Distribution
-- Distribution of customers by origin and destination cities

with customer_locations as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.origin_city,
        c.origin_state,
        c.destination_city,
        c.destination_state,
        count(j.id) as total_jobs
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        or j.id is null
    group by
        c.id, c.name, c.origin_city, c.origin_state, c.destination_city, c.destination_state
)
select
    origin_city,
    origin_state,
    count(distinct customer_id) as customers_from_origin,
    destination_city,
    destination_state,
    count(distinct customer_id) as customers_to_destination,
    count(distinct customer_id) filter (where origin_city is not null and destination_city is not null) as customers_with_both_locations
from
    customer_locations
group by
    origin_city, origin_state, destination_city, destination_state
order by
    customers_from_origin desc,
    customers_to_destination desc;

