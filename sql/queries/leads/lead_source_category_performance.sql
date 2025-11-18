-- Lead Source Category Performance
-- Performance metrics by LeadSource.category

with category_leads as (
    select
        lsr.category,
        lsr.name as lead_source_name,
        count(distinct ls.id) as total_leads,
        count(distinct bo.id) as booked_opportunities,
        count(distinct c.id) as customers,
        count(distinct j.id) as jobs,
        count(distinct bl.id) as bad_leads,
        count(distinct ll.id) as lost_leads
    from
        lead_sources lsr
    left join
        lead_status ls on lsr.id = ls.lead_source_id
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    left join
        customers c on bo.customer_id = c.id
    left join
        jobs j on c.id = j.customer_id
    left join
        bad_leads bl on lsr.id = bl.lead_source_id
    left join
        lost_leads ll on lsr.id = ll.lead_source_id
    where
        (j.is_duplicate = false or j.id is null)
        and (j.opportunity_status in ('BOOKED', 'CLOSED') or j.id is null)
    group by
        lsr.category,
        lsr.name
),
category_revenue as (
    select
        lsr.category,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(bo.estimated_amount, bo.invoiced_amount, 0)) as opportunity_revenue
    from
        lead_sources lsr
    left join
        lead_status ls on lsr.id = ls.lead_source_id
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    left join
        customers c on bo.customer_id = c.id
    left join
        jobs j on c.id = j.customer_id
    where
        (j.is_duplicate = false or j.id is null)
        and (j.opportunity_status in ('BOOKED', 'CLOSED') or j.id is null)
    group by
        lsr.category
)
select
    cl.category,
    cl.total_leads,
    cl.booked_opportunities,
    cl.customers,
    cl.jobs,
    cl.bad_leads,
    cl.lost_leads,
    round(cr.total_revenue::numeric, 2) as total_revenue,
    round(cr.opportunity_revenue::numeric, 2) as opportunity_revenue,
    round((cl.booked_opportunities::numeric / nullif(cl.total_leads, 0) * 100), 2) as booking_rate,
    round((cl.customers::numeric / nullif(cl.total_leads, 0) * 100), 2) as customer_conversion_rate,
    round((cl.bad_leads::numeric / nullif(cl.total_leads, 0) * 100), 2) as bad_lead_rate,
    round((cl.lost_leads::numeric / nullif(cl.total_leads, 0) * 100), 2) as loss_rate,
    round((cr.total_revenue / nullif(cl.total_leads, 0))::numeric, 2) as revenue_per_lead
from
    category_leads cl
left join
    category_revenue cr on cl.category = cr.category
where
    cl.category is not null
order by
    cl.total_leads desc;

