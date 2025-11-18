-- Sales Person Benchmarking
-- Sales person performance vs averages

with sales_person_metrics as (
    select
        sales_person_name,
        sales_person_id,
        count(*) as total_jobs,
        count(distinct customer_id) as unique_customers,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value,
        count(*) filter (where opportunity_status = 'BOOKED') as booked_jobs,
        count(*) filter (where opportunity_status = 'CLOSED') as closed_jobs,
        count(*) filter (where opportunity_status = 'LOST') as lost_jobs,
        count(distinct branch_name) as branches_worked
    from
        jobs
    where
        is_duplicate = false
        and sales_person_name is not null
        and opportunity_status in ('BOOKED', 'CLOSED', 'LOST')
    group by
        sales_person_name,
        sales_person_id
),
industry_averages as (
    select
        avg(total_jobs) as industry_avg_jobs,
        avg(total_revenue) as industry_avg_revenue,
        avg(avg_job_value) as industry_avg_job_value,
        avg((booked_jobs::numeric / nullif(total_jobs, 0) * 100)) as industry_avg_booking_rate,
        avg((closed_jobs::numeric / nullif(total_jobs, 0) * 100)) as industry_avg_closing_rate,
        avg((total_revenue / nullif(total_jobs, 0))) as industry_avg_revenue_per_job
    from
        sales_person_metrics
)
select
    spm.sales_person_name,
    spm.sales_person_id,
    spm.total_jobs,
    spm.unique_customers,
    round(spm.total_revenue::numeric, 2) as total_revenue,
    round(spm.avg_job_value::numeric, 2) as avg_job_value,
    spm.booked_jobs,
    spm.closed_jobs,
    spm.lost_jobs,
    spm.branches_worked,
    round((spm.booked_jobs::numeric / nullif(spm.total_jobs, 0) * 100), 2) as booking_rate_percent,
    round((spm.closed_jobs::numeric / nullif(spm.total_jobs, 0) * 100), 2) as closing_rate_percent,
    round((spm.lost_jobs::numeric / nullif(spm.total_jobs, 0) * 100), 2) as loss_rate_percent,
    round((spm.total_revenue / nullif(spm.total_jobs, 0))::numeric, 2) as revenue_per_job,
    round((spm.total_revenue / nullif(spm.unique_customers, 0))::numeric, 2) as revenue_per_customer,
    -- Industry benchmarks
    round(ia.industry_avg_jobs::numeric, 2) as industry_avg_jobs,
    round(ia.industry_avg_revenue::numeric, 2) as industry_avg_revenue,
    round(ia.industry_avg_job_value::numeric, 2) as industry_avg_job_value,
    round(ia.industry_avg_booking_rate::numeric, 2) as industry_avg_booking_rate,
    round(ia.industry_avg_closing_rate::numeric, 2) as industry_avg_closing_rate,
    -- Performance vs industry
    round(((spm.total_jobs - ia.industry_avg_jobs) / nullif(ia.industry_avg_jobs, 0) * 100)::numeric, 2) as jobs_vs_industry_percent,
    round(((spm.total_revenue - ia.industry_avg_revenue) / nullif(ia.industry_avg_revenue, 0) * 100)::numeric, 2) as revenue_vs_industry_percent,
    round(((spm.avg_job_value - ia.industry_avg_job_value) / nullif(ia.industry_avg_job_value, 0) * 100)::numeric, 2) as job_value_vs_industry_percent,
    round(((spm.booked_jobs::numeric / nullif(spm.total_jobs, 0) * 100) - ia.industry_avg_booking_rate)::numeric, 2) as booking_rate_vs_industry,
    case
        when spm.total_revenue > ia.industry_avg_revenue * 1.2 then 'top_performer'
        when spm.total_revenue > ia.industry_avg_revenue * 1.1 then 'above_average'
        when spm.total_revenue < ia.industry_avg_revenue * 0.9 then 'below_average'
        else 'average'
    end as performance_category
from
    sales_person_metrics spm,
    industry_averages ia
order by
    spm.total_revenue desc;

