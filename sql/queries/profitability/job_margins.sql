-- Job Margins Analysis
-- Calculate profit margins per job (actual vs estimated)
-- Margin = (Actual Cost - Estimated Cost) / Estimated Cost * 100

select
    j.id,
    j.job_id,
    j.job_number,
    j.job_date,
    j.branch_name,
    j.job_type,
    j.opportunity_status,
    j.total_estimated_cost,
    j.total_actual_cost,
    coalesce(j.total_actual_cost, j.total_estimated_cost, 0) as revenue,
    coalesce(j.total_actual_cost, j.total_estimated_cost, 0) - coalesce(j.total_estimated_cost, 0) as margin_amount,
    case
        when j.total_estimated_cost > 0 then
            round(((coalesce(j.total_actual_cost, j.total_estimated_cost, 0) - j.total_estimated_cost)::numeric / j.total_estimated_cost * 100), 2)
        else null
    end as margin_percent,
    case
        when j.total_estimated_cost > 0 and coalesce(j.total_actual_cost, j.total_estimated_cost, 0) > j.total_estimated_cost then 'over_estimate'
        when j.total_estimated_cost > 0 and coalesce(j.total_actual_cost, j.total_estimated_cost, 0) < j.total_estimated_cost then 'under_estimate'
        else 'on_target'
    end as estimate_accuracy
from
    jobs j
where
    j.is_duplicate = false
    and j.opportunity_status in ('BOOKED', 'CLOSED')
    and j.total_estimated_cost is not null
order by
    j.job_date desc nulls last,
    margin_percent desc nulls last;

