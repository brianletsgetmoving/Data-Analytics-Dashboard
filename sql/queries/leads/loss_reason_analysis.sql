-- Loss Reason Analysis
-- Analyze LostLead.reason patterns and their impact

with lost_lead_reasons as (
    select
        ll.id,
        ll.quote_number,
        ll.reason,
        ll.lost_date,
        ll.move_date,
        ll.lead_source_id,
        lsr.name as lead_source_name,
        lsr.category as lead_source_category,
        ll.booked_opportunity_id,
        bo.customer_id,
        bo.estimated_amount,
        bo.invoiced_amount
    from
        lost_leads ll
    left join
        lead_sources lsr on ll.lead_source_id = lsr.id
    left join
        booked_opportunities bo on ll.booked_opportunity_id = bo.id
    where
        ll.reason is not null
),
reason_summary as (
    select
        reason,
        lead_source_category,
        count(*) as total_lost,
        count(distinct customer_id) as unique_customers,
        count(distinct lead_source_id) as lead_sources_count,
        sum(coalesce(estimated_amount, invoiced_amount, 0)) as lost_value,
        min(lost_date) as first_lost_date,
        max(lost_date) as last_lost_date,
        round(avg(extract(epoch from (move_date - lost_date)) / 86400)::numeric, 2) as avg_days_to_move
    from
        lost_lead_reasons
    group by
        reason,
        lead_source_category
)
select
    reason,
    lead_source_category,
    total_lost,
    unique_customers,
    lead_sources_count,
    round(lost_value::numeric, 2) as lost_value,
    first_lost_date,
    last_lost_date,
    avg_days_to_move,
    round((total_lost::numeric / sum(total_lost) over () * 100), 2) as percentage_of_losses,
    round((lost_value / nullif(total_lost, 0))::numeric, 2) as avg_value_per_loss
from
    reason_summary
order by
    total_lost desc;

