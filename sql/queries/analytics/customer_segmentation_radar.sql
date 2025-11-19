-- Radar Chart: Customer Segmentation Analysis
-- This query is used by the /api/v1/analytics/radar endpoint
-- Returns multi-dimensional customer metrics for radar chart visualization
-- 
-- Note: Filters are applied dynamically via build_where_clause in the Python code
-- 
-- Returns metrics:
--   - Lifetime Value (average customer LTV)
--   - Job Frequency (average jobs per customer)
--   - Avg Job Value (average value per job)
--   - Customer Lifespan (average days between first and last job)

with customer_metrics as (
    select
        c.id,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as lifetime_value,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        extract(epoch from (max(j.job_date) - min(j.job_date))) / 86400.0 as customer_lifespan_days
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        -- Filters are injected here dynamically
        j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.job_date is not null
    group by
        c.id
    having
        count(distinct j.id) > 0
)
select
    'Lifetime Value' as subject,
    coalesce(avg(lifetime_value), 0) as value,
    coalesce(max(lifetime_value), 0) as full_mark
from
    customer_metrics
union all
select
    'Job Frequency' as subject,
    coalesce(avg(total_jobs), 0) as value,
    coalesce(max(total_jobs), 0) as full_mark
from
    customer_metrics
union all
select
    'Avg Job Value' as subject,
    coalesce(avg(avg_job_value), 0) as value,
    coalesce(max(avg_job_value), 0) as full_mark
from
    customer_metrics
union all
select
    'Customer Lifespan' as subject,
    coalesce(avg(customer_lifespan_days), 0) as value,
    coalesce(max(customer_lifespan_days), 0) as full_mark
from
    customer_metrics
where
    customer_lifespan_days > 0;

