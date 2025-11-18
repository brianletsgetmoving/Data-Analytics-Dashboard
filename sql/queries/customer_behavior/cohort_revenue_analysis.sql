-- Cohort Revenue Analysis
-- Revenue patterns by customer acquisition cohort

with customer_cohorts as (
    select
        c.id as customer_id,
        date_trunc('month', c.first_lead_date) as acquisition_month,
        date_trunc('year', c.first_lead_date) as acquisition_year,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.first_lead_date is not null
    group by
        c.id,
        date_trunc('month', c.first_lead_date),
        date_trunc('year', c.first_lead_date)
),
cohort_revenue as (
    select
        cc.customer_id,
        cc.acquisition_month,
        cc.acquisition_year,
        date_trunc('month', j.job_date) as revenue_month,
        extract(month from age(date_trunc('month', j.job_date), cc.acquisition_month)) as months_since_acquisition,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as monthly_revenue
    from
        customer_cohorts cc
    inner join
        jobs j on cc.customer_id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        cc.customer_id,
        cc.acquisition_month,
        cc.acquisition_year,
        date_trunc('month', j.job_date)
)
select
    acquisition_year,
    acquisition_month,
    months_since_acquisition,
    count(distinct customer_id) as active_customers,
    round(sum(monthly_revenue)::numeric, 2) as total_revenue,
    round(avg(monthly_revenue)::numeric, 2) as avg_revenue_per_customer,
    round(percentile_cont(0.5) within group (order by monthly_revenue)::numeric, 2) as median_revenue_per_customer
from
    cohort_revenue
group by
    acquisition_year,
    acquisition_month,
    months_since_acquisition
order by
    acquisition_year desc,
    acquisition_month desc,
    months_since_acquisition;

