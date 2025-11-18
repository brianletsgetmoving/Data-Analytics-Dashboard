-- User Call Performance
-- User call metrics from user_performance table

select
    name,
    user_status,
    total_calls,
    round(avg_calls_per_day, 2) as avg_calls_per_day,
    inbound_count,
    outbound_count,
    round(missed_percent, 2) as missed_percent,
    avg_handle_time,
    round(inbound_count::numeric / nullif(total_calls, 0) * 100, 2) as inbound_percentage,
    round(outbound_count::numeric / nullif(total_calls, 0) * 100, 2) as outbound_percentage
from
    user_performance
order by
    total_calls desc nulls last;

