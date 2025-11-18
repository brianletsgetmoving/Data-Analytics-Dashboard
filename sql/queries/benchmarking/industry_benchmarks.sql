-- Industry Benchmarks
-- Internal benchmarks (avg job value, conversion rates, etc.)

with overall_benchmarks as (
    select
        count(*) as total_jobs,
        count(distinct customer_id) as total_customers,
        count(distinct branch_name) as total_branches,
        count(distinct sales_person_name) as total_sales_people,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(total_actual_cost, total_estimated_cost, 0)) as median_job_value,
        percentile_cont(0.25) within group (order by coalesce(total_actual_cost, total_estimated_cost, 0)) as p25_job_value,
        percentile_cont(0.75) within group (order by coalesce(total_actual_cost, total_estimated_cost, 0)) as p75_job_value,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
        count(*) filter (where opportunity_status = 'LOST') as lost_jobs,
        count(*) filter (where opportunity_status = 'QUOTED') as quoted_jobs,
        avg(coalesce(actual_number_crew, 0)) as avg_crew_size,
        avg(coalesce(actual_number_trucks, 0)) as avg_trucks_per_job
    from
        jobs
    where
        is_duplicate = false
        and opportunity_status in ('BOOKED', 'CLOSED', 'LOST', 'QUOTED')
)
select
    'overall' as benchmark_category,
    total_jobs,
    total_customers,
    total_branches,
    total_sales_people,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value,
    round(p25_job_value::numeric, 2) as p25_job_value,
    round(p75_job_value::numeric, 2) as p75_job_value,
    booked_jobs,
    closed_jobs,
    lost_jobs,
    quoted_jobs,
    round((booked_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as booking_rate_percent,
    round((closed_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as closing_rate_percent,
    round((lost_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as loss_rate_percent,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job,
    round((total_revenue / nullif(total_customers, 0))::numeric, 2) as revenue_per_customer,
    round(avg_crew_size::numeric, 2) as avg_crew_size,
    round(avg_trucks_per_job::numeric, 2) as avg_trucks_per_job
from
    overall_benchmarks;

