-- Revenue by Job Status
-- Revenue breakdown by job status

select
    opportunity_status,
    count(*) as job_count,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    min(coalesce(total_actual_cost, total_estimated_cost)) as min_job_value,
    max(coalesce(total_actual_cost, total_estimated_cost)) as max_job_value,
    percentile_cont(0.5) within group (order by coalesce(total_actual_cost, total_estimated_cost)) as median_job_value,
    round(sum(coalesce(total_actual_cost, total_estimated_cost, 0))::numeric / 
        (select sum(coalesce(total_actual_cost, total_estimated_cost, 0)) from jobs where is_duplicate = false) * 100, 2) as revenue_percentage
from
    jobs
where
    is_duplicate = false
    and opportunity_status is not null
group by
    opportunity_status
order by
    total_revenue desc;

