-- Job Conversion Rates
-- Quote to booking conversion rates overall and by branch/sales person

with conversion_rates as (
    select
        'overall' as dimension,
        null as dimension_value,
        count(*) filter (where opportunity_status = 'QUOTED') as quoted_count,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
        count(*) filter (where opportunity_status = 'LOST') as lost_count
    from
        jobs
    where
        is_duplicate = false
    union all
    select
        'branch' as dimension,
        branch_name as dimension_value,
        count(*) filter (where opportunity_status = 'QUOTED') as quoted_count,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
        count(*) filter (where opportunity_status = 'LOST') as lost_count
    from
        jobs
    where
        is_duplicate = false
        and branch_name is not null
    group by
        branch_name
    union all
    select
        'sales_person' as dimension,
        sales_person_name as dimension_value,
        count(*) filter (where opportunity_status = 'QUOTED') as quoted_count,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_count,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_count,
        count(*) filter (where opportunity_status = 'LOST') as lost_count
    from
        jobs
    where
        is_duplicate = false
        and sales_person_name is not null
    group by
        sales_person_name
)
select
    dimension,
    dimension_value,
    quoted_count,
    booked_count,
    closed_count,
    lost_count,
    quoted_count + booked_count + closed_count + lost_count as total_leads,
    round(booked_count::numeric / nullif(quoted_count, 0) * 100, 2) as quote_to_booking_rate,
    round(closed_count::numeric / nullif(booked_count, 0) * 100, 2) as booking_to_closed_rate,
    round((booked_count + closed_count)::numeric / nullif(quoted_count, 0) * 100, 2) as quote_to_closed_rate,
    round(lost_count::numeric / nullif(quoted_count + lost_count, 0) * 100, 2) as loss_rate
from
    conversion_rates
order by
    dimension,
    quote_to_booking_rate desc nulls last;

