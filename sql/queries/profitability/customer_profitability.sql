-- Customer Profitability Analysis
-- Most and least profitable customers ranked by lifetime value and margin

with customer_revenue as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(j.total_estimated_cost, 0)) as total_estimated,
        sum(coalesce(j.total_actual_cost, 0)) as total_actual,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        max(j.job_date) - min(j.job_date) as customer_lifetime_days,
        count(distinct j.branch_name) as branches_used,
        count(distinct j.job_type) as job_types_used
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id, c.name, c.email, c.phone
)
select
    customer_id,
    customer_name,
    email,
    phone,
    total_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(total_estimated::numeric, 2) as total_estimated,
    round(total_actual::numeric, 2) as total_actual,
    round((total_actual - total_estimated)::numeric, 2) as variance_amount,
    case
        when total_estimated > 0 then
            round(((total_actual - total_estimated)::numeric / total_estimated * 100), 2)
        else null
    end as variance_percent,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job,
    first_job_date,
    last_job_date,
    customer_lifetime_days,
    branches_used,
    job_types_used,
    case
        when total_revenue >= 5000 then 'high_value'
        when total_revenue >= 2000 then 'medium_value'
        when total_revenue >= 500 then 'low_value'
        else 'minimal_value'
    end as profitability_segment
from
    customer_revenue
where
    total_jobs > 0
order by
    total_revenue desc
limit 500;

