-- Job Estimated vs Actual Cost Comparison
-- Comparison of estimated vs actual costs with variance analysis

select
    id,
    job_id,
    job_number,
    customer_id,
    opportunity_status,
    job_date,
    total_estimated_cost,
    total_actual_cost,
    total_actual_cost - total_estimated_cost as cost_variance,
    round((total_actual_cost - total_estimated_cost)::numeric / nullif(total_estimated_cost, 0) * 100, 2) as variance_percent,
    hourly_rate_quoted,
    hourly_rate_billed,
    hourly_rate_billed - hourly_rate_quoted as rate_variance,
    case
        when total_actual_cost > total_estimated_cost * 1.1 then 'Over Budget (>10%)'
        when total_actual_cost < total_estimated_cost * 0.9 then 'Under Budget (>10%)'
        else 'Within Budget'
    end as budget_status
from
    jobs
where
    is_duplicate = false
    and total_estimated_cost is not null
    and total_actual_cost is not null
order by
    abs(total_actual_cost - total_estimated_cost) desc;

