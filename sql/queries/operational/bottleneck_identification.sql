-- Bottleneck Identification
-- Identify slow-moving jobs, status transitions, and operational bottlenecks

with job_status_transitions as (
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
        -- Time in each stage
        case
            when j.created_at_utc is not null and j.booked_at_utc is not null then
                extract(epoch from (j.booked_at_utc - j.created_at_utc)) / 3600
            else null
        end as hours_in_quoted_stage,
        case
            when j.booked_at_utc is not null and j.job_date is not null then
                extract(epoch from (j.job_date - j.booked_at_utc)) / 24
            else null
        end as days_in_booked_stage,
        current_timestamp - j.created_at_utc as total_age
    from
        jobs j
    where
        j.is_duplicate = false
),
bottleneck_analysis as (
    select
        job_type,
        branch_name,
        opportunity_status,
        count(*) as job_count,
        round(avg(hours_in_quoted_stage)::numeric, 2) as avg_hours_quoted,
        percentile_cont(0.75) within group (order by hours_in_quoted_stage) as p75_hours_quoted,
        percentile_cont(0.95) within group (order by hours_in_quoted_stage) as p95_hours_quoted,
        round(avg(days_in_booked_stage)::numeric, 2) as avg_days_booked,
        percentile_cont(0.75) within group (order by days_in_booked_stage) as p75_days_booked,
        percentile_cont(0.95) within group (order by days_in_booked_stage) as p95_days_booked,
        count(*) filter (where hours_in_quoted_stage > 48) as jobs_stuck_in_quoted,
        count(*) filter (where days_in_booked_stage > 30) as jobs_stuck_in_booked,
        count(*) filter (where opportunity_status = 'QUOTED' and total_age > interval '7 days') as quoted_over_7_days,
        count(*) filter (where opportunity_status = 'BOOKED' and total_age > interval '30 days') as booked_over_30_days
    from
        job_status_transitions
    group by
        job_type,
        branch_name,
        opportunity_status
)
select
    job_type,
    branch_name,
    opportunity_status,
    job_count,
    avg_hours_quoted,
    p75_hours_quoted,
    p95_hours_quoted,
    avg_days_booked,
    p75_days_booked,
    p95_days_booked,
    jobs_stuck_in_quoted,
    jobs_stuck_in_booked,
    quoted_over_7_days,
    booked_over_30_days,
    round((jobs_stuck_in_quoted::numeric / nullif(job_count, 0) * 100), 2) as stuck_quoted_percent,
    round((jobs_stuck_in_booked::numeric / nullif(job_count, 0) * 100), 2) as stuck_booked_percent,
    case
        when jobs_stuck_in_quoted > 0 or jobs_stuck_in_booked > 0 then 'bottleneck_detected'
        else 'normal'
    end as bottleneck_status
from
    bottleneck_analysis
where
    job_count > 0
order by
    jobs_stuck_in_quoted desc,
    jobs_stuck_in_booked desc,
    job_count desc;

