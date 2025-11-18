-- Merge Method Performance Analysis
-- Performance metrics for different customer merge methods

with merged_customers as (
    select
        c.id as customer_id,
        c.name,
        c.merge_history,
        array_length(c.merged_from_ids, 1) as merged_from_count,
        c.first_lead_date,
        c.conversion_date
    from
        customers c
    where
        c.merge_history is not null
        and jsonb_array_length(c.merge_history) > 0
),
merge_methods as (
    select
        mc.customer_id,
        (jsonb_array_elements(mc.merge_history)->>'method')::text as merge_method,
        (jsonb_array_elements(mc.merge_history)->>'confidence')::numeric as confidence
    from
        merged_customers mc
),
customer_metrics as (
    select
        mm.customer_id,
        mm.merge_method,
        mm.confidence,
        count(distinct j.id) as total_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        count(distinct bo.id) as booked_opportunities
    from
        merge_methods mm
    left join
        customers c on mm.customer_id = c.id
    left join
        jobs j on c.id = j.customer_id
    left join
        booked_opportunities bo on c.id = bo.customer_id
    where
        (j.is_duplicate = false or j.id is null)
        and (j.opportunity_status in ('BOOKED', 'CLOSED') or j.id is null)
    group by
        mm.customer_id,
        mm.merge_method,
        mm.confidence
)
select
    merge_method,
    count(distinct customer_id) as customers_merged,
    round(avg(confidence)::numeric, 2) as avg_confidence,
    round(percentile_cont(0.5) within group (order by confidence)::numeric, 2) as median_confidence,
    sum(total_jobs) as total_jobs,
    round(sum(total_revenue)::numeric, 2) as total_revenue,
    sum(booked_opportunities) as total_booked_opportunities,
    round(avg(total_jobs)::numeric, 2) as avg_jobs_per_customer,
    round(avg(total_revenue)::numeric, 2) as avg_revenue_per_customer,
    round((sum(total_revenue) / nullif(sum(total_jobs), 0))::numeric, 2) as revenue_per_job
from
    customer_metrics
where
    merge_method is not null
group by
    merge_method
order by
    customers_merged desc;

