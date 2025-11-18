-- Revenue by Branch
-- Total revenue and average job value per branch

select
    branch_name,
    count(*) as total_jobs,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    round(sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED')::numeric / 
        nullif(count(*) filter (where opportunity_status = 'BOOKED'), 0), 2) as avg_booked_value,
    round(sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED')::numeric / 
        nullif(count(*) filter (where opportunity_status = 'CLOSED'), 0), 2) as avg_closed_value
from
    jobs
where
    is_duplicate = false
    and branch_name is not null
group by
    branch_name
order by
    total_revenue desc;

