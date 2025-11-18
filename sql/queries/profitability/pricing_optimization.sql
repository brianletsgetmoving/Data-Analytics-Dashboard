-- Pricing Optimization Analysis
-- Analysis of quoted vs actual pricing to identify optimization opportunities

with pricing_analysis as (
    select
        j.job_type,
        j.branch_name,
        count(*) as total_jobs,
        avg(j.hourly_rate_quoted) as avg_hourly_rate_quoted,
        avg(j.hourly_rate_billed) as avg_hourly_rate_billed,
        avg(coalesce(j.total_estimated_cost, 0)) as avg_estimated_cost,
        avg(coalesce(j.total_actual_cost, 0)) as avg_actual_cost,
        percentile_cont(0.25) within group (order by j.hourly_rate_quoted) as p25_hourly_quoted,
        percentile_cont(0.5) within group (order by j.hourly_rate_quoted) as median_hourly_quoted,
        percentile_cont(0.75) within group (order by j.hourly_rate_quoted) as p75_hourly_quoted,
        percentile_cont(0.25) within group (order by j.hourly_rate_billed) as p25_hourly_billed,
        percentile_cont(0.5) within group (order by j.hourly_rate_billed) as median_hourly_billed,
        percentile_cont(0.75) within group (order by j.hourly_rate_billed) as p75_hourly_billed,
        count(*) filter (where j.hourly_rate_billed > j.hourly_rate_quoted) as jobs_over_quoted_rate,
        count(*) filter (where j.hourly_rate_billed < j.hourly_rate_quoted) as jobs_under_quoted_rate,
        count(*) filter (where j.total_actual_cost > j.total_estimated_cost) as jobs_over_estimated_cost,
        count(*) filter (where j.total_actual_cost < j.total_estimated_cost) as jobs_under_estimated_cost
    from
        jobs j
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and j.hourly_rate_quoted is not null
    group by
        j.job_type,
        j.branch_name
)
select
    job_type,
    branch_name,
    total_jobs,
    round(avg_hourly_rate_quoted::numeric, 2) as avg_hourly_rate_quoted,
    round(avg_hourly_rate_billed::numeric, 2) as avg_hourly_rate_billed,
    round((avg_hourly_rate_billed - avg_hourly_rate_quoted)::numeric, 2) as hourly_rate_variance,
    case
        when avg_hourly_rate_quoted > 0 then
            round(((avg_hourly_rate_billed - avg_hourly_rate_quoted)::numeric / avg_hourly_rate_quoted * 100), 2)
        else null
    end as hourly_rate_variance_percent,
    round(avg_estimated_cost::numeric, 2) as avg_estimated_cost,
    round(avg_actual_cost::numeric, 2) as avg_actual_cost,
    round((avg_actual_cost - avg_estimated_cost)::numeric, 2) as cost_variance,
    round(p25_hourly_quoted::numeric, 2) as p25_hourly_quoted,
    round(median_hourly_quoted::numeric, 2) as median_hourly_quoted,
    round(p75_hourly_quoted::numeric, 2) as p75_hourly_quoted,
    round(p25_hourly_billed::numeric, 2) as p25_hourly_billed,
    round(median_hourly_billed::numeric, 2) as median_hourly_billed,
    round(p75_hourly_billed::numeric, 2) as p75_hourly_billed,
    jobs_over_quoted_rate,
    jobs_under_quoted_rate,
    round((jobs_over_quoted_rate::numeric / nullif(total_jobs, 0) * 100), 2) as over_quoted_rate_percent,
    jobs_over_estimated_cost,
    jobs_under_estimated_cost,
    round((jobs_over_estimated_cost::numeric / nullif(total_jobs, 0) * 100), 2) as over_estimated_cost_percent
from
    pricing_analysis
where
    total_jobs > 0
order by
    total_jobs desc,
    hourly_rate_variance_percent desc nulls last;

