-- ROI by Referral Source
-- Return on Investment analysis by lead/referral source

with source_metrics as (
    select
        j.referral_source,
        count(distinct j.id) as total_jobs,
        count(distinct j.customer_id) as unique_customers,
        count(distinct j.id) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(distinct j.id) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (where j.opportunity_status = 'BOOKED') as booked_revenue,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (where j.opportunity_status = 'CLOSED') as closed_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(distinct l.id) as total_leads
    from
        jobs j
    left join
        lead_statuses ls on j.customer_id = ls.customer_id
    left join
        leads l on ls.lead_id = l.id
    where
        j.is_duplicate = false
        and j.referral_source is not null
    group by
        j.referral_source
)
select
    referral_source,
    total_jobs,
    unique_customers,
    booked_jobs,
    closed_jobs,
    round(total_revenue::numeric, 2) as total_revenue,
    round(booked_revenue::numeric, 2) as booked_revenue,
    round(closed_revenue::numeric, 2) as closed_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job,
    round((total_revenue / nullif(unique_customers, 0))::numeric, 2) as revenue_per_customer,
    round((booked_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as booking_rate_percent,
    round((closed_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as closing_rate_percent,
    total_leads,
    case
        when total_leads > 0 then
            round((total_revenue / nullif(total_leads, 0))::numeric, 2)
        else null
    end as revenue_per_lead,
    case
        when total_leads > 0 then
            round((unique_customers::numeric / nullif(total_leads, 0) * 100), 2)
        else null
    end as lead_to_customer_conversion_rate
from
    source_metrics
order by
    total_revenue desc;

