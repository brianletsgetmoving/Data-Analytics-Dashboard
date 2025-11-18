-- Revenue Forecast Trends
-- Revenue forecasting based on historical trends using moving averages

with monthly_revenue as (
    select
        date_trunc('month', job_date) as month,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('month', job_date)
),
revenue_with_trends as (
    select
        month,
        revenue,
        avg(revenue) over (order by month rows between 2 preceding and current row) as three_month_avg,
        avg(revenue) over (order by month rows between 5 preceding and current row) as six_month_avg,
        avg(revenue) over (order by month rows between 11 preceding and current row) as twelve_month_avg,
        lag(revenue, 12) over (order by month) as same_month_previous_year
    from
        monthly_revenue
)
select
    month,
    revenue,
    round(three_month_avg, 2) as three_month_moving_avg,
    round(six_month_avg, 2) as six_month_moving_avg,
    round(twelve_month_avg, 2) as twelve_month_moving_avg,
    same_month_previous_year,
    round((revenue - same_month_previous_year)::numeric / nullif(same_month_previous_year, 0) * 100, 2) as yoy_change_percent,
    round(twelve_month_avg, 2) as forecasted_revenue
from
    revenue_with_trends
order by
    month desc;

