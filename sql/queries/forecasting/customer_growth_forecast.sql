-- Customer Growth Forecast
-- Predict customer acquisition and retention

with monthly_customer_metrics as (
    select
        date_trunc('month', j.job_date) as month,
        extract(year from j.job_date) as year,
        extract(month from j.job_date) as month_number,
        count(distinct j.customer_id) as new_customers,
        count(distinct j.id) as total_jobs,
        count(distinct case when j.job_date = c.first_job_date then j.customer_id end) as first_time_customers,
        count(distinct case when j.job_date > c.first_job_date then j.customer_id end) as repeat_customers
    from
        jobs j
    inner join (
        select
            customer_id,
            min(job_date) as first_job_date
        from
            jobs
        where
            is_duplicate = false
            and opportunity_status in ('BOOKED', 'CLOSED')
        group by
            customer_id
    ) c on j.customer_id = c.customer_id
    where
        j.is_duplicate = false
        and j.job_date is not null
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        date_trunc('month', j.job_date),
        extract(year from j.job_date),
        extract(month from j.job_date)
),
customer_trends as (
    select
        month,
        year,
        month_number,
        new_customers,
        total_jobs,
        first_time_customers,
        repeat_customers,
        -- Moving averages
        avg(new_customers) over (order by month rows between 2 preceding and current row) as three_month_ma_new,
        avg(new_customers) over (order by month rows between 5 preceding and current row) as six_month_ma_new,
        avg(new_customers) over (order by month rows between 11 preceding and current row) as twelve_month_ma_new,
        avg(repeat_customers) over (order by month rows between 2 preceding and current row) as three_month_ma_repeat,
        -- Year-over-year
        lag(new_customers, 12) over (order by month) as same_month_previous_year_new,
        lag(repeat_customers, 12) over (order by month) as same_month_previous_year_repeat,
        -- Growth rate
        (new_customers - lag(new_customers, 1) over (order by month))::numeric / nullif(lag(new_customers, 1) over (order by month), 0) * 100 as month_over_month_growth
    from
        monthly_customer_metrics
)
select
    month,
    year,
    month_number,
    new_customers as actual_new_customers,
    repeat_customers as actual_repeat_customers,
    total_jobs,
    first_time_customers,
    round(three_month_ma_new::numeric, 2) as three_month_ma_new_customers,
    round(six_month_ma_new::numeric, 2) as six_month_ma_new_customers,
    round(twelve_month_ma_new::numeric, 2) as twelve_month_ma_new_customers,
    round(three_month_ma_repeat::numeric, 2) as three_month_ma_repeat_customers,
    same_month_previous_year_new,
    same_month_previous_year_repeat,
    round(month_over_month_growth::numeric, 2) as mom_growth_percent,
    round((new_customers - same_month_previous_year_new)::numeric / nullif(same_month_previous_year_new, 0) * 100, 2) as yoy_growth_new_customers_percent,
    round((repeat_customers - same_month_previous_year_repeat)::numeric / nullif(same_month_previous_year_repeat, 0) * 100, 2) as yoy_growth_repeat_customers_percent,
    -- Forecasts
    round(twelve_month_ma_new::numeric, 2) as forecasted_new_customers,
    round(three_month_ma_repeat::numeric, 2) as forecasted_repeat_customers,
    round((twelve_month_ma_new * 0.9)::numeric, 2) as forecast_new_customers_lower,
    round((twelve_month_ma_new * 1.1)::numeric, 2) as forecast_new_customers_upper,
    case
        when month >= date_trunc('month', current_date) then 'forecast'
        else 'historical'
    end as data_type
from
    customer_trends
order by
    month desc;

