-- Daily Active Jobs
-- Daily job activity metrics

select
    date_trunc('day', job_date) as job_day,
    count(*) as daily_job_count,
    count(*) filter (where opportunity_status = 'QUOTED') as quoted_count,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
    count(*) filter (where opportunity_status = 'LOST') as lost_count,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as daily_revenue,
    count(distinct customer_id) as unique_customers,
    count(distinct branch_name) as active_branches,
    count(distinct sales_person_name) as active_sales_people
from
    jobs
where
    is_duplicate = false
    and job_date is not null
group by
    date_trunc('day', job_date)
order by
    job_day desc;

