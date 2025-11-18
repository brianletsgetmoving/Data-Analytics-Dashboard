-- Bad Leads Analysis
-- Bad leads count, reasons, and trends

select
    provider,
    lead_bad_reason,
    count(*) as bad_lead_count,
    count(distinct customer_id) as unique_customers,
    count(distinct customer_email) as unique_emails,
    min(date_lead_received) as earliest_lead,
    max(date_lead_received) as latest_lead
from
    bad_leads
where
    lead_bad_reason is not null
group by
    provider,
    lead_bad_reason
order by
    bad_lead_count desc;

