-- Top Destination Cities
-- Top destination cities by job count and revenue

select
    destination_city,
    destination_state,
    count(*) as job_count,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    count(distinct customer_id) as unique_customers,
    count(distinct branch_name) as branches_serving
from
    jobs
where
    is_duplicate = false
    and destination_city is not null
group by
    destination_city,
    destination_state
order by
    job_count desc
limit
    50;

