-- Lead Response Time Analysis
-- Time to first contact analysis

with lead_times as (
    select
        quote_number,
        time_to_contact,
        case
            when time_to_contact ~ '^[0-9]+$' then time_to_contact::integer
            when time_to_contact ~ '^[0-9]+\s*(min|minutes?)$' then regexp_replace(time_to_contact, '[^0-9]', '', 'g')::integer
            when time_to_contact ~ '^[0-9]+\s*(hour|hours?)$' then regexp_replace(time_to_contact, '[^0-9]', '', 'g')::integer * 60
            when time_to_contact ~ '^[0-9]+\s*(day|days?)$' then regexp_replace(time_to_contact, '[^0-9]', '', 'g')::integer * 1440
            else null
        end as minutes_to_contact
    from
        lead_status
    where
        time_to_contact is not null
)
select
    quote_number,
    time_to_contact,
    minutes_to_contact,
    case
        when minutes_to_contact <= 15 then 'Immediate (0-15 min)'
        when minutes_to_contact <= 60 then 'Fast (15-60 min)'
        when minutes_to_contact <= 240 then 'Moderate (1-4 hours)'
        when minutes_to_contact <= 1440 then 'Slow (4-24 hours)'
        else 'Very Slow (>24 hours)'
    end as response_category
from
    lead_times
order by
    minutes_to_contact asc nulls last;

