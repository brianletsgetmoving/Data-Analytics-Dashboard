-- Sales Person Specialization Analysis
-- Identify sales person specialization patterns by job type, branch, and customer segment

with sales_specialization as (
    select
        sp.id as sales_person_id,
        sp.name as sales_person_name,
        j.job_type,
        j.branch_name,
        count(distinct j.id) as total_jobs,
        count(distinct j.customer_id) as customer_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        count(distinct bo.id) as booked_opportunities,
        count(distinct ls.id) as total_leads
    from
        sales_persons sp
    inner join
        jobs j on sp.id = j.sales_person_id
    left join
        booked_opportunities bo on sp.id = bo.sales_person_id
    left join
        lead_status ls on sp.id = ls.sales_person_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        sp.id,
        sp.name,
        j.job_type,
        j.branch_name
),
specialization_summary as (
    select
        sales_person_id,
        sales_person_name,
        count(distinct job_type) as job_types_handled,
        count(distinct branch_name) as branches_worked,
        sum(total_jobs) as total_jobs,
        sum(customer_count) as total_customers,
        sum(total_revenue) as total_revenue,
        sum(booked_opportunities) as total_booked_opportunities,
        sum(total_leads) as total_leads,
        mode() within group (order by job_type) as primary_job_type,
        mode() within group (order by branch_name) as primary_branch
    from
        sales_specialization
    group by
        sales_person_id,
        sales_person_name
)
select
    sales_person_name,
    job_types_handled,
    branches_worked,
    total_jobs,
    total_customers,
    round(total_revenue::numeric, 2) as total_revenue,
    total_booked_opportunities,
    total_leads,
    primary_job_type,
    primary_branch,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job,
    round((total_booked_opportunities::numeric / nullif(total_leads, 0) * 100), 2) as conversion_rate,
    case
        when job_types_handled = 1 and branches_worked = 1 then 'highly_specialized'
        when job_types_handled <= 2 and branches_worked <= 2 then 'specialized'
        when job_types_handled <= 4 and branches_worked <= 3 then 'moderately_diverse'
        else 'diverse'
    end as specialization_level
from
    specialization_summary
order by
    total_revenue desc;

