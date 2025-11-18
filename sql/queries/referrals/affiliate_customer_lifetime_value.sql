-- Affiliate Customer Lifetime Value
-- Customer lifetime value by affiliate

with affiliate_customers as (
    select
        j.affiliate_name,
        j.customer_id,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        max(j.job_date) - min(j.job_date) as customer_lifetime_days
    from
        jobs j
    where
        j.is_duplicate = false
        and j.affiliate_name is not null
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        j.affiliate_name,
        j.customer_id
)
select
    affiliate_name,
    count(distinct customer_id) as customer_count,
    sum(total_jobs) as total_jobs,
    round(sum(total_revenue)::numeric, 2) as total_revenue,
    round(avg(total_jobs)::numeric, 2) as avg_jobs_per_customer,
    round(avg(total_revenue)::numeric, 2) as avg_lifetime_value,
    round(percentile_cont(0.5) within group (order by total_revenue)::numeric, 2) as median_lifetime_value,
    round(avg(extract(epoch from customer_lifetime_days) / 86400.0 / 365.0)::numeric, 2) as avg_customer_lifetime_years,
    round((sum(total_revenue) / nullif(count(distinct customer_id), 0))::numeric, 2) as revenue_per_customer
from
    affiliate_customers
group by
    affiliate_name
order by
    total_revenue desc;

