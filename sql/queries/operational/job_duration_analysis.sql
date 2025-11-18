-- Job Duration Analysis
-- Average job duration by type, location, and other factors

with job_duration_calc as (
    select
        j.id,
        j.job_id,
        j.job_type,
        j.branch_name,
        j.origin_city,
        j.destination_city,
        j.opportunity_status,
        j.created_at_utc,
        j.booked_at_utc,
        j.job_date,
        j.total_actual_cost,
        j.total_estimated_cost,
        -- Calculate time from creation to booking
        case
            when j.created_at_utc is not null and j.booked_at_utc is not null then
                extract(epoch from (j.booked_at_utc - j.created_at_utc)) / 3600
            else null
        end as hours_to_book,
        -- Calculate time from booking to job date
        case
            when j.booked_at_utc is not null and j.job_date is not null then
                extract(epoch from (j.job_date - j.booked_at_utc)) / 24
            else null
        end as days_booking_to_job,
        coalesce(j.actual_number_crew, 0) as crew_size,
        coalesce(j.actual_number_trucks, 0) as trucks_used
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
)
select
    job_type,
    branch_name,
    count(*) as total_jobs,
    round(avg(hours_to_book)::numeric, 2) as avg_hours_to_book,
    percentile_cont(0.5) within group (order by hours_to_book) as median_hours_to_book,
    round(avg(days_booking_to_job)::numeric, 2) as avg_days_booking_to_job,
    percentile_cont(0.5) within group (order by days_booking_to_job) as median_days_booking_to_job,
    round(avg(crew_size)::numeric, 2) as avg_crew_size,
    round(avg(trucks_used)::numeric, 2) as avg_trucks_used,
    round(avg(coalesce(total_actual_cost, total_estimated_cost, 0))::numeric, 2) as avg_job_value,
    count(*) filter (where hours_to_book <= 24) as booked_within_24h,
    count(*) filter (where hours_to_book <= 48) as booked_within_48h,
    count(*) filter (where days_booking_to_job <= 7) as jobs_within_7_days,
    count(*) filter (where days_booking_to_job <= 14) as jobs_within_14_days,
    round((count(*) filter (where hours_to_book <= 24)::numeric / nullif(count(*), 0) * 100), 2) as booking_within_24h_percent,
    round((count(*) filter (where days_booking_to_job <= 7)::numeric / nullif(count(*), 0) * 100), 2) as jobs_within_7_days_percent
from
    job_duration_calc
where
    job_type is not null
group by
    job_type,
    branch_name
having
    count(*) > 0
order by
    total_jobs desc,
    avg_hours_to_book;

