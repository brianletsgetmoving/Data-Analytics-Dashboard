-- Operational Efficiency
-- Crew and truck utilization and efficiency metrics

select
    job_type,
    count(*) as total_jobs,
    avg(actual_number_crew) as avg_crew_size,
    avg(actual_number_trucks) as avg_trucks_per_job,
    sum(actual_number_crew) as total_crew_hours,
    sum(actual_number_trucks) as total_truck_hours,
    avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value,
    round(avg(coalesce(total_actual_cost, total_estimated_cost, 0)) / nullif(avg(actual_number_crew), 0), 2) as revenue_per_crew_member,
    round(avg(coalesce(total_actual_cost, total_estimated_cost, 0)) / nullif(avg(actual_number_trucks), 0), 2) as revenue_per_truck,
    count(*) filter (where actual_number_crew is not null) as jobs_with_crew_data,
    count(*) filter (where actual_number_trucks is not null) as jobs_with_truck_data
from
    jobs
where
    is_duplicate = false
    and job_type is not null
group by
    job_type
order by
    total_jobs desc;

