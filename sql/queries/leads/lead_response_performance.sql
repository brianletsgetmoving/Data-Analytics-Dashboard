-- Lead Response Performance
-- Response time performance by sales person and branch

with lead_response_data as (
    select
        ls.id as lead_id,
        ls.time_to_contact,
        ls.sales_person_id,
        sp.name as sales_person_name,
        ls.branch_id,
        b.name as branch_name,
        ls.lead_source_id,
        lsr.name as lead_source_name,
        bo.id as booked_opportunity_id,
        case when bo.id is not null then true else false end as converted,
        case
            when ls.time_to_contact like '%min%' or ls.time_to_contact like '%Min%' then 'minutes'
            when ls.time_to_contact like '%hour%' or ls.time_to_contact like '%Hour%' then 'hours'
            when ls.time_to_contact like '%day%' or ls.time_to_contact like '%Day%' then 'days'
            else 'unknown'
        end as time_unit,
        case
            when ls.time_to_contact ~ '^[0-9]+' then (regexp_match(ls.time_to_contact, '^[0-9]+'))[1]::integer
            else null
        end as time_value
    from
        lead_status ls
    left join
        sales_persons sp on ls.sales_person_id = sp.id
    left join
        branches b on ls.branch_id = b.id
    left join
        lead_sources lsr on ls.lead_source_id = lsr.id
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    where
        ls.time_to_contact is not null
),
response_metrics as (
    select
        sales_person_id,
        sales_person_name,
        branch_id,
        branch_name,
        lead_source_id,
        lead_source_name,
        count(*) as total_leads,
        count(*) filter (where converted) as converted_leads,
        count(*) filter (where time_unit = 'minutes' and time_value <= 15) as fast_response_leads,
        count(*) filter (where time_unit = 'minutes' and time_value > 60) as slow_response_leads,
        round(avg(case when time_unit = 'minutes' then time_value end)::numeric, 2) as avg_response_minutes
    from
        lead_response_data
    where
        time_value is not null
    group by
        sales_person_id,
        sales_person_name,
        branch_id,
        branch_name,
        lead_source_id,
        lead_source_name
)
select
    sales_person_name,
    branch_name,
    lead_source_name,
    total_leads,
    converted_leads,
    fast_response_leads,
    slow_response_leads,
    avg_response_minutes,
    round((converted_leads::numeric / nullif(total_leads, 0) * 100), 2) as conversion_rate,
    round((fast_response_leads::numeric / nullif(total_leads, 0) * 100), 2) as fast_response_rate,
    round((slow_response_leads::numeric / nullif(total_leads, 0) * 100), 2) as slow_response_rate
from
    response_metrics
order by
    conversion_rate desc,
    avg_response_minutes asc;

