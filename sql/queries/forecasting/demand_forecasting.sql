-- Demand Forecasting
-- Demand forecasting by region, job type

with monthly_demand as (
    select
        date_trunc('month', job_date) as month,
        extract(year from job_date) as year,
        extract(month from job_date) as month_number,
        origin_city,
        origin_state,
        job_type,
        branch_name,
        count(*) as demand_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as demand_revenue
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
        origin_city,
        origin_state,
        job_type,
        branch_name
),
demand_trends as (
    select
        month,
        year,
        month_number,
        origin_city,
        origin_state,
        job_type,
        branch_name,
        demand_count,
        round(demand_revenue::numeric, 2) as demand_revenue,
        -- Moving averages
        avg(demand_count) over (partition by origin_city, origin_state, job_type, branch_name order by month rows between 2 preceding and current row) as three_month_ma,
        avg(demand_count) over (partition by origin_city, origin_state, job_type, branch_name order by month rows between 5 preceding and current row) as six_month_ma,
        avg(demand_count) over (partition by origin_city, origin_state, job_type, branch_name order by month rows between 11 preceding and current row) as twelve_month_ma,
        -- Seasonal average
        avg(demand_count) over (partition by origin_city, origin_state, job_type, branch_name, month_number) as seasonal_avg,
        -- Year-over-year
        lag(demand_count, 12) over (partition by origin_city, origin_state, job_type, branch_name order by month) as same_month_previous_year
    from
        monthly_demand
)
select
    month,
    year,
    month_number,
    origin_city,
    origin_state,
    job_type,
    branch_name,
    demand_count as actual_demand,
    demand_revenue,
    round(three_month_ma::numeric, 2) as three_month_moving_avg,
    round(six_month_ma::numeric, 2) as six_month_moving_avg,
    round(twelve_month_ma::numeric, 2) as twelve_month_moving_avg,
    round(seasonal_avg::numeric, 2) as seasonal_average,
    same_month_previous_year,
    round((demand_count - same_month_previous_year)::numeric / nullif(same_month_previous_year, 0) * 100, 2) as yoy_change_percent,
    -- Forecast (prefer seasonal average, fallback to twelve month MA)
    coalesce(round(seasonal_avg::numeric, 2), round(twelve_month_ma::numeric, 2)) as forecasted_demand,
    round((coalesce(seasonal_avg, twelve_month_ma) * 0.85)::numeric, 2) as forecast_lower_bound,
    round((coalesce(seasonal_avg, twelve_month_ma) * 1.15)::numeric, 2) as forecast_upper_bound,
    case
        when month >= date_trunc('month', current_date) then 'forecast'
        else 'historical'
    end as data_type
from
    demand_trends
order by
    month desc,
    origin_city,
    origin_state,
    job_type,
    branch_name;

