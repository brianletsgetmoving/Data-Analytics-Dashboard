-- Jobs by Time Period
-- Job counts by day, week, month, and year with trends

with daily_jobs as (
    select
        date_trunc('day', job_date) as job_day,
        count(*) as daily_job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as daily_booked,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as daily_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('day', job_date)
),
weekly_jobs as (
    select
        date_trunc('week', job_date) as job_week,
        count(*) as weekly_job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as weekly_booked,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as weekly_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('week', job_date)
),
monthly_jobs as (
    select
        date_trunc('month', job_date) as job_month,
        count(*) as monthly_job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as monthly_booked,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as monthly_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('month', job_date)
),
yearly_jobs as (
    select
        date_trunc('year', job_date) as job_year,
        count(*) as yearly_job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as yearly_booked,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as yearly_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        date_trunc('year', job_date)
)
select
    'daily' as period_type,
    job_day as period_date,
    daily_job_count as job_count,
    daily_booked as booked_count,
    daily_revenue as revenue
from
    daily_jobs
union all
select
    'weekly' as period_type,
    job_week as period_date,
    weekly_job_count as job_count,
    weekly_booked as booked_count,
    weekly_revenue as revenue
from
    weekly_jobs
union all
select
    'monthly' as period_type,
    job_month as period_date,
    monthly_job_count as job_count,
    monthly_booked as booked_count,
    monthly_revenue as revenue
from
    monthly_jobs
union all
select
    'yearly' as period_type,
    job_year as period_date,
    yearly_job_count as job_count,
    yearly_booked as booked_count,
    yearly_revenue as revenue
from
    yearly_jobs
order by
    period_type,
    period_date desc;

