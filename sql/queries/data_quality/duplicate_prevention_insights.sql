-- Duplicate Prevention Insights
-- Patterns in duplicate detection and prevention

with duplicate_jobs as (
    select
        j.id,
        j.job_id,
        j.job_number,
        j.customer_id,
        j.customer_name,
        j.customer_email,
        j.customer_phone,
        j.job_date,
        j.opportunity_status,
        j.branch_name,
        j.sales_person_name,
        j.total_estimated_cost,
        j.total_actual_cost,
        j.is_duplicate,
        j.created_at
    from
        jobs j
    where
        j.is_duplicate = true
),
duplicate_patterns as (
    select
        date_trunc('month', created_at) as month,
        branch_name,
        sales_person_name,
        opportunity_status,
        count(*) as duplicate_count,
        sum(coalesce(total_estimated_cost, total_actual_cost, 0)) as duplicate_value
    from
        duplicate_jobs
    group by
        date_trunc('month', created_at),
        branch_name,
        sales_person_name,
        opportunity_status
),
customer_duplicates as (
    select
        customer_id,
        customer_email,
        customer_phone,
        count(*) as duplicate_count,
        count(distinct job_id) as unique_job_ids,
        min(created_at) as first_duplicate,
        max(created_at) as last_duplicate
    from
        duplicate_jobs
    where
        customer_id is not null
    group by
        customer_id,
        customer_email,
        customer_phone
)
select
    'monthly_patterns' as analysis_type,
    month,
    branch_name,
    sales_person_name,
    opportunity_status,
    duplicate_count,
    round(duplicate_value::numeric, 2) as duplicate_value
from
    duplicate_patterns
union all
select
    'customer_patterns' as analysis_type,
    null as month,
    null as branch_name,
    null as sales_person_name,
    null as opportunity_status,
    duplicate_count,
    null as duplicate_value
from
    customer_duplicates
order by
    analysis_type,
    duplicate_count desc;

