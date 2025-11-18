-- Average Job Value
-- Average job value overall and by various dimensions

with overall_avg as (
    select
        'overall' as dimension,
        null as dimension_value,
        count(*) as job_count,
        avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(total_actual_cost, total_estimated_cost)) as median_job_value
    from
        jobs
    where
        is_duplicate = false
),
by_branch as (
    select
        'branch' as dimension,
        branch_name as dimension_value,
        count(*) as job_count,
        avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(total_actual_cost, total_estimated_cost)) as median_job_value
    from
        jobs
    where
        is_duplicate = false
        and branch_name is not null
    group by
        branch_name
),
by_sales_person as (
    select
        'sales_person' as dimension,
        sales_person_name as dimension_value,
        count(*) as job_count,
        avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(total_actual_cost, total_estimated_cost)) as median_job_value
    from
        jobs
    where
        is_duplicate = false
        and sales_person_name is not null
    group by
        sales_person_name
),
by_job_type as (
    select
        'job_type' as dimension,
        job_type as dimension_value,
        count(*) as job_count,
        avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(total_actual_cost, total_estimated_cost)) as median_job_value
    from
        jobs
    where
        is_duplicate = false
        and job_type is not null
    group by
        job_type
)
select
    dimension,
    dimension_value,
    job_count,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value
from
    overall_avg
union all
select
    dimension,
    dimension_value,
    job_count,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value
from
    by_branch
union all
select
    dimension,
    dimension_value,
    job_count,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value
from
    by_sales_person
union all
select
    dimension,
    dimension_value,
    job_count,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value
from
    by_job_type
order by
    dimension,
    avg_job_value desc;

