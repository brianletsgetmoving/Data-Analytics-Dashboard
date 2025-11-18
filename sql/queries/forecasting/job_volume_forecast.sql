-- Job Volume Forecast
-- Forecast job volumes by type, branch, and season

with monthly_job_volumes as (
    select
        date_trunc('month', job_date) as month,
        extract(year from job_date) as year,
        extract(month from job_date) as month_number,
        job_type,
        branch_name,
        count(*) as job_count,
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
        job_type,
        branch_name
),
volume_trends as (
    select
        month,
        year,
        month_number,
        job_type,
        branch_name,
        job_count,
        unique_customers,
        -- Moving averages
        avg(job_count) over (partition by job_type, branch_name order by month rows between 2 preceding and current row) as three_month_ma,
        avg(job_count) over (partition by job_type, branch_name order by month rows between 5 preceding and current row) as six_month_ma,
        avg(job_count) over (partition by job_type, branch_name order by month rows between 11 preceding and current row) as twelve_month_ma,
        -- Year-over-year
        lag(job_count, 12) over (partition by job_type, branch_name order by month) as same_month_previous_year,
        -- Seasonal average (same month across all years)
        avg(job_count) over (partition by job_type, branch_name, month_number) as seasonal_avg
    from
        monthly_job_volumes
)
select
    month,
    year,
    month_number,
    job_type,
    branch_name,
    job_count as actual_job_count,
    unique_customers,
    round(three_month_ma::numeric, 2) as three_month_moving_avg,
    round(six_month_ma::numeric, 2) as six_month_moving_avg,
    round(twelve_month_ma::numeric, 2) as twelve_month_moving_avg,
    same_month_previous_year,
    round(seasonal_avg::numeric, 2) as seasonal_average,
    round((job_count - same_month_previous_year)::numeric / nullif(same_month_previous_year, 0) * 100, 2) as yoy_change_percent,
    -- Forecast (using seasonal average if available, otherwise twelve month MA)
    coalesce(round(seasonal_avg::numeric, 2), round(twelve_month_ma::numeric, 2)) as forecasted_job_count,
    round((coalesce(seasonal_avg, twelve_month_ma) * 0.9)::numeric, 2) as forecast_lower_bound,
    round((coalesce(seasonal_avg, twelve_month_ma) * 1.1)::numeric, 2) as forecast_upper_bound,
    case
        when month >= date_trunc('month', current_date) then 'forecast'
        else 'historical'
    end as data_type
from
    volume_trends
order by
    month desc,
    job_type,
    branch_name;

