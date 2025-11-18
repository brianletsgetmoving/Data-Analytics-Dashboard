-- Job Cancellation Analysis
-- Cancelled jobs analysis with patterns

select
    id,
    job_id,
    job_number,
    customer_id,
    branch_name,
    sales_person_name,
    job_type,
    job_date,
    created_at_utc,
    booked_at_utc,
    booked_at_utc - created_at_utc as time_before_cancellation,
    extract(epoch from (booked_at_utc - created_at_utc)) / 86400 as days_before_cancellation,
    total_estimated_cost,
    referral_source,
    affiliate_name
from
    jobs
where
    is_duplicate = false
    and opportunity_status = 'CANCELLED'
order by
    job_date desc;

