-- Quarterly Metrics Summary
-- Quarterly summary of key metrics

select
    date_trunc('quarter', job_date) as quarter,
    extract(year from job_date) as year,
    extract(quarter from job_date) as quarter_number,
    count(*) as total_jobs,
    count(*) filter (where opportunity_status = 'QUOTED') as quoted_jobs,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    count(*) filter (where opportunity_status = 'LOST') as lost_jobs,
    count(*) filter (where opportunity_status = 'CANCELLED') as cancelled_jobs,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    count(distinct customer_id) as unique_customers,
    count(distinct branch_name) as active_branches,
    count(distinct sales_person_name) as active_sales_people,
    round(count(*) filter (where opportunity_status = 'BOOKED')::numeric / nullif(count(*), 0) * 100, 2) as booking_rate_percent
from
    jobs
where
    is_duplicate = false
    and job_date is not null
group by
    date_trunc('quarter', job_date),
    extract(year from job_date),
    extract(quarter from job_date)
order by
    quarter desc;

