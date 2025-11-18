-- Lead to Customer Traceability
-- Traces leads through all modules to customers
-- Shows the complete journey from initial lead to customer conversion

with all_leads as (
    -- Combine all lead sources
    select
        ls.quote_number,
        ls.id as lead_id,
        'lead_status' as lead_source,
        ls.status as lead_status,
        ls.sales_person,
        ls.branch_name,
        ls.referral_source,
        ls.time_to_contact,
        ls.created_at as lead_created_at,
        null::uuid as customer_id,
        null::text as customer_name,
        null::text as customer_email,
        null::text as customer_phone
    from
        lead_status ls
    union all
    -- Bad leads (attempt to link via customer)
    select
        null as quote_number,
        bl.id as lead_id,
        'bad_lead' as lead_source,
        'Bad Lead' as lead_status,
        null as sales_person,
        null as branch_name,
        null as referral_source,
        null as time_to_contact,
        bl.created_at as lead_created_at,
        bl.customer_id,
        bl.customer_name,
        bl.customer_email,
        bl.customer_phone
    from
        bad_leads bl
    union all
    -- Lost leads
    select
        ll.quote_number,
        ll.id as lead_id,
        'lost_lead' as lead_source,
        'Lost' as lead_status,
        null as sales_person,
        null as branch_name,
        null as referral_source,
        ll.time_to_first_contact as time_to_contact,
        ll.created_at as lead_created_at,
        null::uuid as customer_id,
        ll.name as customer_name,
        null::text as customer_email,
        null::text as customer_phone
    from
        lost_leads ll
),
leads_with_bookings as (
    -- Link leads to booked opportunities via quote_number
    select
        al.*,
        bo.id as booked_opportunity_id,
        bo.status as booked_opportunity_status,
        bo.customer_id as booked_customer_id,
        bo.booked_date,
        bo.sales_person as booked_sales_person,
        bo.branch_name as booked_branch_name
    from
        all_leads al
    left join
        booked_opportunities bo on al.quote_number = bo.quote_number
        or (al.customer_id is not null and al.customer_id = bo.customer_id)
        or (al.customer_email is not null and al.customer_email = bo.email)
        or (al.customer_phone is not null and al.customer_phone = bo.phone_number)
),
leads_with_customer_jobs as (
    -- Link to customer jobs (booked/closed only - customers, not leads)
    select
        lwb.*,
        c.id as final_customer_id,
        c.name as final_customer_name,
        c.email as final_customer_email,
        c.phone as final_customer_phone,
        count(j.id) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as customer_job_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (
            where j.opportunity_status in ('BOOKED', 'CLOSED')
        ) as customer_revenue,
        min(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as first_customer_job_date
    from
        leads_with_bookings lwb
    left join
        customers c on coalesce(lwb.booked_customer_id, lwb.customer_id) = c.id
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
    group by
        lwb.quote_number,
        lwb.lead_id,
        lwb.lead_source,
        lwb.lead_status,
        lwb.sales_person,
        lwb.branch_name,
        lwb.referral_source,
        lwb.time_to_contact,
        lwb.lead_created_at,
        lwb.customer_id,
        lwb.customer_name,
        lwb.customer_email,
        lwb.customer_phone,
        lwb.booked_opportunity_id,
        lwb.booked_opportunity_status,
        lwb.booked_customer_id,
        lwb.booked_date,
        lwb.booked_sales_person,
        lwb.booked_branch_name,
        c.id,
        c.name,
        c.email,
        c.phone
)
select
    quote_number,
    lead_id,
    lead_source,
    lead_status,
    sales_person as lead_sales_person,
    branch_name as lead_branch_name,
    referral_source as lead_referral_source,
    time_to_contact,
    lead_created_at,
    -- Booked opportunity information
    booked_opportunity_id,
    booked_opportunity_status,
    booked_customer_id,
    booked_date,
    booked_sales_person,
    booked_branch_name,
    -- Final customer information
    final_customer_id,
    final_customer_name,
    final_customer_email,
    final_customer_phone,
    customer_job_count,
    customer_revenue,
    first_customer_job_date,
    -- Journey classification
    case
        when customer_job_count > 0 then 'Lead → Customer (Converted)'
        when booked_opportunity_id is not null and final_customer_id is not null then 'Lead → Booked → Customer (Pending Jobs)'
        when booked_opportunity_id is not null then 'Lead → Booked (Not Yet Customer)'
        when lead_status = 'Lost' then 'Lead → Lost'
        when lead_status = 'Bad Lead' then 'Lead → Bad Lead'
        else 'Lead → Active'
    end as journey_status,
    -- Time to conversion
    case
        when first_customer_job_date is not null
        and lead_created_at is not null
        then first_customer_job_date - lead_created_at
        else null
    end as days_to_customer_conversion,
    case
        when booked_date is not null
        and lead_created_at is not null
        then booked_date - lead_created_at
        else null
    end as days_to_booking
from
    leads_with_customer_jobs
order by
    customer_revenue desc nulls last,
    first_customer_job_date desc nulls last,
    booked_date desc nulls last,
    lead_created_at desc;

