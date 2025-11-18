-- Sales Person Customer Analysis
-- Sales person performance broken down by customer relationships
-- Shows how sales people perform across the customer lifecycle

with sales_person_customers as (
    -- Get all customers associated with each sales person through jobs
    select
        j.sales_person_name,
        j.customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(j.id) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as customer_job_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (
            where j.opportunity_status in ('BOOKED', 'CLOSED')
        ) as customer_revenue,
        min(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as first_customer_job_date,
        max(j.job_date) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as last_customer_job_date
    from
        jobs j
    inner join
        customers c on j.customer_id = c.id
    where
        j.is_duplicate = false
        and j.sales_person_name is not null
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        j.sales_person_name, j.customer_id, c.name, c.email, c.phone
),
sales_person_customer_opportunities as (
    -- Get booked opportunities for customers by sales person
    select
        bo.sales_person,
        bo.customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(bo.id) as opportunity_count,
        sum(coalesce(bo.invoiced_amount, bo.estimated_amount, 0)) as opportunity_revenue,
        min(bo.booked_date) as first_opportunity_date
    from
        booked_opportunities bo
    inner join
        customers c on bo.customer_id = c.id
    where
        bo.sales_person is not null
        and bo.customer_id is not null
    group by
        bo.sales_person, bo.customer_id, c.name, c.email, c.phone
),
sales_person_customer_leads as (
    -- Get leads handled by sales person that may become customers
    select
        ls.sales_person,
        bo.customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        count(ls.id) as lead_count,
        min(ls.created_at) as first_lead_date
    from
        lead_status ls
    left join
        booked_opportunities bo on ls.quote_number = bo.quote_number
    left join
        customers c on bo.customer_id = c.id
    where
        ls.sales_person is not null
        and bo.customer_id is not null
    group by
        ls.sales_person, bo.customer_id, c.name, c.email, c.phone
),
sales_person_summary as (
    -- Aggregate sales person performance
    select
        coalesce(spc.sales_person_name, spco.sales_person, spcl.sales_person) as sales_person_name,
        coalesce(spc.customer_id, spco.customer_id, spcl.customer_id) as customer_id,
        coalesce(spc.customer_name, spco.customer_name, spcl.customer_name) as customer_name,
        coalesce(spc.email, spco.email, spcl.email) as customer_email,
        coalesce(spc.phone, spco.phone, spcl.phone) as customer_phone,
        -- Job metrics
        coalesce(spc.customer_job_count, 0) as customer_job_count,
        coalesce(spc.customer_revenue, 0) as customer_revenue,
        spc.first_customer_job_date,
        spc.last_customer_job_date,
        -- Opportunity metrics
        coalesce(spco.opportunity_count, 0) as opportunity_count,
        coalesce(spco.opportunity_revenue, 0) as opportunity_revenue,
        spco.first_opportunity_date,
        -- Lead metrics
        coalesce(spcl.lead_count, 0) as lead_count,
        spcl.first_lead_date
    from
        sales_person_customers spc
    full outer join
        sales_person_customer_opportunities spco on spc.sales_person_name = spco.sales_person
        and spc.customer_id = spco.customer_id
    full outer join
        sales_person_customer_leads spcl on coalesce(spc.sales_person_name, spco.sales_person) = spcl.sales_person
        and coalesce(spc.customer_id, spco.customer_id) = spcl.customer_id
)
select
    sales_person_name,
    customer_id,
    customer_name,
    customer_email,
    customer_phone,
    -- Job metrics
    customer_job_count,
    customer_revenue,
    first_customer_job_date,
    last_customer_job_date,
    -- Opportunity metrics
    opportunity_count,
    opportunity_revenue,
    first_opportunity_date,
    -- Lead metrics
    lead_count,
    first_lead_date,
    -- Customer relationship type
    case
        when customer_job_count > 0 then 'Customer (Has Jobs)'
        when opportunity_count > 0 then 'Customer (Has Opportunities)'
        when lead_count > 0 then 'Lead (Not Yet Customer)'
        else 'Unknown'
    end as customer_relationship_type,
    -- Total value
    customer_revenue + opportunity_revenue as total_customer_value,
    -- Time to conversion
    case
        when first_customer_job_date is not null
        and first_lead_date is not null
        then first_customer_job_date - first_lead_date
        else null
    end as days_from_lead_to_customer
from
    sales_person_summary
where
    customer_id is not null
order by
    sales_person_name,
    total_customer_value desc nulls last,
    customer_name;

