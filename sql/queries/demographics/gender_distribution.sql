-- Gender Distribution Analysis
-- Customer gender distribution across all customers and by various segments

with customer_gender_stats as (
    select
        c.gender,
        count(distinct c.id) as total_customers,
        count(distinct j.id) as total_jobs,
        count(distinct case when j.opportunity_status in ('BOOKED', 'CLOSED') then j.id end) as active_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.gender
),
gender_summary as (
    select
        gender,
        total_customers,
        total_jobs,
        active_jobs,
        round(total_revenue::numeric, 2) as total_revenue,
        round(avg_job_value::numeric, 2) as avg_job_value,
        round(total_customers::numeric / sum(total_customers) over () * 100, 2) as customer_percentage,
        round(total_jobs::numeric / nullif(total_customers, 0), 2) as jobs_per_customer
    from
        customer_gender_stats
)
select
    coalesce(gender::text, 'UNKNOWN') as gender,
    total_customers,
    total_jobs,
    active_jobs,
    total_revenue,
    avg_job_value,
    customer_percentage,
    jobs_per_customer
from
    gender_summary
order by
    total_customers desc;

