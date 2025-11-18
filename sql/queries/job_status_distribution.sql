-- Job Status Distribution
-- Count and percentage of jobs by status (QUOTED, BOOKED, LOST, CANCELLED, CLOSED)

with status_counts as (
    select
        opportunity_status,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue
    from
        jobs
    where
        is_duplicate = false
        and opportunity_status is not null
    group by
        opportunity_status
),
total_summary as (
    select
        sum(job_count) as total_jobs,
        sum(total_revenue) as total_revenue_all
    from
        status_counts
)
select
    sc.opportunity_status,
    sc.job_count,
    round(sc.job_count::numeric / nullif(ts.total_jobs, 0) * 100, 2) as percentage_of_total,
    sc.total_revenue,
    round(sc.total_revenue::numeric / nullif(ts.total_revenue_all, 0) * 100, 2) as revenue_percentage,
    round(sc.total_revenue / nullif(sc.job_count, 0), 2) as avg_value_per_job
from
    status_counts sc
cross join
    total_summary ts
order by
    sc.job_count desc;

