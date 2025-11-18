-- Customer Lead Journey
-- Tracks customer journey from lead to booking/loss across all modules
-- Shows the complete lifecycle: lead → quote → booking → customer or loss

with lead_status_leads as (
    -- All leads from lead_status table (central hub for leads)
    select
        ls.quote_number,
        ls.status as lead_status,
        ls.sales_person,
        ls.branch_name,
        ls.referral_source,
        ls.time_to_contact,
        'lead_status' as source_module
    from
        lead_status ls
),
booked_opportunity_leads as (
    -- Leads that became booked opportunities
    select
        bo.quote_number,
        bo.status as lead_status,
        bo.sales_person,
        bo.branch_name,
        bo.referral_source,
        null as time_to_contact,
        'booked_opportunity' as source_module
    from
        booked_opportunities bo
),
lost_lead_records as (
    -- Lost leads with their details
    select
        ll.quote_number,
        'Lost' as lead_status,
        null as sales_person,
        null as branch_name,
        null as referral_source,
        ll.time_to_first_contact as time_to_contact,
        'lost_lead' as source_module
    from
        lost_leads ll
),
bad_lead_records as (
    -- Bad leads (should link to lead_status via customer matching)
    select
        null as quote_number,
        'Bad Lead' as lead_status,
        null as sales_person,
        null as branch_name,
        null as referral_source,
        null as time_to_contact,
        'bad_lead' as source_module
    from
        bad_leads bl
),
all_leads as (
    -- Combine all lead sources
    select * from lead_status_leads
    union all
    select * from booked_opportunity_leads
    union all
    select * from lost_lead_records
    union all
    select * from bad_lead_records
),
customer_conversions as (
    -- Track which leads converted to customers (booked/closed jobs)
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(j.id) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as converted_job_count,
        min(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as first_customer_job_date,
        max(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as last_customer_job_date
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
    group by
        c.id, c.name, c.email, c.phone
),
lead_to_customer_mapping as (
    -- Map leads to customers via booked opportunities
    select
        bo.quote_number,
        bo.customer_id,
        bo.booked_date,
        bo.status as booking_status
    from
        booked_opportunities bo
    where
        bo.customer_id is not null
)
select
    al.quote_number,
    al.lead_status,
    al.sales_person,
    al.branch_name,
    al.referral_source,
    al.time_to_contact,
    al.source_module,
    -- Customer conversion information
    lcm.customer_id,
    cc.customer_name,
    cc.email,
    cc.phone,
    lcm.booked_date as conversion_date,
    lcm.booking_status,
    cc.converted_job_count,
    cc.first_customer_job_date,
    cc.last_customer_job_date,
    -- Journey stage classification
    case
        when cc.converted_job_count > 0 then 'Converted to Customer'
        when al.lead_status = 'Lost' then 'Lost Lead'
        when al.lead_status = 'Bad Lead' then 'Bad Lead'
        when lcm.customer_id is not null then 'Booked (Not Yet Customer)'
        else 'Active Lead'
    end as journey_stage
from
    all_leads al
left join
    lead_to_customer_mapping lcm on al.quote_number = lcm.quote_number
left join
    customer_conversions cc on lcm.customer_id = cc.customer_id
order by
    lcm.booked_date desc nulls last,
    al.quote_number;

