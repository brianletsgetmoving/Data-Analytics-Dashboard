-- Win/Loss by Reason Analysis
-- Conversion rates by loss reason category

with lead_outcomes as (
    select
        ll.id as lost_lead_id,
        ll.reason as loss_reason,
        ll.quote_number,
        bo.id as booked_opportunity_id,
        case when bo.id is not null then 'won' else 'lost' end as outcome,
        bo.estimated_amount,
        bo.invoiced_amount
    from
        lost_leads ll
    left join
        booked_opportunities bo on ll.quote_number = bo.quote_number
    where
        ll.reason is not null
),
reason_categories as (
    select
        loss_reason,
        count(*) filter (where outcome = 'won') as won_count,
        count(*) filter (where outcome = 'lost') as lost_count,
        count(*) as total_count,
        sum(coalesce(estimated_amount, invoiced_amount, 0)) filter (where outcome = 'won') as won_value,
        sum(coalesce(estimated_amount, invoiced_amount, 0)) filter (where outcome = 'lost') as lost_value
    from
        lead_outcomes
    group by
        loss_reason
)
select
    loss_reason,
    won_count,
    lost_count,
    total_count,
    round(won_value::numeric, 2) as won_value,
    round(lost_value::numeric, 2) as lost_value,
    round((won_count::numeric / nullif(total_count, 0) * 100), 2) as win_rate,
    round((lost_count::numeric / nullif(total_count, 0) * 100), 2) as loss_rate,
    round((won_value / nullif(won_count, 0))::numeric, 2) as avg_won_value,
    round((lost_value / nullif(lost_count, 0))::numeric, 2) as avg_lost_value
from
    reason_categories
order by
    total_count desc;

