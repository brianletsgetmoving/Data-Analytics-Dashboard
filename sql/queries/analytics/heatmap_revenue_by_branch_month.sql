-- Heatmap: Revenue by Branch and Month
-- This query is used by the /api/v1/analytics/heatmap endpoint
-- Note: Filters are applied dynamically via build_where_clause in the Python code
-- 
-- Parameters:
--   - Filters are injected via WHERE clause
--   - dimension: 'revenue' or 'jobs' (determines value calculation)

select
    coalesce(b.name, 'Unknown') as branch_name,
    to_char(date_trunc('month', j.job_date), 'YYYY-MM') as month,
    sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as value
from
    jobs j
left join
    branches b on j.branch_id = b.id
where
    -- Filters are injected here dynamically
    j.job_date is not null
    and j.opportunity_status in ('BOOKED', 'CLOSED')
group by
    b.name,
    date_trunc('month', j.job_date)
order by
    month desc,
    branch_name
limit 200;

