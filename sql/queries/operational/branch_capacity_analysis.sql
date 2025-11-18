-- Branch Capacity Analysis
-- Branch capacity vs demand analysis

with branch_demand as (
    select
        b.id as branch_id,
        b.name as branch_name,
        b.city as branch_city,
        b.state as branch_state,
        date_trunc('month', j.job_date) as month,
        count(distinct j.id) as job_count,
        count(distinct j.customer_id) as customer_count,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        count(distinct date_trunc('day', j.job_date)) as active_days
    from
        branches b
    inner join
        jobs j on b.id = j.branch_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.job_date is not null
    group by
        b.id,
        b.name,
        b.city,
        b.state,
        date_trunc('month', j.job_date)
),
branch_capacity_metrics as (
    select
        branch_id,
        branch_name,
        branch_city,
        branch_state,
        count(distinct month) as months_active,
        sum(job_count) as total_jobs,
        sum(customer_count) as total_customers,
        sum(total_crew_hours) as total_crew_hours,
        sum(total_truck_hours) as total_truck_hours,
        sum(total_revenue) as total_revenue,
        sum(active_days) as total_active_days,
        round(avg(job_count)::numeric, 2) as avg_jobs_per_month,
        round(avg(total_crew_hours)::numeric, 2) as avg_crew_hours_per_month,
        round(avg(total_truck_hours)::numeric, 2) as avg_truck_hours_per_month,
        round(max(job_count)::numeric, 0) as peak_jobs_per_month,
        round(max(total_crew_hours)::numeric, 2) as peak_crew_hours_per_month
    from
        branch_demand
    group by
        branch_id,
        branch_name,
        branch_city,
        branch_state
)
select
    branch_name,
    branch_city,
    branch_state,
    months_active,
    total_jobs,
    total_customers,
    total_crew_hours,
    total_truck_hours,
    round(total_revenue::numeric, 2) as total_revenue,
    total_active_days,
    avg_jobs_per_month,
    avg_crew_hours_per_month,
    avg_truck_hours_per_month,
    peak_jobs_per_month,
    peak_crew_hours_per_month,
    round((total_jobs::numeric / nullif(total_active_days, 0)), 2) as jobs_per_day,
    round((total_crew_hours::numeric / nullif(total_active_days, 0)), 2) as crew_hours_per_day,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job,
    round((total_revenue / nullif(total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
    case
        when peak_jobs_per_month > avg_jobs_per_month * 1.5 then 'high_variance'
        when peak_jobs_per_month > avg_jobs_per_month * 1.2 then 'moderate_variance'
        else 'stable'
    end as demand_variance
from
    branch_capacity_metrics
order by
    total_revenue desc;

