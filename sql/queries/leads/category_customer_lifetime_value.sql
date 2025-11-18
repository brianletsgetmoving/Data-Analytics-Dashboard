-- Category Customer Lifetime Value
-- Customer lifetime value analysis by lead source category

with category_customers as (
    select
        lsr.category,
        c.id as customer_id,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        max(j.job_date) - min(j.job_date) as customer_lifetime_days
    from
        lead_sources lsr
    inner join
        lead_status ls on lsr.id = ls.lead_source_id
    inner join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    inner join
        customers c on bo.customer_id = c.id
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and lsr.category is not null
    group by
        lsr.category,
        c.id
)
select
    category,
    count(distinct customer_id) as customer_count,
    sum(total_jobs) as total_jobs,
    round(sum(total_revenue)::numeric, 2) as total_revenue,
    round(avg(total_jobs)::numeric, 2) as avg_jobs_per_customer,
    round(avg(total_revenue)::numeric, 2) as avg_lifetime_value,
    round(percentile_cont(0.5) within group (order by total_revenue)::numeric, 2) as median_lifetime_value,
    round(avg(extract(epoch from customer_lifetime_days) / 86400.0 / 365.0)::numeric, 2) as avg_customer_lifetime_years,
    round((sum(total_revenue) / nullif(count(distinct customer_id), 0))::numeric, 2) as revenue_per_customer
from
    category_customers
group by
    category
order by
    total_revenue desc;

