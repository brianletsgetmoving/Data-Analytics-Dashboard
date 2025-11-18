-- Response Time Impact Analysis
-- Impact of timeToContact on lead conversion rates

with lead_response_times as (
    select
        ls.id as lead_id,
        ls.quote_number,
        ls.time_to_contact,
        ls.status,
        ls.sales_person_id,
        ls.branch_id,
        ls.lead_source_id,
        bo.id as booked_opportunity_id,
        bo.customer_id,
        case when bo.id is not null then true else false end as converted,
        case when ll.id is not null then true else false end as lost,
        case when bl.id is not null then true else false end as bad_lead
    from
        lead_status ls
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    left join
        lost_leads ll on ls.quote_number = ll.quote_number
    left join
        bad_leads bl on ls.lead_status_id = ls.id
    where
        ls.time_to_contact is not null
),
response_time_buckets as (
    select
        lead_id,
        time_to_contact,
        converted,
        lost,
        bad_lead,
        case
            when time_to_contact like '%min%' or time_to_contact like '%Min%' then 'minutes'
            when time_to_contact like '%hour%' or time_to_contact like '%Hour%' then 'hours'
            when time_to_contact like '%day%' or time_to_contact like '%Day%' then 'days'
            else 'unknown'
        end as time_unit,
        case
            when time_to_contact ~ '^[0-9]+' then (regexp_match(time_to_contact, '^[0-9]+'))[1]::integer
            else null
        end as time_value
    from
        lead_response_times
),
response_analysis as (
    select
        time_unit,
        case
            when time_value <= 15 then '0-15'
            when time_value <= 30 then '16-30'
            when time_value <= 60 then '31-60'
            when time_value <= 120 then '61-120'
            when time_value <= 240 then '121-240'
            else '240+'
        end as time_bucket,
        count(*) as total_leads,
        count(*) filter (where converted) as converted_leads,
        count(*) filter (where lost) as lost_leads,
        count(*) filter (where bad_lead) as bad_leads
    from
        response_time_buckets
    where
        time_unit in ('minutes', 'hours')
        and time_value is not null
    group by
        time_unit,
        case
            when time_value <= 15 then '0-15'
            when time_value <= 30 then '16-30'
            when time_value <= 60 then '31-60'
            when time_value <= 120 then '121-120'
            when time_value <= 240 then '121-240'
            else '240+'
        end
)
select
    time_unit,
    time_bucket,
    total_leads,
    converted_leads,
    lost_leads,
    bad_leads,
    round((converted_leads::numeric / nullif(total_leads, 0) * 100), 2) as conversion_rate,
    round((lost_leads::numeric / nullif(total_leads, 0) * 100), 2) as loss_rate,
    round((bad_leads::numeric / nullif(total_leads, 0) * 100), 2) as bad_lead_rate
from
    response_analysis
order by
    time_unit,
    time_bucket;

