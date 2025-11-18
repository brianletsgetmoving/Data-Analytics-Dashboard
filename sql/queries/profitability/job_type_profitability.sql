-- Job Type Profitability Analysis
-- Profitability analysis by job type

select
    j.job_type,
    count(*) as total_jobs,
    count(*) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
    sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
    sum(coalesce(j.total_estimated_cost, 0)) as total_estimated,
    sum(coalesce(j.total_actual_cost, 0)) as total_actual,
    avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
    percentile_cont(0.5) within group (order by coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as median_job_value,
    round((sum(coalesce(j.total_actual_cost, 0)) - sum(coalesce(j.total_estimated_cost, 0)))::numeric, 2) as variance_amount,
    case
        when sum(coalesce(j.total_estimated_cost, 0)) > 0 then
            round(((sum(coalesce(j.total_actual_cost, 0)) - sum(coalesce(j.total_estimated_cost, 0)))::numeric / sum(coalesce(j.total_estimated_cost, 0)) * 100), 2)
        else null
    end as variance_percent,
    sum(coalesce(j.actual_number_crew, 0)) as total_crew_hours,
    sum(coalesce(j.actual_number_trucks, 0)) as total_truck_hours,
    round((sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) / nullif(sum(coalesce(j.actual_number_crew, 0)), 0))::numeric, 2) as revenue_per_crew_hour,
    round((sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) / nullif(sum(coalesce(j.actual_number_trucks, 0)), 0))::numeric, 2) as revenue_per_truck_hour
from
    jobs j
where
    j.is_duplicate = false
    and j.job_type is not null
group by
    j.job_type
having
    count(*) > 0
order by
    total_revenue desc;

