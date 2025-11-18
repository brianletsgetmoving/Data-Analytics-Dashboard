-- Bad Lead Reason Patterns
-- Analyze BadLead.leadBadReason patterns

with bad_lead_reasons as (
    select
        bl.id,
        bl.lead_bad_reason,
        bl.provider,
        bl.move_date,
        bl.date_lead_received,
        bl.lead_source_id,
        lsr.name as lead_source_name,
        lsr.category as lead_source_category,
        bl.customer_id,
        bl.lead_status_id
    from
        bad_leads bl
    left join
        lead_sources lsr on bl.lead_source_id = lsr.id
    where
        bl.lead_bad_reason is not null
),
reason_analysis as (
    select
        lead_bad_reason,
        lead_source_category,
        provider,
        count(*) as total_bad_leads,
        count(distinct customer_id) as unique_customers,
        count(distinct lead_source_id) as lead_sources_count,
        min(date_lead_received) as first_received,
        max(date_lead_received) as last_received,
        round(avg(extract(epoch from (move_date - date_lead_received)) / 86400)::numeric, 2) as avg_days_to_move
    from
        bad_lead_reasons
    group by
        lead_bad_reason,
        lead_source_category,
        provider
)
select
    lead_bad_reason,
    lead_source_category,
    provider,
    total_bad_leads,
    unique_customers,
    lead_sources_count,
    first_received,
    last_received,
    avg_days_to_move,
    round((total_bad_leads::numeric / sum(total_bad_leads) over () * 100), 2) as percentage_of_bad_leads
from
    reason_analysis
order by
    total_bad_leads desc;

