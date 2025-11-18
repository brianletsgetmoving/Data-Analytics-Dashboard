-- Customer Acquisition Cost (CAC) Analysis
-- CAC by source and segment

with lead_costs as (
    select
        l.id as lead_id,
        l.customer_id,
        l.date_received as lead_date,
        ls.name as lead_source_name,
        ls.id as lead_source_id,
        count(distinct j.id) as jobs_from_lead,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue_from_lead
    from
        leads l
    left join
        lead_sources ls on l.lead_source_id = ls.id
    left join
        lead_statuses lst on l.id = lst.lead_id
    left join
        jobs j on lst.customer_id = j.customer_id
    where
        (j.is_duplicate = false or j.id is null)
    group by
        l.id, l.customer_id, l.date_received, ls.name, ls.id
),
source_metrics as (
    select
        ls.name as lead_source_name,
        ls.id as lead_source_id,
        count(distinct l.id) as total_leads,
        count(distinct l.customer_id) as unique_customers,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(distinct j.id) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(distinct j.id) filter (where j.opportunity_status = 'CLOSED') as closed_jobs
    from
        lead_sources ls
    left join
        leads l on ls.id = l.lead_source_id
    left join
        lead_statuses lst on l.id = lst.lead_id
    left join
        jobs j on lst.customer_id = j.customer_id
    where
        (j.is_duplicate = false or j.id is null)
    group by
        ls.id, ls.name
),
customer_segments as (
    select
        c.id as customer_id,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        case
            when sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) >= 5000 then 'high_value'
            when sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) >= 2000 then 'medium_value'
            when sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) >= 500 then 'low_value'
            else 'minimal_value'
        end as customer_segment
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id
)
select
    sm.lead_source_name,
    sm.lead_source_id,
    sm.total_leads,
    sm.unique_customers,
    sm.total_jobs,
    round(sm.total_revenue::numeric, 2) as total_revenue,
    round(sm.avg_job_value::numeric, 2) as avg_job_value,
    sm.booked_jobs,
    sm.closed_jobs,
    round((sm.unique_customers::numeric / nullif(sm.total_leads, 0) * 100), 2) as lead_to_customer_conversion_rate,
    round((sm.total_jobs::numeric / nullif(sm.total_leads, 0)), 2) as jobs_per_lead,
    round((sm.total_revenue / nullif(sm.total_leads, 0))::numeric, 2) as revenue_per_lead,
    round((sm.total_revenue / nullif(sm.unique_customers, 0))::numeric, 2) as revenue_per_customer,
    round((sm.booked_jobs::numeric / nullif(sm.total_jobs, 0) * 100), 2) as booking_rate_percent,
    round((sm.closed_jobs::numeric / nullif(sm.total_jobs, 0) * 100), 2) as closing_rate_percent
from
    source_metrics sm
where
    sm.total_leads > 0
order by
    sm.total_revenue desc,
    sm.total_leads desc;

