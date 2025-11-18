-- Branch Performance Benchmarking
-- Branch-to-branch comparisons with industry averages

with branch_metrics as (
    select
        branch_name,
        count(*) as total_jobs,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
        count(*) filter (where opportunity_status = 'LOST') as lost_jobs,
        avg(coalesce(actual_number_crew, 0)) as avg_crew_size,
        avg(coalesce(actual_number_trucks, 0)) as avg_trucks_per_job
    from
        jobs
    where
        is_duplicate = false
        and branch_name is not null
        and opportunity_status in ('BOOKED', 'CLOSED', 'LOST')
    group by
        branch_name
),
industry_averages as (
    select
        avg(total_jobs) as industry_avg_jobs,
        avg(total_revenue) as industry_avg_revenue,
        avg(avg_job_value) as industry_avg_job_value,
        avg((booked_jobs::numeric / nullif(total_jobs, 0) * 100)) as industry_avg_booking_rate,
        avg((closed_jobs::numeric / nullif(total_jobs, 0) * 100)) as industry_avg_closing_rate,
        avg(avg_crew_size) as industry_avg_crew_size,
        avg(avg_trucks_per_job) as industry_avg_trucks
    from
        branch_metrics
)
select
    bm.branch_name,
    bm.total_jobs,
    bm.unique_customers,
    round(bm.total_revenue::numeric, 2) as total_revenue,
    round(bm.avg_job_value::numeric, 2) as avg_job_value,
    bm.booked_jobs,
    bm.closed_jobs,
    bm.lost_jobs,
    round((bm.booked_jobs::numeric / nullif(bm.total_jobs, 0) * 100), 2) as booking_rate_percent,
    round((bm.closed_jobs::numeric / nullif(bm.total_jobs, 0) * 100), 2) as closing_rate_percent,
    round((bm.lost_jobs::numeric / nullif(bm.total_jobs, 0) * 100), 2) as loss_rate_percent,
    round(bm.avg_crew_size::numeric, 2) as avg_crew_size,
    round(bm.avg_trucks_per_job::numeric, 2) as avg_trucks_per_job,
    -- Industry benchmarks
    round(ia.industry_avg_jobs::numeric, 2) as industry_avg_jobs,
    round(ia.industry_avg_revenue::numeric, 2) as industry_avg_revenue,
    round(ia.industry_avg_job_value::numeric, 2) as industry_avg_job_value,
    round(ia.industry_avg_booking_rate::numeric, 2) as industry_avg_booking_rate,
    round(ia.industry_avg_closing_rate::numeric, 2) as industry_avg_closing_rate,
    -- Performance vs industry
    round(((bm.total_jobs - ia.industry_avg_jobs) / nullif(ia.industry_avg_jobs, 0) * 100)::numeric, 2) as jobs_vs_industry_percent,
    round(((bm.total_revenue - ia.industry_avg_revenue) / nullif(ia.industry_avg_revenue, 0) * 100)::numeric, 2) as revenue_vs_industry_percent,
    round(((bm.avg_job_value - ia.industry_avg_job_value) / nullif(ia.industry_avg_job_value, 0) * 100)::numeric, 2) as job_value_vs_industry_percent,
    round(((bm.booked_jobs::numeric / nullif(bm.total_jobs, 0) * 100) - ia.industry_avg_booking_rate)::numeric, 2) as booking_rate_vs_industry,
    case
        when bm.total_revenue > ia.industry_avg_revenue * 1.1 then 'above_average'
        when bm.total_revenue < ia.industry_avg_revenue * 0.9 then 'below_average'
        else 'average'
    end as performance_category
from
    branch_metrics bm,
    industry_averages ia
order by
    bm.total_revenue desc;

