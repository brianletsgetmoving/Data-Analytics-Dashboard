-- Category Conversion Funnel
-- Conversion funnel analysis by lead source category

with category_funnel as (
    select
        lsr.category,
        count(distinct ls.id) as total_leads,
        count(distinct case when ls.status in ('Quoted', 'Pending') then ls.id end) as quoted_leads,
        count(distinct bo.id) as booked_opportunities,
        count(distinct case when bo.status = 'Closed' then bo.id end) as closed_opportunities,
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
        and lsr.category is not null
    group by
        lsr.category
)
select
    category,
    total_leads,
    quoted_leads,
    booked_opportunities,
    closed_opportunities,
    customers,
    jobs,
    bad_leads,
    lost_leads,
    round((quoted_leads::numeric / nullif(total_leads, 0) * 100), 2) as lead_to_quote_rate,
    round((booked_opportunities::numeric / nullif(quoted_leads, 0) * 100), 2) as quote_to_booking_rate,
    round((closed_opportunities::numeric / nullif(booked_opportunities, 0) * 100), 2) as booking_to_closed_rate,
    round((customers::numeric / nullif(total_leads, 0) * 100), 2) as overall_conversion_rate
from
    category_funnel
order by
    total_leads desc;

