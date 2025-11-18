-- Job Crew and Truck Utilization
-- Average crew size and trucks per job by type

select
    job_type,
    count(*) as job_count,
    avg(actual_number_crew) as avg_crew_size,
    min(actual_number_crew) as min_crew_size,
    max(actual_number_crew) as max_crew_size,
    percentile_cont(0.5) within group (order by actual_number_crew) as median_crew_size,
    avg(actual_number_trucks) as avg_trucks_used,
    min(actual_number_trucks) as min_trucks_used,
    max(actual_number_trucks) as max_trucks_used,
    percentile_cont(0.5) within group (order by actual_number_trucks) as median_trucks_used,
    sum(actual_number_crew) as total_crew_hours,
    sum(actual_number_trucks) as total_truck_hours
from
    jobs
where
    is_duplicate = false
    and job_type is not null
    and (actual_number_crew is not null or actual_number_trucks is not null)
group by
    job_type
order by
    job_count desc;

