-- Revenue by Sales Person
-- Revenue and average booking value per sales person

select
    sales_person_name,
    count(*) as total_jobs,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
    avg(coalesce(total_actual_cost, total_estimated_cost)) as avg_job_value,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED') as booked_revenue,
    sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'CLOSED') as closed_revenue,
    count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
    count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
    round(sum(coalesce(total_actual_cost, total_estimated_cost, 0)) filter (where opportunity_status = 'BOOKED')::numeric / 
        nullif(count(*) filter (where opportunity_status = 'BOOKED'), 0), 2) as avg_booked_value,
    count(distinct branch_name) as branches_worked,
    count(distinct customer_id) as unique_customers
from
    jobs
where
    is_duplicate = false
    and sales_person_name is not null
group by
    sales_person_name
order by
    total_revenue desc;

