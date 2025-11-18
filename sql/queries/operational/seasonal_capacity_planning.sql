-- Seasonal Capacity Planning
-- Capacity needs by season/month for planning

with seasonal_metrics as (
    select
        extract(year from j.job_date) as year,
        extract(month from j.job_date) as month,
        extract(quarter from j.job_date) as quarter,
        case
            when extract(month from j.job_date) in (12, 1, 2) then 'winter'
            when extract(month from j.job_date) in (3, 4, 5) then 'spring'
            when extract(month from j.job_date) in (6, 7, 8) then 'summer'
            when extract(month from j.job_date) in (9, 10, 11) then 'fall'
        end as season,
        j.branch_name,
        j.job_type,
        count(*) as total_jobs,
        sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        count(distinct date_trunc('day', j.job_date)) as active_days,
        avg(coalesce(j.actual_number_crew, 0)) as avg_crew_per_job,
        avg(coalesce(j.actual_number_trucks, 0)) as avg_trucks_per_job
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.job_date is not null
    group by
        extract(year from j.job_date),
        extract(month from j.job_date),
        extract(quarter from j.job_date),
        case
            when extract(month from j.job_date) in (12, 1, 2) then 'winter'
            when extract(month from j.job_date) in (3, 4, 5) then 'spring'
            when extract(month from j.job_date) in (6, 7, 8) then 'summer'
            when extract(month from j.job_date) in (9, 10, 11) then 'fall'
        end,
        j.branch_name,
        j.job_type
),
seasonal_averages as (
    select
        season,
        branch_name,
        job_type,
        avg(total_jobs) as avg_jobs_per_period,
        avg(total_crew_hours) as avg_crew_hours_per_period,
        avg(total_truck_hours) as avg_truck_hours_per_period,
        avg(total_revenue) as avg_revenue_per_period,
        avg(active_days) as avg_active_days,
        avg(avg_crew_per_job) as avg_crew_per_job,
        avg(avg_trucks_per_job) as avg_trucks_per_job,
        max(total_jobs) as peak_jobs,
        max(total_crew_hours) as peak_crew_hours,
        max(total_truck_hours) as peak_truck_hours
    from
        seasonal_metrics
    group by
        season,
        branch_name,
        job_type
)
select
    season,
    branch_name,
    job_type,
    round(avg_jobs_per_period::numeric, 2) as avg_jobs_per_period,
    round(avg_crew_hours_per_period::numeric, 2) as avg_crew_hours_per_period,
    round(avg_truck_hours_per_period::numeric, 2) as avg_truck_hours_per_period,
    round(avg_revenue_per_period::numeric, 2) as avg_revenue_per_period,
    round(avg_active_days::numeric, 2) as avg_active_days,
    round(avg_crew_per_job::numeric, 2) as avg_crew_per_job,
    round(avg_trucks_per_job::numeric, 2) as avg_trucks_per_job,
    peak_jobs,
    peak_crew_hours,
    peak_truck_hours,
    round((peak_jobs / nullif(avg_jobs_per_period, 0))::numeric, 2) as peak_to_avg_ratio,
    round((peak_crew_hours / nullif(avg_crew_hours_per_period, 0))::numeric, 2) as peak_crew_ratio,
    round((peak_truck_hours / nullif(avg_truck_hours_per_period, 0))::numeric, 2) as peak_truck_ratio,
    -- Capacity planning recommendations
    case
        when peak_to_avg_ratio > 1.5 then 'high_variability'
        when peak_to_avg_ratio > 1.2 then 'moderate_variability'
        else 'stable'
    end as variability_level
from
    seasonal_averages
order by
    season,
    branch_name,
    avg_revenue_per_period desc;

