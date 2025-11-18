-- Lost Leads Analysis
-- Lost leads with reasons and time to contact

select
    quote_number,
    name,
    lost_date,
    move_date,
    reason,
    date_received,
    time_to_first_contact,
    lost_date - date_received as days_to_lost,
    extract(epoch from (lost_date - date_received)) / 86400 as days_to_lost_numeric
from
    lost_leads
where
    lost_date is not null
    and date_received is not null
order by
    lost_date desc;

