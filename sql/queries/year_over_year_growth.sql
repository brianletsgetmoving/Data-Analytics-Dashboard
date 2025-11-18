-- Year Over Year Growth
-- Year-over-year growth in jobs, revenue, and customers

with yearly_metrics as (
    select
        extract(year from job_date) as year,
        count(*) as job_count,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        count(distinct customer_id) as unique_customers,
        count(distinct branch_name) as active_branches
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
    group by
        extract(year from job_date)
),
growth_metrics as (
    select
        year,
        job_count,
        booked_jobs,
        closed_jobs,
        total_revenue,
        unique_customers,
        active_branches,
        lag(job_count) over (order by year) as previous_year_jobs,
        lag(total_revenue) over (order by year) as previous_year_revenue,
        lag(unique_customers) over (order by year) as previous_year_customers
    from
        yearly_metrics
)
select
    year,
    job_count,
    booked_jobs,
    closed_jobs,
    total_revenue,
    unique_customers,
    active_branches,
    previous_year_jobs,
    previous_year_revenue,
    previous_year_customers,
    round((job_count - previous_year_jobs)::numeric / nullif(previous_year_jobs, 0) * 100, 2) as job_growth_percent,
    round((total_revenue - previous_year_revenue)::numeric / nullif(previous_year_revenue, 0) * 100, 2) as revenue_growth_percent,
    round((unique_customers - previous_year_customers)::numeric / nullif(previous_year_customers, 0) * 100, 2) as customer_growth_percent
from
    growth_metrics
order by
    year desc;

