-- Customer Journey Analysis
-- Complete customer journey from lead to repeat customer

with customer_timeline as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        min(l.date_received) as first_lead_date,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date,
        count(distinct l.id) as total_leads,
        count(distinct j.id) as total_jobs,
        count(distinct j.id) filter (where j.opportunity_status = 'QUOTED') as quoted_jobs,
        count(distinct j.id) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(distinct j.id) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        count(distinct j.id) filter (where j.opportunity_status = 'LOST') as lost_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        min(j.job_date) - min(l.date_received) as lead_to_first_job_days
    from
        customers c
    left join
        lead_statuses ls on c.id = ls.customer_id
    left join
        leads l on ls.lead_id = l.id
    left join
        jobs j on c.id = j.customer_id
    where
        (j.is_duplicate = false or j.id is null)
    group by
        c.id, c.name, c.email, c.phone
),
journey_stages as (
    select
        customer_id,
        customer_name,
        email,
        phone,
        first_lead_date,
        first_job_date,
        last_job_date,
        total_leads,
        total_jobs,
        quoted_jobs,
        booked_jobs,
        closed_jobs,
        lost_jobs,
        round(total_revenue::numeric, 2) as total_revenue,
        lead_to_first_job_days,
        case
            when first_lead_date is not null and first_job_date is not null then 'lead_to_customer'
            when first_lead_date is not null and first_job_date is null then 'lead_only'
            when first_lead_date is null and first_job_date is not null then 'direct_customer'
            else 'unknown'
        end as acquisition_path,
        case
            when total_jobs = 0 then 'no_jobs'
            when total_jobs = 1 then 'one_time_customer'
            when total_jobs between 2 and 5 then 'repeat_customer'
            else 'loyal_customer'
        end as customer_type,
        case
            when total_jobs > 0 and closed_jobs > 0 then 'converted'
            when total_jobs > 0 and booked_jobs > 0 then 'active'
            when total_jobs > 0 and quoted_jobs > 0 then 'considering'
            when total_leads > 0 then 'lead_only'
            else 'unknown'
        end as current_stage
    from
        customer_timeline
)
select
    customer_id,
    customer_name,
    email,
    phone,
    first_lead_date,
    first_job_date,
    last_job_date,
    total_leads,
    total_jobs,
    quoted_jobs,
    booked_jobs,
    closed_jobs,
    lost_jobs,
    total_revenue,
    lead_to_first_job_days,
    case
        when lead_to_first_job_days is not null then
            round(lead_to_first_job_days::numeric / 30.0, 1)
        else null
    end as lead_to_first_job_months,
    acquisition_path,
    customer_type,
    current_stage,
    round((closed_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as conversion_rate_percent,
    round((booked_jobs::numeric / nullif(total_jobs, 0) * 100), 2) as booking_rate_percent
from
    journey_stages
where
    total_leads > 0 or total_jobs > 0
order by
    total_revenue desc nulls last,
    total_jobs desc;

