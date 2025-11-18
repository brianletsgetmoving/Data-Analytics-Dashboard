-- Data Quality Metrics
-- Data completeness and quality metrics across all tables

with job_quality as (
    select
        'jobs' as table_name,
        count(*) as total_records,
        count(customer_id) as records_with_customer_id,
        count(job_date) as records_with_job_date,
        count(branch_name) as records_with_branch_name,
        count(sales_person_name) as records_with_sales_person,
        count(total_estimated_cost) as records_with_estimated_cost,
        count(total_actual_cost) as records_with_actual_cost,
        round(count(customer_id)::numeric / nullif(count(*), 0) * 100, 2) as customer_id_completeness,
        round(count(job_date)::numeric / nullif(count(*), 0) * 100, 2) as job_date_completeness
    from
        jobs
    where
        is_duplicate = false
),
customer_quality as (
    select
        'customers' as table_name,
        count(*) as total_records,
        count(email) as records_with_email,
        count(phone) as records_with_phone,
        count(origin_city) as records_with_origin_city,
        count(destination_city) as records_with_destination_city,
        null::bigint as records_with_customer_id,
        null::bigint as records_with_job_date,
        null::bigint as records_with_branch_name,
        null::bigint as records_with_sales_person,
        null::bigint as records_with_estimated_cost,
        null::bigint as records_with_actual_cost,
        round(count(email)::numeric / nullif(count(*), 0) * 100, 2) as customer_id_completeness,
        round(count(phone)::numeric / nullif(count(*), 0) * 100, 2) as job_date_completeness
    from
        customers
)
select
    table_name,
    total_records,
    records_with_customer_id,
    records_with_job_date,
    records_with_branch_name,
    records_with_sales_person,
    records_with_estimated_cost,
    records_with_actual_cost,
    customer_id_completeness,
    job_date_completeness
from
    job_quality
union all
select
    table_name,
    total_records,
    records_with_customer_id,
    records_with_job_date,
    records_with_branch_name,
    records_with_sales_person,
    records_with_estimated_cost,
    records_with_actual_cost,
    customer_id_completeness,
    job_date_completeness
from
    customer_quality;

