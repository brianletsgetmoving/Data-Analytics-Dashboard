-- Trend Analysis
-- Identify trends (growth, decline, seasonality)

with monthly_metrics as (
    select
        date_trunc('month', job_date) as month,
        extract(year from job_date) as year,
        extract(month from job_date) as month_number,
        extract(quarter from job_date) as quarter,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        count(distinct customer_id) as unique_customers
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
        and opportunity_status in ('BOOKED', 'CLOSED')
    group by
        date_trunc('month', job_date),
        extract(year from job_date),
        extract(month from job_date),
        extract(quarter from job_date)
),
trend_calculations as (
    select
        month,
        year,
        month_number,
        quarter,
        job_count,
        round(revenue::numeric, 2) as revenue,
        unique_customers,
        -- Previous period comparisons
        lag(job_count, 1) over (order by month) as previous_month_jobs,
        lag(revenue, 1) over (order by month) as previous_month_revenue,
        lag(job_count, 12) over (order by month) as same_month_previous_year_jobs,
        lag(revenue, 12) over (order by month) as same_month_previous_year_revenue,
        -- Moving averages for trend detection
        avg(job_count) over (order by month rows between 2 preceding and current row) as three_month_ma_jobs,
        avg(revenue) over (order by month rows between 2 preceding and current row) as three_month_ma_revenue,
        avg(job_count) over (order by month rows between 5 preceding and current row) as six_month_ma_jobs,
        avg(revenue) over (order by month rows between 5 preceding and current row) as six_month_ma_revenue,
        -- Trend direction
        case
            when job_count > lag(job_count, 1) over (order by month) then 'increasing'
            when job_count < lag(job_count, 1) over (order by month) then 'decreasing'
            else 'stable'
        end as job_trend_direction,
        case
            when revenue > lag(revenue, 1) over (order by month) then 'increasing'
            when revenue < lag(revenue, 1) over (order by month) then 'decreasing'
            else 'stable'
        end as revenue_trend_direction,
        -- Row number for linear regression
        row_number() over (order by month) as period_number
    from
        monthly_metrics
)
select
    month,
    year,
    month_number,
    quarter,
    job_count,
    revenue,
    unique_customers,
    previous_month_jobs,
    round(previous_month_revenue::numeric, 2) as previous_month_revenue,
    same_month_previous_year_jobs,
    round(same_month_previous_year_revenue::numeric, 2) as same_month_previous_year_revenue,
    -- Month-over-month changes
    round(((job_count - previous_month_jobs)::numeric / nullif(previous_month_jobs, 0) * 100), 2) as mom_job_change_percent,
    round(((revenue - previous_month_revenue)::numeric / nullif(previous_month_revenue, 0) * 100), 2) as mom_revenue_change_percent,
    -- Year-over-year changes
    round(((job_count - same_month_previous_year_jobs)::numeric / nullif(same_month_previous_year_jobs, 0) * 100), 2) as yoy_job_change_percent,
    round(((revenue - same_month_previous_year_revenue)::numeric / nullif(same_month_previous_year_revenue, 0) * 100), 2) as yoy_revenue_change_percent,
    -- Moving averages
    round(three_month_ma_jobs::numeric, 2) as three_month_ma_jobs,
    round(three_month_ma_revenue::numeric, 2) as three_month_ma_revenue,
    round(six_month_ma_jobs::numeric, 2) as six_month_ma_jobs,
    round(six_month_ma_revenue::numeric, 2) as six_month_ma_revenue,
    -- Trend analysis
    job_trend_direction,
    revenue_trend_direction,
    case
        when round(((revenue - same_month_previous_year_revenue)::numeric / nullif(same_month_previous_year_revenue, 0) * 100), 2) > 10 then 'strong_growth'
        when round(((revenue - same_month_previous_year_revenue)::numeric / nullif(same_month_previous_year_revenue, 0) * 100), 2) > 5 then 'moderate_growth'
        when round(((revenue - same_month_previous_year_revenue)::numeric / nullif(same_month_previous_year_revenue, 0) * 100), 2) > 0 then 'slow_growth'
        when round(((revenue - same_month_previous_year_revenue)::numeric / nullif(same_month_previous_year_revenue, 0) * 100), 2) > -5 then 'declining'
        else 'sharp_decline'
    end as growth_category,
    -- Seasonality detection (comparing current month to average)
    case
        when month_number in (5, 6, 7, 8) then 'peak_season'
        when month_number in (12, 1, 2) then 'low_season'
        else 'normal_season'
    end as seasonal_category
from
    trend_calculations
order by
    month desc;

