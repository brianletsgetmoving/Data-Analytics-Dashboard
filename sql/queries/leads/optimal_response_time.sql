-- Optimal Response Time Analysis
-- Identify optimal response time windows for maximum conversion

with lead_response_data as (
    select
        ls.id as lead_id,
        ls.time_to_contact,
        bo.id as booked_opportunity_id,
        case when bo.id is not null then true else false end as converted,
        case
            when ls.time_to_contact like '%min%' or ls.time_to_contact like '%Min%' then 'minutes'
            when ls.time_to_contact like '%hour%' or ls.time_to_contact like '%Hour%' then 'hours'
            else 'unknown'
        end as time_unit,
        case
            when ls.time_to_contact ~ '^[0-9]+' then (regexp_match(ls.time_to_contact, '^[0-9]+'))[1]::integer
            else null
        end as time_value
    from
        lead_status ls
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    where
        ls.time_to_contact is not null
        and (ls.time_to_contact like '%min%' or ls.time_to_contact like '%hour%')
),
response_windows as (
    select
        case
            when time_value <= 5 then '0-5 min'
            when time_value <= 15 then '6-15 min'
            when time_value <= 30 then '16-30 min'
            when time_value <= 60 then '31-60 min'
            when time_value <= 120 then '1-2 hours'
            when time_value <= 240 then '2-4 hours'
            when time_value <= 480 then '4-8 hours'
            else '8+ hours'
        end as response_window,
        count(*) as total_leads,
        count(*) filter (where converted) as converted_leads,
        count(*) filter (where not converted) as non_converted_leads
    from
        lead_response_data
    where
        time_value is not null
    group by
        case
            when time_value <= 5 then '0-5 min'
            when time_value <= 15 then '6-15 min'
            when time_value <= 30 then '16-30 min'
            when time_value <= 60 then '31-60 min'
            when time_value <= 120 then '1-2 hours'
            when time_value <= 240 then '2-4 hours'
            when time_value <= 480 then '4-8 hours'
            else '8+ hours'
        end
)
select
    response_window,
    total_leads,
    converted_leads,
    non_converted_leads,
    round((converted_leads::numeric / nullif(total_leads, 0) * 100), 2) as conversion_rate,
    round((total_leads::numeric / sum(total_leads) over () * 100), 2) as percentage_of_leads,
    case
        when (converted_leads::numeric / nullif(total_leads, 0)) >= 0.3 then 'optimal'
        when (converted_leads::numeric / nullif(total_leads, 0)) >= 0.2 then 'good'
        when (converted_leads::numeric / nullif(total_leads, 0)) >= 0.1 then 'acceptable'
        else 'needs_improvement'
    end as performance_category
from
    response_windows
order by
    conversion_rate desc;

