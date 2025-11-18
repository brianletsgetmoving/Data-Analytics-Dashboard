-- Job Type Distribution
-- Distribution of job types (Moving, Packing, etc.)

select
    job_type,
    count(*) as job_count,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
    round(count(*)::numeric / (select count(*) from jobs where is_duplicate = false) * 100, 2) as percentage_of_total,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    avg(actual_number_crew) as avg_crew_size,
    avg(actual_number_trucks) as avg_trucks_used
from
    jobs
where
    is_duplicate = false
    and job_type is not null
group by
    job_type
order by
    job_count desc;

