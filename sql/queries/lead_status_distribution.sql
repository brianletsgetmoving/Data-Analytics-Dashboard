-- Lead Status Distribution
-- Distribution of leads by status

with job_statuses as (
    select
        opportunity_status::text as status,
        'jobs' as source,
        count(*) as lead_count
    from
        jobs
    where
        is_duplicate = false
        and opportunity_status is not null
    group by
        opportunity_status
),
booked_statuses as (
    select
        status,
        'booked_opportunities' as source,
        count(*) as lead_count
    from
        booked_opportunities
    where
        status is not null
    group by
        status
),
lead_status_counts as (
    select
        status,
        'lead_status' as source,
        count(*) as lead_count
    from
        lead_status
    where
        status is not null
    group by
        status
)
select
    status,
    source,
    lead_count,
    round(lead_count::numeric / sum(lead_count) over (partition by source) * 100, 2) as percentage
from
    (
        select * from job_statuses
        union all
        select * from booked_statuses
        union all
        select * from lead_status_counts
    ) combined
order by
    source,
    lead_count desc;

