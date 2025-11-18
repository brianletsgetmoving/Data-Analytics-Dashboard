-- Gender Revenue Analysis
-- Revenue patterns and job value analysis by customer gender

with gender_revenue_metrics as (
    select
        c.gender,
        count(distinct c.id) as customer_count,
        count(distinct j.id) as job_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        percentile_cont(0.5) within group (order by coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as median_job_value,
        percentile_cont(0.25) within group (order by coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as p25_job_value,
        percentile_cont(0.75) within group (order by coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as p75_job_value,
        min(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as min_job_value,
        max(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as max_job_value,
        sum(case when j.opportunity_status = 'BOOKED' 
            then coalesce(j.total_actual_cost, j.total_estimated_cost, 0) else 0 end) as booked_revenue,
        sum(case when j.opportunity_status = 'CLOSED' 
            then coalesce(j.total_actual_cost, j.total_estimated_cost, 0) else 0 end) as closed_revenue
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
        and c.gender is not null
    group by
        c.gender
)
select
    gender::text as gender,
    customer_count,
    job_count,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    round(median_job_value::numeric, 2) as median_job_value,
    round(p25_job_value::numeric, 2) as p25_job_value,
    round(p75_job_value::numeric, 2) as p75_job_value,
    round(min_job_value::numeric, 2) as min_job_value,
    round(max_job_value::numeric, 2) as max_job_value,
    round(booked_revenue::numeric, 2) as booked_revenue,
    round(closed_revenue::numeric, 2) as closed_revenue,
    round((total_revenue / nullif(customer_count, 0))::numeric, 2) as revenue_per_customer,
    round((total_revenue / nullif(job_count, 0))::numeric, 2) as revenue_per_job
from
    gender_revenue_metrics
order by
    total_revenue desc;

