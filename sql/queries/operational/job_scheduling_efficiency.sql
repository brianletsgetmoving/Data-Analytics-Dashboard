-- Job Scheduling Efficiency
-- Booking to completion time analysis

with scheduling_metrics as (
    select
        j.id,
        j.job_id,
        j.job_type,
        j.branch_name,
        j.opportunity_status,
        j.created_at_utc,
        j.booked_at_utc,
        j.job_date,
        j.total_estimated_cost,
        j.total_actual_cost,
        -- Time metrics
        case
            when j.created_at_utc is not null and j.booked_at_utc is not null then
                extract(epoch from (j.booked_at_utc - j.created_at_utc)) / 3600
            else null
        end as hours_quote_to_book,
        case
            when j.booked_at_utc is not null and j.job_date is not null then
                extract(epoch from (j.job_date - j.booked_at_utc)) / 24
            else null
        end as days_book_to_job,
        case
            when j.created_at_utc is not null and j.job_date is not null then
                extract(epoch from (j.job_date - j.created_at_utc)) / 24
            else null
        end as days_total_cycle
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
    round(avg(hours_quote_to_book)::numeric, 2) as avg_hours_quote_to_book,
    percentile_cont(0.5) within group (order by hours_quote_to_book) as median_hours_quote_to_book,
    percentile_cont(0.75) within group (order by hours_quote_to_book) as p75_hours_quote_to_book,
    round(avg(days_book_to_job)::numeric, 2) as avg_days_book_to_job,
    percentile_cont(0.5) within group (order by days_book_to_job) as median_days_book_to_job,
    percentile_cont(0.75) within group (order by days_book_to_job) as p75_days_book_to_job,
    round(avg(days_total_cycle)::numeric, 2) as avg_days_total_cycle,
    percentile_cont(0.5) within group (order by days_total_cycle) as median_days_total_cycle,
    -- Efficiency metrics
    count(*) filter (where hours_quote_to_book <= 24) as booked_within_24h,
    count(*) filter (where hours_quote_to_book <= 48) as booked_within_48h,
    count(*) filter (where days_book_to_job <= 7) as scheduled_within_7_days,
    count(*) filter (where days_book_to_job <= 14) as scheduled_within_14_days,
    count(*) filter (where days_total_cycle <= 14) as completed_within_14_days,
    round((count(*) filter (where hours_quote_to_book <= 24)::numeric / nullif(count(*), 0) * 100), 2) as booking_within_24h_percent,
    round((count(*) filter (where days_book_to_job <= 7)::numeric / nullif(count(*), 0) * 100), 2) as scheduling_within_7_days_percent,
    round((count(*) filter (where days_total_cycle <= 14)::numeric / nullif(count(*), 0) * 100), 2) as completion_within_14_days_percent,
    -- Average job values
    round(avg(coalesce(total_actual_cost, total_estimated_cost, 0))::numeric, 2) as avg_job_value
from
    scheduling_metrics
where
    job_type is not null
group by
    job_type,
    branch_name
having
    count(*) > 0
order by
    total_jobs desc,
    avg_hours_quote_to_book;

