-- Customer Job Frequency Analysis
-- Calculates average time between jobs per customer

with customer_jobs_ordered as (
    select
        j.customer_id,
        c.name as customer_name,
        j.job_date,
        row_number() over (partition by j.customer_id order by j.job_date) as job_sequence,
        lag(j.job_date) over (partition by j.customer_id order by j.job_date) as previous_job_date
    from
        jobs j
    inner join
        customers c on j.customer_id = c.id
    where
        j.is_duplicate = false
        and j.customer_id is not null
        and j.job_date is not null
),
job_intervals as (
    select
        customer_id,
        customer_name,
        job_date - previous_job_date as days_between_jobs
    from
        customer_jobs_ordered
    where
        previous_job_date is not null
),
customer_frequency_stats as (
    select
        customer_id,
        customer_name,
        count(*) as intervals_count,
        avg(extract(epoch from days_between_jobs) / 86400) as avg_days_between_jobs,
        min(extract(epoch from days_between_jobs) / 86400) as min_days_between_jobs,
        max(extract(epoch from days_between_jobs) / 86400) as max_days_between_jobs,
        percentile_cont(0.5) within group (order by extract(epoch from days_between_jobs) / 86400) as median_days_between_jobs
    from
        job_intervals
    group by
        customer_id, customer_name
)
select
    customer_id,
    customer_name,
    intervals_count,
    round(avg_days_between_jobs::numeric, 2) as avg_days_between_jobs,
    round(min_days_between_jobs::numeric, 0) as min_days_between_jobs,
    round(max_days_between_jobs::numeric, 0) as max_days_between_jobs,
    round(median_days_between_jobs::numeric, 2) as median_days_between_jobs,
    round(avg_days_between_jobs / 30, 2) as avg_months_between_jobs
from
    customer_frequency_stats
order by
    avg_days_between_jobs asc;

