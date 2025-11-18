-- Seasonal Job Patterns
-- Seasonal patterns in job bookings by month

with monthly_patterns as (
    select
        extract(month from job_date) as month_number,
        to_char(job_date, 'Month') as month_name,
        count(*) as total_jobs,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        extract(month from job_date),
        to_char(job_date, 'Month')
)
select
    month_number,
    trim(month_name) as month_name,
    total_jobs,
    booked_jobs,
    closed_jobs,
    total_revenue,
    round(total_jobs::numeric / (select sum(total_jobs) from monthly_patterns) * 100, 2) as percentage_of_year,
    round(avg(total_jobs) over (), 2) as overall_monthly_avg,
    round(total_jobs - avg(total_jobs) over (), 0) as deviation_from_avg
from
    monthly_patterns
order by
    month_number;

