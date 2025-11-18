-- Market Share Analysis
-- Market share by region/city

with geographic_metrics as (
    select
        origin_city,
        origin_state,
        destination_city,
        destination_state,
        count(*) as total_jobs,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value,
        count(distinct branch_name) as branches_serving
    from
        jobs
    where
        is_duplicate = false
        and opportunity_status in ('BOOKED', 'CLOSED')
        and origin_city is not null
    group by
        origin_city,
        origin_state,
        destination_city,
        destination_state
),
total_market as (
    select
        sum(total_jobs) as market_total_jobs,
        sum(total_revenue) as market_total_revenue,
        sum(unique_customers) as market_total_customers
    from
        geographic_metrics
)
select
    gm.origin_city,
    gm.origin_state,
    gm.destination_city,
    gm.destination_state,
    gm.total_jobs,
    gm.unique_customers,
    round(gm.total_revenue::numeric, 2) as total_revenue,
    round(gm.avg_job_value::numeric, 2) as avg_job_value,
    gm.branches_serving,
    -- Market share calculations
    round((gm.total_jobs::numeric / nullif(tm.market_total_jobs, 0) * 100), 2) as market_share_jobs_percent,
    round((gm.total_revenue / nullif(tm.market_total_revenue, 0) * 100), 2) as market_share_revenue_percent,
    round((gm.unique_customers::numeric / nullif(tm.market_total_customers, 0) * 100), 2) as market_share_customers_percent,
    -- Market totals
    tm.market_total_jobs,
    round(tm.market_total_revenue::numeric, 2) as market_total_revenue,
    tm.market_total_customers,
    case
        when (gm.total_revenue / nullif(tm.market_total_revenue, 0) * 100) > 5 then 'major_market'
        when (gm.total_revenue / nullif(tm.market_total_revenue, 0) * 100) > 2 then 'significant_market'
        when (gm.total_revenue / nullif(tm.market_total_revenue, 0) * 100) > 1 then 'moderate_market'
        else 'small_market'
    end as market_category
from
    geographic_metrics gm,
    total_market tm
order by
    gm.total_revenue desc;

