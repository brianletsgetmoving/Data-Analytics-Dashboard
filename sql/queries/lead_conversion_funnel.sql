-- Lead Conversion Funnel
-- Lead to quote to booking conversion funnel

with lead_sources as (
    select
        'jobs' as source_table,
        count(*) as total_leads,
        count(*) filter (where opportunity_status = 'QUOTED') as quoted,
        count(*) filter (where opportunity_status = 'BOOKED') as booked,
        count(*) filter (where opportunity_status = 'CLOSED') as closed,
        count(*) filter (where opportunity_status = 'LOST') as lost
    from
        jobs
    where
        is_duplicate = false
    union all
    select
        'booked_opportunities' as source_table,
        count(*) as total_leads,
        count(*) filter (where status = 'Quoted' or status = 'Pending') as quoted,
        count(*) filter (where status = 'Booked' or status = 'Closed') as booked,
        count(*) filter (where status = 'Closed') as closed,
        count(*) filter (where status = 'Lost') as lost
    from
        booked_opportunities
    union all
    select
        'bad_leads' as source_table,
        count(*) as total_leads,
        0 as quoted,
        0 as booked,
        0 as closed,
        count(*) as lost
    from
        bad_leads
    union all
    select
        'lost_leads' as source_table,
        count(*) as total_leads,
        0 as quoted,
        0 as booked,
        0 as closed,
        count(*) as lost
    from
        lost_leads
),
funnel_summary as (
    select
        sum(total_leads) as total_leads,
        sum(quoted) as total_quoted,
        sum(booked) as total_booked,
        sum(closed) as total_closed,
        sum(lost) as total_lost
    from
        lead_sources
)
select
    'funnel' as metric_type,
    total_leads,
    total_quoted,
    total_booked,
    total_closed,
    total_lost,
    round(total_quoted::numeric / nullif(total_leads, 0) * 100, 2) as lead_to_quote_rate,
    round(total_booked::numeric / nullif(total_quoted, 0) * 100, 2) as quote_to_booking_rate,
    round(total_closed::numeric / nullif(total_booked, 0) * 100, 2) as booking_to_closed_rate,
    round(total_closed::numeric / nullif(total_leads, 0) * 100, 2) as overall_conversion_rate
from
    funnel_summary;

