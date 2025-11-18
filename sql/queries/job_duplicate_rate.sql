-- Job Duplicate Rate
-- Duplicate job detection and rates

with duplicate_summary as (
    select
        count(*) filter (where is_duplicate = true) as duplicate_jobs,
        count(*) filter (where is_duplicate = false) as non_duplicate_jobs,
        count(*) as total_jobs
    from
        jobs
)
select
    duplicate_jobs,
    non_duplicate_jobs,
    total_jobs,
    round(duplicate_jobs::numeric / nullif(total_jobs, 0) * 100, 2) as duplicate_rate_percent,
    round(non_duplicate_jobs::numeric / nullif(total_jobs, 0) * 100, 2) as non_duplicate_rate_percent
from
    duplicate_summary;

