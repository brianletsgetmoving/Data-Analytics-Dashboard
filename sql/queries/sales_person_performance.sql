-- Sales Person Performance
-- Comprehensive sales person metrics from sales_performance table

select
    name,
    leads_received,
    bad,
    round(percent_bad, 2) as percent_bad,
    sent,
    round(percent_sent, 2) as percent_sent,
    pending,
    round(percent_pending, 2) as percent_pending,
    booked,
    round(percent_booked, 2) as percent_booked,
    lost,
    round(percent_lost, 2) as percent_lost,
    cancelled,
    round(percent_cancelled, 2) as percent_cancelled,
    booked_total,
    average_booking,
    round(booked::numeric / nullif(leads_received, 0) * 100, 2) as calculated_booking_rate,
    round(booked_total / nullif(booked, 0), 2) as calculated_avg_booking
from
    sales_performance
order by
    booked_total desc nulls last;

