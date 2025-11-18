-- Customer Retention Cohort Analysis
-- Customer retention rates by acquisition cohort

with customer_cohorts as (
    select
        c.id as customer_id,
        date_trunc('quarter', c.first_lead_date) as acquisition_quarter,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        count(distinct j.id) as total_jobs,
        count(distinct date_trunc('quarter', j.job_date)) as active_quarters
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
        date_trunc('quarter', c.first_lead_date)
),
quarterly_activity as (
    select
        cc.customer_id,
        cc.acquisition_quarter,
        date_trunc('quarter', j.job_date) as activity_quarter,
        extract(quarter from age(date_trunc('quarter', j.job_date), cc.acquisition_quarter)) as quarters_since_acquisition
    from
        customer_cohorts cc
    inner join
        jobs j on cc.customer_id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        cc.customer_id,
        cc.acquisition_quarter,
        date_trunc('quarter', j.job_date)
)
select
    acquisition_quarter,
    quarters_since_acquisition,
    count(distinct customer_id) as active_customers,
    count(distinct customer_id) filter (where quarters_since_acquisition = 0) as cohort_size,
    round((count(distinct customer_id)::numeric / nullif(count(distinct customer_id) filter (where quarters_since_acquisition = 0), 0) * 100), 2) as retention_rate
from
    quarterly_activity
group by
    acquisition_quarter,
    quarters_since_acquisition
having
    count(distinct customer_id) filter (where quarters_since_acquisition = 0) > 0
order by
    acquisition_quarter desc,
    quarters_since_acquisition;

