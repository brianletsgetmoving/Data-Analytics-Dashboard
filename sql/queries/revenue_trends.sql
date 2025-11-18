-- Revenue Trends
-- Revenue trends by month, quarter, and year

with monthly_revenue as (
    select
        date_trunc('month', job_date) as period,
        'monthly' as period_type,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
        lag(sum(coalesce(total_actual_cost, total_estimated_cost, 0))) over (order by date_trunc('month', job_date)) as previous_period_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('month', job_date)
),
quarterly_revenue as (
    select
        date_trunc('quarter', job_date) as period,
        'quarterly' as period_type,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
        lag(sum(coalesce(total_actual_cost, total_estimated_cost, 0))) over (order by date_trunc('quarter', job_date)) as previous_period_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('quarter', job_date)
),
yearly_revenue as (
    select
        date_trunc('year', job_date) as period,
        'yearly' as period_type,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
        lag(sum(coalesce(total_actual_cost, total_estimated_cost, 0))) over (order by date_trunc('year', job_date)) as previous_period_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('year', job_date)
)
select
    period_type,
    period,
    job_count,
    revenue,
    booked_revenue,
    closed_revenue,
    previous_period_revenue,
    round((revenue - previous_period_revenue)::numeric / nullif(previous_period_revenue, 0) * 100, 2) as period_over_period_change_percent
from
    monthly_revenue
union all
select
    period_type,
    period,
    job_count,
    revenue,
    booked_revenue,
    closed_revenue,
    previous_period_revenue,
    round((revenue - previous_period_revenue)::numeric / nullif(previous_period_revenue, 0) * 100, 2) as period_over_period_change_percent
from
    quarterly_revenue
union all
select
    period_type,
    period,
    job_count,
    revenue,
    booked_revenue,
    closed_revenue,
    previous_period_revenue,
    round((revenue - previous_period_revenue)::numeric / nullif(previous_period_revenue, 0) * 100, 2) as period_over_period_change_percent
from
    yearly_revenue
order by
    period_type,
    period desc;

