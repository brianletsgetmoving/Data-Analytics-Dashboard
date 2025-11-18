-- Job Data Completeness Metrics
-- Job record completeness metrics

select
    count(*) as total_jobs,
    count(customer_id) as jobs_with_customer_id,
    count(job_date) as jobs_with_job_date,
    count(branch_name) as jobs_with_branch_name,
    count(sales_person_name) as jobs_with_sales_person,
    count(job_type) as jobs_with_job_type,
    count(opportunity_status) as jobs_with_status,
    count(total_estimated_cost) as jobs_with_estimated_cost,
    count(total_actual_cost) as jobs_with_actual_cost,
    count(origin_city) as jobs_with_origin_city,
    count(destination_city) as jobs_with_destination_city,
    count(referral_source) as jobs_with_referral_source,
    round(count(customer_id)::numeric / nullif(count(*), 0) * 100, 2) as customer_id_completeness_percent,
    round(count(job_date)::numeric / nullif(count(*), 0) * 100, 2) as job_date_completeness_percent,
    round(count(branch_name)::numeric / nullif(count(*), 0) * 100, 2) as branch_name_completeness_percent,
    round(count(sales_person_name)::numeric / nullif(count(*), 0) * 100, 2) as sales_person_completeness_percent,
    round(count(total_estimated_cost)::numeric / nullif(count(*), 0) * 100, 2) as estimated_cost_completeness_percent,
    round(count(total_actual_cost)::numeric / nullif(count(*), 0) * 100, 2) as actual_cost_completeness_percent
from
    jobs
where
    is_duplicate = false;

