-- Branch Geographic Coverage
-- Branch coverage analysis by city and state

with branch_coverage as (
    select
        b.id as branch_id,
        b.name as branch_name,
        b.city as branch_city,
        b.state as branch_state,
        j.origin_city,
        j.origin_state,
        j.destination_city,
        j.destination_state,
        count(distinct j.id) as job_count,
        count(distinct j.customer_id) as customer_count,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue
    from
        branches b
    inner join
        jobs j on b.id = j.branch_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        b.id,
        b.name,
        b.city,
        b.state,
        j.origin_city,
        j.origin_state,
        j.destination_city,
        j.destination_state
),
branch_summary as (
    select
        branch_id,
        branch_name,
        branch_city,
        branch_state,
        count(distinct origin_city) as origin_cities_served,
        count(distinct origin_state) as origin_states_served,
        count(distinct destination_city) as destination_cities_served,
        count(distinct destination_state) as destination_states_served,
        sum(job_count) as total_jobs,
        sum(customer_count) as total_customers,
        sum(total_revenue) as total_revenue
    from
        branch_coverage
    group by
        branch_id,
        branch_name,
        branch_city,
        branch_state
)
select
    branch_name,
    branch_city,
    branch_state,
    origin_cities_served,
    origin_states_served,
    destination_cities_served,
    destination_states_served,
    total_jobs,
    total_customers,
    round(total_revenue::numeric, 2) as total_revenue,
    round((total_revenue / nullif(total_jobs, 0))::numeric, 2) as revenue_per_job
from
    branch_summary
order by
    total_revenue desc;

