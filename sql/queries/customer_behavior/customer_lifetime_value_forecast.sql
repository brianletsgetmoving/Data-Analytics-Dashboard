-- Customer Lifetime Value Forecast
-- Predictive LTV using historical patterns and trends

with customer_history as (
    select
        c.id as customer_id,
        c.name as customer_name,
        count(j.id) as total_jobs,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        max(j.job_date) - min(j.job_date) as customer_lifetime_days,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(distinct date_trunc('month', j.job_date)) as months_active,
        count(distinct date_trunc('year', j.job_date)) as years_active
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id, c.name
),
ltv_forecast as (
    select
        customer_id,
        customer_name,
        total_jobs,
        first_job_date,
        last_job_date,
        customer_lifetime_days,
        round(extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 365.0, 2) as customer_lifetime_years,
        round(total_revenue::numeric, 2) as current_ltv,
        round(avg_job_value::numeric, 2) as avg_job_value,
        months_active,
        years_active,
        -- Calculate job frequency (jobs per month)
        case
            when customer_lifetime_days > 0 then
                round((total_jobs::numeric / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 30.0)), 2)
            else 0
        end as jobs_per_month,
        -- Calculate monthly revenue rate
        case
            when customer_lifetime_days > 0 then
                round((total_revenue / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 30.0))::numeric, 2)
            else 0
        end as monthly_revenue_rate,
        -- Forecast LTV for next 12 months (assuming same rate)
        case
            when customer_lifetime_days > 0 then
                round((total_revenue + (total_revenue / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 30.0) * 12))::numeric, 2)
            else total_revenue
        end as forecasted_ltv_12_months,
        -- Forecast LTV for next 24 months
        case
            when customer_lifetime_days > 0 then
                round((total_revenue + (total_revenue / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 30.0) * 24))::numeric, 2)
            else total_revenue
        end as forecasted_ltv_24_months,
        -- Forecast LTV for next 36 months
        case
            when customer_lifetime_days > 0 then
                round((total_revenue + (total_revenue / (extract(epoch from customer_lifetime_days)::numeric / 86400.0 / 30.0) * 36))::numeric, 2)
            else total_revenue
        end as forecasted_ltv_36_months
    from
        customer_history
    where
        total_jobs > 0
)
select
    customer_id,
    customer_name,
    total_jobs,
    first_job_date,
    last_job_date,
    customer_lifetime_days,
    customer_lifetime_years,
    current_ltv,
    avg_job_value,
    months_active,
    years_active,
    jobs_per_month,
    monthly_revenue_rate,
    forecasted_ltv_12_months,
    forecasted_ltv_24_months,
    forecasted_ltv_36_months,
    round((forecasted_ltv_12_months - current_ltv)::numeric, 2) as projected_growth_12_months,
    round((forecasted_ltv_24_months - current_ltv)::numeric, 2) as projected_growth_24_months,
    round((forecasted_ltv_36_months - current_ltv)::numeric, 2) as projected_growth_36_months
from
    ltv_forecast
order by
    forecasted_ltv_12_months desc,
    current_ltv desc;

