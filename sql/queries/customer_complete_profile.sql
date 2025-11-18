-- Customer Complete Profile
-- Complete customer profile with all related entities across all modules
-- Provides a 360-degree view of each customer

with customer_jobs_detail as (
    -- All jobs for customer (booked/closed only - customers, not leads)
    select
        c.id as customer_id,
        json_agg(
            json_build_object(
                'job_id', j.id,
                'job_number', j.job_number,
                'job_date', j.job_date,
                'status', j.opportunity_status,
                'branch_name', j.branch_name,
                'sales_person', j.sales_person_name,
                'revenue', coalesce(j.total_actual_cost, j.total_estimated_cost, 0)
            )
            order by j.job_date desc
        ) as jobs,
        count(j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_job_revenue
    from
        customers c
    left join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id
),
customer_bad_leads_detail as (
    -- All bad leads for customer
    select
        c.id as customer_id,
        json_agg(
            json_build_object(
                'bad_lead_id', bl.id,
                'provider', bl.provider,
                'move_date', bl.move_date,
                'date_lead_received', bl.date_lead_received,
                'lead_bad_reason', bl.lead_bad_reason
            )
            order by bl.date_lead_received desc
        ) as bad_leads,
        count(bl.id) as total_bad_leads
    from
        customers c
    left join
        bad_leads bl on c.id = bl.customer_id
    group by
        c.id
),
customer_booked_opportunities_detail as (
    -- All booked opportunities for customer
    select
        c.id as customer_id,
        json_agg(
            json_build_object(
                'booked_opportunity_id', bo.id,
                'quote_number', bo.quote_number,
                'status', bo.status,
                'booked_date', bo.booked_date,
                'service_date', bo.service_date,
                'branch_name', bo.branch_name,
                'sales_person', bo.sales_person,
                'revenue', coalesce(bo.invoiced_amount, bo.estimated_amount, 0)
            )
            order by bo.booked_date desc
        ) as booked_opportunities,
        count(bo.id) as total_booked_opportunities,
        sum(coalesce(bo.invoiced_amount, bo.estimated_amount, 0)) as total_opportunity_revenue
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
    group by
        c.id
),
customer_lead_status_detail as (
    -- Lead status records linked via booked opportunities
    select
        c.id as customer_id,
        json_agg(
            distinct json_build_object(
                'lead_status_id', ls.id,
                'quote_number', ls.quote_number,
                'status', ls.status,
                'sales_person', ls.sales_person,
                'branch_name', ls.branch_name,
                'time_to_contact', ls.time_to_contact
            )
        ) as lead_status_records,
        count(distinct ls.id) as total_lead_status_records
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
    left join
        lead_status ls on bo.quote_number = ls.quote_number
    group by
        c.id
),
customer_lost_leads_detail as (
    -- Lost leads linked via booked opportunities
    select
        c.id as customer_id,
        json_agg(
            distinct json_build_object(
                'lost_lead_id', ll.id,
                'quote_number', ll.quote_number,
                'lost_date', ll.lost_date,
                'reason', ll.reason,
                'time_to_first_contact', ll.time_to_first_contact
            )
        ) as lost_leads,
        count(distinct ll.id) as total_lost_leads
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
    left join
        lost_leads ll on bo.quote_number = ll.quote_number
    group by
        c.id
)
select
    c.id as customer_id,
    c.name as customer_name,
    c.email,
    c.phone,
    c.first_name,
    c.last_name,
    c.origin_city,
    c.origin_state,
    c.destination_city,
    c.destination_state,
    c.gender,
    c.created_at as customer_created_at,
    -- Job information
    cjd.jobs,
    coalesce(cjd.total_jobs, 0) as total_jobs,
    coalesce(cjd.total_job_revenue, 0) as total_job_revenue,
    -- Bad lead information
    cbld.bad_leads,
    coalesce(cbld.total_bad_leads, 0) as total_bad_leads,
    -- Booked opportunity information
    cbod.booked_opportunities,
    coalesce(cbod.total_booked_opportunities, 0) as total_booked_opportunities,
    coalesce(cbod.total_opportunity_revenue, 0) as total_opportunity_revenue,
    -- Lead status information
    clsd.lead_status_records,
    coalesce(clsd.total_lead_status_records, 0) as total_lead_status_records,
    -- Lost lead information
    clld.lost_leads,
    coalesce(clld.total_lost_leads, 0) as total_lost_leads,
    -- Customer classification
    case
        when coalesce(cjd.total_jobs, 0) > 0 then 'Customer (Has Jobs)'
        when coalesce(cbod.total_booked_opportunities, 0) > 0 then 'Customer (Has Opportunities)'
        when coalesce(cbld.total_bad_leads, 0) > 0 then 'Lead (Bad Lead)'
        else 'Lead (No Activity)'
    end as customer_type,
    -- Total value
    coalesce(cjd.total_job_revenue, 0) + coalesce(cbod.total_opportunity_revenue, 0) as total_customer_value
from
    customers c
left join
    customer_jobs_detail cjd on c.id = cjd.customer_id
left join
    customer_bad_leads_detail cbld on c.id = cbld.customer_id
left join
    customer_booked_opportunities_detail cbod on c.id = cbod.customer_id
left join
    customer_lead_status_detail clsd on c.id = clsd.customer_id
left join
    customer_lost_leads_detail clld on c.id = clld.customer_id
where
    coalesce(cjd.total_jobs, 0) > 0
    or coalesce(cbld.total_bad_leads, 0) > 0
    or coalesce(cbod.total_booked_opportunities, 0) > 0
order by
    total_customer_value desc nulls last,
    total_jobs desc nulls last,
    customer_name;

