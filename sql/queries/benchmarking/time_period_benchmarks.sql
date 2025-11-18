-- Time Period Benchmarks
-- Current period vs historical averages

with period_metrics as (
    select
        date_trunc('month', job_date) as period,
        extract(year from job_date) as year,
        extract(month from job_date) as month,
        count(*) as total_jobs,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
        count(*) filter (where opportunity_status = 'LOST') as lost_jobs
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
        and opportunity_status in ('BOOKED', 'CLOSED', 'LOST')
    group by
        date_trunc('month', job_date),
        extract(year from job_date),
        extract(month from job_date)
),
historical_averages as (
    select
        avg(total_jobs) as historical_avg_jobs,
        avg(total_revenue) as historical_avg_revenue,
        avg(avg_job_value) as historical_avg_job_value,
        avg((booked_jobs::numeric / nullif(total_jobs, 0) * 100)) as historical_avg_booking_rate,
        avg((closed_jobs::numeric / nullif(total_jobs, 0) * 100)) as historical_avg_closing_rate
    from
        period_metrics
    where
        period < date_trunc('month', current_date)
),
current_period as (
    select
        period,
        year,
        month,
        total_jobs,
        unique_customers,
        total_revenue,
        avg_job_value,
        booked_jobs,
        closed_jobs,
        lost_jobs,
        round((booked_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as booking_rate_percent,
        round((closed_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as closing_rate_percent,
        round((lost_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as loss_rate_percent
    from
        period_metrics
    where
        period >= date_trunc('month', current_date - interval '12 months')
)
select
    cp.period,
    cp.year,
    cp.month,
    cp.total_jobs,
    cp.unique_customers,
    round(cp.total_revenue::numeric, 2) as total_revenue,
    round(cp.avg_job_value::numeric, 2) as avg_job_value,
    cp.booked_jobs,
    cp.closed_jobs,
    cp.lost_jobs,
    cp.booking_rate_percent,
    cp.closing_rate_percent,
    cp.loss_rate_percent,
    -- Historical benchmarks
    round(ha.historical_avg_jobs::numeric, 2) as historical_avg_jobs,
    round(ha.historical_avg_revenue::numeric, 2) as historical_avg_revenue,
    round(ha.historical_avg_job_value::numeric, 2) as historical_avg_job_value,
    round(ha.historical_avg_booking_rate::numeric, 2) as historical_avg_booking_rate,
    round(ha.historical_avg_closing_rate::numeric, 2) as historical_avg_closing_rate,
    -- Performance vs historical
    round(((cp.total_jobs - ha.historical_avg_jobs) / nullif(ha.historical_avg_jobs, 0) * 100)::numeric, 2) as jobs_vs_historical_percent,
    round(((cp.total_revenue - ha.historical_avg_revenue) / nullif(ha.historical_avg_revenue, 0) * 100)::numeric, 2) as revenue_vs_historical_percent,
    round(((cp.avg_job_value - ha.historical_avg_job_value) / nullif(ha.historical_avg_job_value, 0) * 100)::numeric, 2) as job_value_vs_historical_percent,
    round((cp.booking_rate_percent - ha.historical_avg_booking_rate)::numeric, 2) as booking_rate_vs_historical,
    round((cp.closing_rate_percent - ha.historical_avg_closing_rate)::numeric, 2) as closing_rate_vs_historical,
    case
        when cp.total_revenue > ha.historical_avg_revenue * 1.1 then 'above_trend'
        when cp.total_revenue < ha.historical_avg_revenue * 0.9 then 'below_trend'
        else 'on_trend'
    end as trend_category
from
    current_period cp,
    historical_averages ha
order by
    cp.period desc;

