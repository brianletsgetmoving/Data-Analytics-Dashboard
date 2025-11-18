-- Cost Efficiency Metrics
-- Cost per job, cost per customer acquisition, and efficiency ratios

with job_metrics as (
    select
        count(*) as total_jobs,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        sum(coalesce(actual_number_crew, 0)) as total_crew_hours,
        sum(coalesce(actual_number_trucks, 0)) as total_truck_hours,
        sum(coalesce(total_estimated_cost, 0)) as total_estimated_cost
    from
        jobs
    where
        is_duplicate = false
        and opportunity_status in ('BOOKED', 'CLOSED')
),
lead_metrics as (
    select
        count(distinct id) as total_leads,
        count(distinct customer_id) as leads_with_customers
    from
        leads
),
customer_acquisition as (
    select
        count(distinct c.id) as total_customers,
        count(distinct l.id) as customers_from_leads
    from
        customers c
    left join
        lead_statuses ls on c.id = ls.customer_id
    left join
        leads l on ls.lead_id = l.id
)
select
    'overall' as metric_category,
    jm.total_jobs,
    jm.unique_customers,
    round(jm.total_revenue::numeric, 2) as total_revenue,
    round((jm.total_revenue / nullif(jm.total_jobs, 0))::numeric, 2) as cost_per_job,
    round((jm.total_revenue / nullif(jm.unique_customers, 0))::numeric, 2) as cost_per_customer_acquisition,
    round((jm.total_revenue / nullif(jm.total_crew_hours, 0))::numeric, 2) as revenue_per_crew_hour,
    round((jm.total_revenue / nullif(jm.total_truck_hours, 0))::numeric, 2) as revenue_per_truck_hour,
    round((jm.total_estimated_cost / nullif(jm.total_jobs, 0))::numeric, 2) as avg_estimated_cost_per_job,
    lm.total_leads,
    round((lm.leads_with_customers::numeric / nullif(lm.total_leads, 0) * 100), 2) as lead_conversion_rate,
    ca.total_customers,
    round((ca.customers_from_leads::numeric / nullif(ca.total_customers, 0) * 100), 2) as customer_acquisition_from_leads_percent
from
    job_metrics jm,
    lead_metrics lm,
    customer_acquisition ca;

