-- Branch Performance Comparison
-- Comparative performance across all branches

select
    branch_name,
    count(*) as total_jobs,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    count(*) filter (where opportunity_status = 'LOST') as lost_jobs,
    round(count(*) filter (where opportunity_status = 'BOOKED')::numeric / nullif(count(*), 0) * 100, 2) as booking_rate_percent,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    count(distinct customer_id) as unique_customers,
    count(distinct sales_person_name) as sales_people_count,
    min(job_date) as first_job_date,
    max(job_date) as last_job_date
from
    jobs
where
    is_duplicate = false
    and branch_name is not null
group by
    branch_name
order by
    total_revenue desc;

