-- Gender Job Preferences Analysis
-- Job type, branch, and service preferences by customer gender

with gender_preferences as (
    select
        c.gender,
        j.job_type,
        j.branch_name,
        count(distinct j.id) as job_count,
        count(distinct c.id) as customer_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.gender is not null
    group by
        c.gender,
        j.job_type,
        j.branch_name
),
gender_totals as (
    select
        gender,
        sum(job_count) as total_jobs
    from
        gender_preferences
    group by
        gender
)
select
    gp.gender::text as gender,
    gp.job_type,
    gp.branch_name,
    gp.job_count,
    gp.customer_count,
    round(gp.total_revenue::numeric, 2) as total_revenue,
    round(gp.avg_job_value::numeric, 2) as avg_job_value,
    round((gp.job_count::numeric / nullif(gt.total_jobs, 0) * 100), 2) as percentage_of_gender_jobs,
    round((gp.job_count::numeric / nullif(gp.customer_count, 0)), 2) as jobs_per_customer
from
    gender_preferences gp
inner join
    gender_totals gt on gp.gender = gt.gender
order by
    gp.gender,
    gp.job_count desc;

