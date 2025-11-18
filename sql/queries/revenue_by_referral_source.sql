-- Revenue by Referral Source
-- Revenue by referral source and affiliate

select
    referral_source,
    affiliate_name,
    count(*) as job_count,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    round(count(*) filter (where opportunity_status = 'BOOKED')::numeric / nullif(count(*), 0) * 100, 2) as booking_rate_percent
from
    jobs
where
    is_duplicate = false
    and referral_source is not null
group by
    referral_source,
    affiliate_name
order by
    total_revenue desc;

