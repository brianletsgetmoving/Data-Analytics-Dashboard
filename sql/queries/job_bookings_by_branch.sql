-- Job Bookings by Branch
-- Total bookings count and revenue per branch

select
    branch_name,
    count(*) as total_jobs,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    count(*) filter (where opportunity_status = 'QUOTED') as quoted_jobs,
    count(*) filter (where opportunity_status = 'LOST') as lost_jobs,
    count(*) filter (where opportunity_status = 'CANCELLED') as cancelled_jobs,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    round(count(*) filter (where opportunity_status = 'BOOKED')::numeric / nullif(count(*), 0) * 100, 2) as booking_rate_percent
from
    jobs
where
    is_duplicate = false
    and branch_name is not null
group by
    branch_name
order by
    total_revenue desc;

