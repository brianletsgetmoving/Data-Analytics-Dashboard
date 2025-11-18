-- Repeat Customer Patterns
-- Analyze patterns in repeat customer behavior

with repeat_customers as (
    select
        c.id as customer_id,
        c.name as customer_name,
        count(distinct j.id) as total_jobs,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        max(j.job_date) - min(j.job_date) as customer_lifetime_days,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        -- Time between jobs
        array_agg(j.job_date order by j.job_date) as job_dates_array
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id, c.name
    having
        count(distinct j.id) > 1
),
time_between_jobs as (
    select
        customer_id,
        customer_name,
        total_jobs,
        first_job_date,
        last_job_date,
        customer_lifetime_days,
        round(extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 365.0, 2) as customer_lifetime_years,
        total_revenue,
        avg_job_value,
        -- Calculate average days between jobs
        case
            when total_jobs > 1 then
                round((customer_lifetime_days::numeric / (total_jobs - 1)), 0)
            else null
        end as avg_days_between_jobs,
        -- Calculate jobs per year
        case
            when customer_lifetime_days > 0 then
                round((total_jobs::numeric / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 365.0)), 2)
            else null
        end as jobs_per_year,
        -- Calculate monthly revenue rate
        case
            when customer_lifetime_days > 0 then
                round((total_revenue / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 30.0))::numeric, 2)
            else null
        end as monthly_revenue_rate
    from
        repeat_customers
)
select
    customer_id,
    customer_name,
    total_jobs,
    first_job_date,
    last_job_date,
    customer_lifetime_days,
    customer_lifetime_years,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    avg_days_between_jobs,
    case
        when avg_days_between_jobs is not null then
            round(avg_days_between_jobs::numeric / 30.0, 1)
        else null
    end as avg_months_between_jobs,
    jobs_per_year,
    monthly_revenue_rate,
    case
        when avg_days_between_jobs <= 30 then 'frequent'
        when avg_days_between_jobs <= 90 then 'regular'
        when avg_days_between_jobs <= 180 then 'occasional'
        else 'infrequent'
    end as repeat_pattern_category,
    case
        when jobs_per_year >= 4 then 'very_active'
        when jobs_per_year >= 2 then 'active'
        when jobs_per_year >= 1 then 'moderate'
        else 'low_activity'
    end as activity_level
from
    time_between_jobs
order by
    total_revenue desc,
    total_jobs desc;

