-- Competitive Metrics
-- Win rate, quote-to-close ratio, and other competitive indicators

with competitive_metrics as (
    select
        count(*) filter (where opportunity_status = 'QUOTED') as total_quoted,
        count(*) filter (where opportunity_status = 'BOOKED') as total_booked,
        count(*) filter (where opportunity_status = 'CLOSED') as total_closed,
        count(*) filter (where opportunity_status = 'LOST') as total_lost,
        count(*) filter (where opportunity_status in ('BOOKED', 'CLOSED')) as total_won,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'QUOTED') as quoted_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'LOST') as lost_revenue,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status in ('BOOKED', 'CLOSED')) as won_revenue,
        avg(coalesce(total_estimated_cost, 0)) filter (where opportunity_status = 'QUOTED') as avg_quoted_value,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as avg_booked_value,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as avg_closed_value
    from
        jobs
    where
        is_duplicate = false
        and opportunity_status in ('QUOTED', 'BOOKED', 'CLOSED', 'LOST')
)
select
    total_quoted,
    total_booked,
    total_closed,
    total_lost,
    total_won,
    round(quoted_revenue::numeric, 2) as quoted_revenue,
    round(booked_revenue::numeric, 2) as booked_revenue,
    round(closed_revenue::numeric, 2) as closed_revenue,
    round(lost_revenue::numeric, 2) as lost_revenue,
    round(won_revenue::numeric, 2) as won_revenue,
    round(avg_quoted_value::numeric, 2) as avg_quoted_value,
    round(avg_booked_value::numeric, 2) as avg_booked_value,
    round(avg_closed_value::numeric, 2) as avg_closed_value,
    -- Win rate calculations
    round((total_won::numeric / nullif(total_quoted + total_booked + total_closed + total_lost, 0) * 100), 2) as overall_win_rate_percent,
    round((total_booked::numeric / nullif(total_quoted, 0) * 100), 2) as quote_to_book_rate_percent,
    round((total_closed::numeric / nullif(total_booked, 0) * 100), 2) as book_to_close_rate_percent,
    round((total_closed::numeric / nullif(total_quoted, 0) * 100), 2) as quote_to_close_rate_percent,
    -- Loss rate
    round((total_lost::numeric / nullif(total_quoted + total_booked + total_closed + total_lost, 0) * 100), 2) as loss_rate_percent,
    -- Revenue conversion rates
    round((won_revenue / nullif(quoted_revenue, 0) * 100), 2) as revenue_conversion_rate_percent,
    round((booked_revenue / nullif(quoted_revenue, 0) * 100), 2) as revenue_book_rate_percent,
    round((closed_revenue / nullif(booked_revenue, 0) * 100), 2) as revenue_close_rate_percent,
    -- Average deal size changes
    round(((avg_booked_value - avg_quoted_value) / nullif(avg_quoted_value, 0) * 100)::numeric, 2) as booked_vs_quoted_percent,
    round(((avg_closed_value - avg_booked_value) / nullif(avg_booked_value, 0) * 100)::numeric, 2) as closed_vs_booked_percent
from
    competitive_metrics;

