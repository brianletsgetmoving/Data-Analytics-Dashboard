-- Customer Acquisition Cohorts
-- Cohort analysis by customer acquisition date (first_lead_date)

with customer_cohorts as (
    select
        c.id as customer_id,
        c.name,
        date_trunc('month', c.first_lead_date) as acquisition_month,
        date_trunc('month', j.job_date) as job_month,
        count(distinct j.id) as jobs_in_month,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue_in_month
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.first_lead_date is not null
        and j.job_date >= c.first_lead_date
    group by
        c.id,
        c.name,
        date_trunc('month', c.first_lead_date),
        date_trunc('month', j.job_date)
),
cohort_periods as (
    select
        customer_id,
        name,
        acquisition_month,
        job_month,
        jobs_in_month,
        revenue_in_month,
        extract(month from age(job_month, acquisition_month)) as months_since_acquisition
    from
        customer_cohorts
)
select
    acquisition_month,
    months_since_acquisition,
    count(distinct customer_id) as active_customers,
    sum(jobs_in_month) as total_jobs,
    round(sum(revenue_in_month)::numeric, 2) as total_revenue,
    round(avg(jobs_in_month)::numeric, 2) as avg_jobs_per_customer,
    round(avg(revenue_in_month)::numeric, 2) as avg_revenue_per_customer
from
    cohort_periods
group by
    acquisition_month,
    months_since_acquisition
order by
    acquisition_month desc,
    months_since_acquisition;

