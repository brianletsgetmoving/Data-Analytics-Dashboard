-- Customer Acquisition Timeline
-- New customers acquired by month and year based on their first job date

with first_jobs as (
    select
        j.customer_id,
        min(j.job_date) as first_job_date
    from
        jobs j
    where
        j.is_duplicate = false
        and j.customer_id is not null
        and j.job_date is not null
    group by
        j.customer_id
),
acquisition_timeline as (
    select
        date_trunc('month', first_job_date) as acquisition_month,
        date_trunc('year', first_job_date) as acquisition_year,
        extract(year from first_job_date) as year,
        extract(month from first_job_date) as month,
        count(distinct customer_id) as new_customers
    from
        first_jobs
    group by
        date_trunc('month', first_job_date),
        date_trunc('year', first_job_date),
        extract(year from first_job_date),
        extract(month from first_job_date)
)
select
    acquisition_year,
    acquisition_month,
    year,
    month,
    new_customers,
    sum(new_customers) over (partition by year order by month) as cumulative_customers_year,
    sum(new_customers) over (order by acquisition_month) as cumulative_customers_total
from
    acquisition_timeline
order by
    acquisition_month desc;

