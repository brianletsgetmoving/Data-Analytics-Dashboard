-- Merge History Analysis
-- Analyze customer merge patterns and methods from merge_history JSONB field

with merged_customers as (
    select
        c.id as customer_id,
        c.name,
        c.merge_history,
        jsonb_array_length(c.merge_history) as merge_count,
        array_length(c.merged_from_ids, 1) as merged_from_count,
        c.is_primary_record,
        c.gender,
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
        mc.name,
        mc.merge_count,
        mc.merged_from_count,
        jsonb_array_elements(mc.merge_history) as merge_event,
        (jsonb_array_elements(mc.merge_history)->>'method')::text as merge_method,
        (jsonb_array_elements(mc.merge_history)->>'confidence')::numeric as confidence,
        (jsonb_array_elements(mc.merge_history)->>'timestamp')::timestamp as merge_timestamp
    from
        merged_customers mc
),
merge_summary as (
    select
        merge_method,
        count(distinct customer_id) as customers_merged,
        count(*) as total_merges,
        round(avg(confidence)::numeric, 2) as avg_confidence,
        round(percentile_cont(0.5) within group (order by confidence)::numeric, 2) as median_confidence,
        min(merge_timestamp) as first_merge,
        max(merge_timestamp) as last_merge
    from
        merge_methods
    where
        merge_method is not null
    group by
        merge_method
)
select
    merge_method,
    customers_merged,
    total_merges,
    avg_confidence,
    median_confidence,
    first_merge,
    last_merge,
    round((customers_merged::numeric / sum(customers_merged) over () * 100), 2) as percentage_of_merges
from
    merge_summary
order by
    total_merges desc;

