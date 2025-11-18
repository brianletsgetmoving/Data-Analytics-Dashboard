-- Advanced Customer Segmentation (RFM Analysis)
-- Recency, Frequency, Monetary value segmentation

with customer_rfm as (
    select
        c.id as customer_id,
        c.name as customer_name,
        c.email,
        c.phone,
        max(j.job_date) as last_job_date,
        extract(epoch from (current_date - max(j.job_date))) / 86400 as recency_days,
        count(distinct j.id) as frequency_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as monetary_value,
        count(distinct date_trunc('month', j.job_date)) as frequency_months,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id, c.name, c.email, c.phone
),
rfm_scores as (
    select
        customer_id,
        customer_name,
        email,
        phone,
        last_job_date,
        recency_days,
        frequency_jobs,
        frequency_months,
        round(monetary_value::numeric, 2) as monetary_value,
        round(avg_job_value::numeric, 2) as avg_job_value,
        -- Recency score (1-5, 5 = most recent)
        case
            when recency_days <= 30 then 5
            when recency_days <= 90 then 4
            when recency_days <= 180 then 3
            when recency_days <= 365 then 2
            else 1
        end as recency_score,
        -- Frequency score (1-5, 5 = most frequent)
        case
            when frequency_jobs >= 10 then 5
            when frequency_jobs >= 5 then 4
            when frequency_jobs >= 3 then 3
            when frequency_jobs >= 2 then 2
            else 1
        end as frequency_score,
        -- Monetary score (1-5, 5 = highest value)
        case
            when monetary_value >= 5000 then 5
            when monetary_value >= 2000 then 4
            when monetary_value >= 1000 then 3
            when monetary_value >= 500 then 2
            else 1
        end as monetary_score
    from
        customer_rfm
),
rfm_segments as (
    select
        customer_id,
        customer_name,
        email,
        phone,
        last_job_date,
        recency_days,
        frequency_jobs,
        frequency_months,
        monetary_value,
        avg_job_value,
        recency_score,
        frequency_score,
        monetary_score,
        recency_score::text || frequency_score::text || monetary_score::text as rfm_cell,
        case
            when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4 then 'champions'
            when recency_score >= 3 and frequency_score >= 3 and monetary_score >= 4 then 'loyal_customers'
            when recency_score >= 4 and frequency_score <= 2 and monetary_score >= 3 then 'potential_loyalists'
            when recency_score >= 4 and frequency_score <= 1 and monetary_score <= 2 then 'new_customers'
            when recency_score >= 3 and frequency_score >= 3 and monetary_score <= 3 then 'promising'
            when recency_score <= 2 and frequency_score >= 3 and monetary_score >= 3 then 'needs_attention'
            when recency_score <= 2 and frequency_score >= 2 and monetary_score >= 2 then 'about_to_sleep'
            when recency_score <= 2 and frequency_score <= 2 and monetary_score >= 3 then 'at_risk'
            when recency_score <= 2 and frequency_score <= 2 and monetary_score <= 2 then 'lost'
            else 'other'
        end as rfm_segment
    from
        rfm_scores
)
select
    customer_id,
    customer_name,
    email,
    phone,
    last_job_date,
    recency_days,
    case
        when recency_days is not null then
            round(recency_days::numeric / 30.0, 1)
        else null
    end as recency_months,
    frequency_jobs,
    frequency_months,
    monetary_value,
    avg_job_value,
    recency_score,
    frequency_score,
    monetary_score,
    rfm_cell,
    rfm_segment
from
    rfm_segments
order by
    monetary_value desc,
    recency_score desc,
    frequency_score desc;

