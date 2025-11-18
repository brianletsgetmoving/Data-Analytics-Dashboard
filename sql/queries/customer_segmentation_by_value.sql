-- Customer Segmentation by Lifetime Value
-- Segments customers into CLV tiers: Low, Medium, High, VIP

with customer_clv as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        count(j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.customer_id is not null
    group by
        c.id, c.name, c.email
),
clv_percentiles as (
    select
        percentile_cont(0.25) within group (order by total_revenue) as p25,
        percentile_cont(0.50) within group (order by total_revenue) as p50,
        percentile_cont(0.75) within group (order by total_revenue) as p75,
        percentile_cont(0.90) within group (order by total_revenue) as p90
    from
        customer_clv
    where
        total_revenue > 0
)
select
    cc.customer_id,
    cc.customer_name,
    cc.email,
    cc.total_jobs,
    cc.total_revenue,
    cc.first_job_date,
    cc.last_job_date,
    case
        when cc.total_revenue >= p.p90 then 'VIP'
        when cc.total_revenue >= p.p75 then 'High'
        when cc.total_revenue >= p.p50 then 'Medium'
        when cc.total_revenue >= p.p25 then 'Low'
        else 'Very Low'
    end as clv_segment
from
    customer_clv cc
cross join
    clv_percentiles p
where
    cc.total_jobs > 0
order by
    cc.total_revenue desc;

