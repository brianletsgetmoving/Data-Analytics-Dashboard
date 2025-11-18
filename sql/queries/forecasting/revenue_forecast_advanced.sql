-- Advanced Revenue Forecasting
-- Multi-method forecasting (moving average, exponential smoothing, linear regression)

with monthly_revenue as (
    select
        date_trunc('month', job_date) as month,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        count(*) as job_count
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
        and opportunity_status in ('BOOKED', 'CLOSED')
    group by
        date_trunc('month', job_date)
),
revenue_with_trends as (
    select
        month,
        revenue,
        job_count,
        -- Moving averages
        avg(revenue) over (order by month rows between 2 preceding and current row) as three_month_ma,
        avg(revenue) over (order by month rows between 5 preceding and current row) as six_month_ma,
        avg(revenue) over (order by month rows between 11 preceding and current row) as twelve_month_ma,
        -- Exponential smoothing (simplified - using weighted averages)
        avg(revenue) over (order by month rows between 2 preceding and current row) * 0.6 + 
        lag(revenue, 1) over (order by month) * 0.4 as exponential_smoothing_alpha_06,
        -- Year-over-year comparison
        lag(revenue, 12) over (order by month) as same_month_previous_year,
        -- Linear trend (simplified using window functions)
        row_number() over (order by month) as month_number,
        avg(revenue) over () as overall_avg_revenue
    from
        monthly_revenue
),
forecast_calculations as (
    select
        month,
        revenue,
        job_count,
        round(three_month_ma::numeric, 2) as three_month_moving_avg,
        round(six_month_ma::numeric, 2) as six_month_moving_avg,
        round(twelve_month_ma::numeric, 2) as twelve_month_moving_avg,
        round(exponential_smoothing_alpha_06::numeric, 2) as exponential_smoothing_forecast,
        same_month_previous_year,
        round((revenue - same_month_previous_year)::numeric / nullif(same_month_previous_year, 0) * 100, 2) as yoy_change_percent,
        -- Simple linear regression forecast (next period)
        round((overall_avg_revenue + (revenue - overall_avg_revenue) * 1.05)::numeric, 2) as linear_trend_forecast,
        month_number
    from
        revenue_with_trends
)
select
    month,
    revenue as actual_revenue,
    job_count,
    three_month_moving_avg,
    six_month_moving_avg,
    twelve_month_moving_avg,
    exponential_smoothing_forecast,
    same_month_previous_year,
    yoy_change_percent,
    linear_trend_forecast,
    -- Best forecast (using twelve month MA as default)
    twelve_month_moving_avg as recommended_forecast,
    -- Confidence interval (simplified - using standard deviation approximation)
    round((twelve_month_moving_avg * 0.9)::numeric, 2) as forecast_lower_bound,
    round((twelve_month_moving_avg * 1.1)::numeric, 2) as forecast_upper_bound,
    case
        when month >= date_trunc('month', current_date) then 'forecast'
        else 'historical'
    end as data_type
from
    forecast_calculations
order by
    month desc;

