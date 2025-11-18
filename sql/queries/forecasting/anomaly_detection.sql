-- Anomaly Detection
-- Detect anomalies in revenue, job volumes, etc.

with monthly_metrics as (
    select
        date_trunc('month', job_date) as month,
        count(*) as job_count,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as revenue,
        count(distinct customer_id) as unique_customers,
        avg(coalesce(total_actual_cost, total_estimated_cost, 0)) as avg_job_value
    from
        jobs
    where
        is_duplicate = false
        and job_date is not null
        and opportunity_status in ('BOOKED', 'CLOSED')
    group by
        date_trunc('month', job_date)
),
statistical_analysis as (
    select
        month,
        job_count,
        round(revenue::numeric, 2) as revenue,
        unique_customers,
        round(avg_job_value::numeric, 2) as avg_job_value,
        -- Statistical measures
        avg(job_count) over () as mean_jobs,
        stddev(job_count) over () as stddev_jobs,
        avg(revenue) over () as mean_revenue,
        stddev(revenue) over () as stddev_revenue,
        avg(avg_job_value) over () as mean_job_value,
        stddev(avg_job_value) over () as stddev_job_value,
        -- Percentiles
        percentile_cont(0.25) within group (order by job_count) over () as p25_jobs,
        percentile_cont(0.75) within group (order by job_count) over () as p75_jobs,
        percentile_cont(0.25) within group (order by revenue) over () as p25_revenue,
        percentile_cont(0.75) within group (order by revenue) over () as p75_revenue
    from
        monthly_metrics
),
anomaly_detection as (
    select
        month,
        job_count,
        revenue,
        unique_customers,
        avg_job_value,
        mean_jobs,
        stddev_jobs,
        mean_revenue,
        stddev_revenue,
        mean_job_value,
        stddev_job_value,
        p25_jobs,
        p75_jobs,
        p25_revenue,
        p75_revenue,
        -- Z-score calculations
        case
            when stddev_jobs > 0 then
                round(((job_count - mean_jobs) / stddev_jobs)::numeric, 2)
            else null
        end as z_score_jobs,
        case
            when stddev_revenue > 0 then
                round(((revenue - mean_revenue) / stddev_revenue)::numeric, 2)
            else null
        end as z_score_revenue,
        -- IQR method
        p75_jobs - p25_jobs as iqr_jobs,
        p75_revenue - p25_revenue as iqr_revenue,
        -- Anomaly flags
        case
            when stddev_jobs > 0 and abs((job_count - mean_jobs) / stddev_jobs) > 2 then true
            when job_count < (p25_jobs - 1.5 * (p75_jobs - p25_jobs)) or job_count > (p75_jobs + 1.5 * (p75_jobs - p25_jobs)) then true
            else false
        end as is_job_anomaly,
        case
            when stddev_revenue > 0 and abs((revenue - mean_revenue) / stddev_revenue) > 2 then true
            when revenue < (p25_revenue - 1.5 * (p75_revenue - p25_revenue)) or revenue > (p75_revenue + 1.5 * (p75_revenue - p25_revenue)) then true
            else false
        end as is_revenue_anomaly
    from
        statistical_analysis
)
select
    month,
    job_count,
    revenue,
    unique_customers,
    avg_job_value,
    round(mean_jobs::numeric, 2) as mean_jobs,
    round(stddev_jobs::numeric, 2) as stddev_jobs,
    round(mean_revenue::numeric, 2) as mean_revenue,
    round(stddev_revenue::numeric, 2) as stddev_revenue,
    z_score_jobs,
    z_score_revenue,
    round(iqr_jobs::numeric, 2) as iqr_jobs,
    round(iqr_revenue::numeric, 2) as iqr_revenue,
    is_job_anomaly,
    is_revenue_anomaly,
    case
        when is_job_anomaly or is_revenue_anomaly then 'anomaly_detected'
        else 'normal'
    end as anomaly_status,
    case
        when is_job_anomaly and job_count > mean_jobs then 'high_job_volume'
        when is_job_anomaly and job_count < mean_jobs then 'low_job_volume'
        when is_revenue_anomaly and revenue > mean_revenue then 'high_revenue'
        when is_revenue_anomaly and revenue < mean_revenue then 'low_revenue'
        else null
    end as anomaly_type
from
    anomaly_detection
order by
    month desc;

