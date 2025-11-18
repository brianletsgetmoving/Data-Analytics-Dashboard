-- 6-month rolling window job counting using window functions

with job_windows as (
    select
        customer_id,
        job_date,
        min(job_date) over (partition by customer_id) as first_job_date,
        case
            when job_date < min(job_date) over (partition by customer_id) + interval '6 months'
            then 1
            when job_date < min(job_date) over (partition by customer_id) + interval '12 months'
            then 2
            when job_date < min(job_date) over (partition by customer_id) + interval '18 months'
            then 3
            when job_date < min(job_date) over (partition by customer_id) + interval '24 months'
            then 4
            else 5
        end as window_number
    from
        jobs
    where
        is_duplicate = false
)
select
    customer_id,
    max(window_number) as total_job_count_windows,
    count(*) as total_jobs_overall,
    count(*) filter (where window_number = 1) as window_1_jobs,
    count(*) filter (where window_number = 2) as window_2_jobs,
    count(*) filter (where window_number = 3) as window_3_jobs,
    count(*) filter (where window_number = 4) as window_4_jobs,
    count(*) filter (where window_number = 5) as window_5_jobs
from
    job_windows
group by
    customer_id
order by
    total_job_count_windows desc;

