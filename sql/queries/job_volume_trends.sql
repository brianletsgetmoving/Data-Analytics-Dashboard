-- Job Volume Trends
-- Job volume trends over time (monthly and yearly)

with monthly_trends as (
    select
        date_trunc('month', job_date) as month,
        extract(year from job_date) as year,
        extract(month from job_date) as month_number,
        count(*) as job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        lag(count(*)) over (order by date_trunc('month', job_date)) as previous_month_jobs,
        lag(sum(coalesce(total_actual_cost, total_estimated_cost, 0))) over (order by date_trunc('month', job_date)) as previous_month_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('month', job_date),
        extract(year from job_date),
        extract(month from job_date)
),
yearly_trends as (
    select
        date_trunc('year', job_date) as year,
        extract(year from job_date) as year_number,
        count(*) as job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        lag(count(*)) over (order by date_trunc('year', job_date)) as previous_year_jobs,
        lag(sum(coalesce(total_actual_cost, total_estimated_cost, 0))) over (order by date_trunc('year', job_date)) as previous_year_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('year', job_date),
        extract(year from job_date)
)
select
    'monthly' as trend_type,
    month as period,
    year,
    month_number,
    job_count,
    booked_count,
    closed_count,
    revenue,
    previous_month_jobs,
    round((job_count - previous_month_jobs)::numeric / nullif(previous_month_jobs, 0) * 100, 2) as month_over_month_change_percent,
    round((revenue - previous_month_revenue)::numeric / nullif(previous_month_revenue, 0) * 100, 2) as revenue_mom_change_percent
from
    monthly_trends
union all
select
    'yearly' as trend_type,
    year as period,
    year_number as year,
    null as month_number,
    job_count,
    booked_count,
    closed_count,
    revenue,
    previous_year_jobs,
    round((job_count - previous_year_jobs)::numeric / nullif(previous_year_jobs, 0) * 100, 2) as year_over_year_change_percent,
    round((revenue - previous_year_revenue)::numeric / nullif(previous_year_revenue, 0) * 100, 2) as revenue_yoy_change_percent
from
    yearly_trends
order by
    trend_type,
    period desc;

