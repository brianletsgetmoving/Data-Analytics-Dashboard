-- Referral Source ROI Analysis
-- ROI analysis by referral source

with referral_metrics as (
    select
        j.referral_source,
        count(distinct j.id) as total_jobs,
        count(distinct j.customer_id) as customer_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(distinct bo.id) as booked_opportunities,
        count(distinct ls.id) as total_leads
    from
        jobs j
    left join
        customers c on j.customer_id = c.id
    left join
        booked_opportunities bo on c.id = bo.customer_id
    left join
        lead_status ls on bo.quote_number = ls.quote_number
    where
        j.is_duplicate = false
        and j.referral_source is not null
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        j.referral_source
)
select
    referral_source,
    total_jobs,
    customer_count,
    booked_opportunities,
    total_leads,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((booked_opportunities::numeric / nullif(total_leads, 0) * 100), 2) as conversion_rate,
    round((total_revenue / nullif(total_leads, 0))::numeric, 2) as revenue_per_lead,
    round((total_revenue / nullif(customer_count, 0))::numeric, 2) as revenue_per_customer,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job
from
    referral_metrics
order by
    total_revenue desc;

