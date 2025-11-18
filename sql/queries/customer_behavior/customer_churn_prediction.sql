-- Customer Churn Prediction
-- Identify at-risk customers (no jobs in X months)
-- Customers are considered at-risk if they haven't had a job in the last 3, 6, or 12 months

with customer_last_job as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        max(j.job_date) as last_job_date,
        count(j.id) as total_jobs,
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
        c.id, c.name, c.email, c.phone
),
churn_analysis as (
    select
        customer_id,
        customer_name,
        email,
        phone,
        last_job_date,
        total_jobs,
        total_revenue,
        avg_job_value,
        current_date - last_job_date as days_since_last_job,
        case
            when last_job_date is null then 'never_had_job'
            when extract(epoch from (current_date - last_job_date)) / 86400 <= 90 then 'active'
            when extract(epoch from (current_date - last_job_date)) / 86400 <= 180 then 'at_risk_3_months'
            when extract(epoch from (current_date - last_job_date)) / 86400 <= 365 then 'at_risk_6_months'
            else 'churned'
        end as churn_status,
        case
            when last_job_date is not null and extract(epoch from (current_date - last_job_date)) / 86400 > 365 then 'high_risk'
            when last_job_date is not null and extract(epoch from (current_date - last_job_date)) / 86400 > 180 then 'medium_risk'
            when last_job_date is not null and extract(epoch from (current_date - last_job_date)) / 86400 > 90 then 'low_risk'
            else 'no_risk'
        end as risk_level
    from
        customer_last_job
)
select
    customer_id,
    customer_name,
    email,
    phone,
    last_job_date,
    total_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    days_since_last_job,
    churn_status,
    risk_level,
    case
        when days_since_last_job is not null then
            round(extract(epoch from days_since_last_job)::numeric / 86400.0 / 30.0, 1)
        else null
    end as months_since_last_job
from
    churn_analysis
where
    churn_status != 'active'
    and total_jobs > 0
order by
    days_since_last_job desc nulls last,
    total_revenue desc;

