-- Customer Preferences Analysis
-- Preferred job types, timing, locations, and other patterns

with customer_preferences as (
    select
        c.id as customer_id,
        c.name as customer_name,
        count(distinct j.id) as total_jobs,
        -- Job type preferences
        mode() within group (order by j.job_type) as preferred_job_type,
        count(distinct j.job_type) as job_types_used,
        -- Location preferences
        mode() within group (order by j.origin_city) as preferred_origin_city,
        mode() within group (order by j.destination_city) as preferred_destination_city,
        mode() within group (order by j.branch_name) as preferred_branch,
        count(distinct j.branch_name) as branches_used,
        -- Timing preferences
        mode() within group (order by extract(month from j.job_date)) as preferred_month,
        mode() within group (order by extract(dow from j.job_date)) as preferred_day_of_week,
        -- Sales person preferences
        mode() within group (order by j.sales_person_name) as preferred_sales_person,
        count(distinct j.sales_person_name) as sales_people_used,
        -- Referral source preferences
        mode() within group (order by j.referral_source) as preferred_referral_source,
        count(distinct j.referral_source) as referral_sources_used,
        -- Revenue patterns
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
        avg(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
        min(j.job_date) as first_job_date,
        max(j.job_date) as last_job_date
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and j.opportunity_status in ('BOOKED', 'CLOSED')
    group by
        c.id, c.name
)
select
    customer_id,
    customer_name,
    total_jobs,
    preferred_job_type,
    job_types_used,
    preferred_origin_city,
    preferred_destination_city,
    preferred_branch,
    branches_used,
    preferred_month,
    case preferred_day_of_week
        when 0 then 'Sunday'
        when 1 then 'Monday'
        when 2 then 'Tuesday'
        when 3 then 'Wednesday'
        when 4 then 'Thursday'
        when 5 then 'Friday'
        when 6 then 'Saturday'
    end as preferred_day_of_week_name,
    preferred_sales_person,
    sales_people_used,
    preferred_referral_source,
    referral_sources_used,
    round(total_revenue::numeric, 2) as total_revenue,
    round(avg_job_value::numeric, 2) as avg_job_value,
    first_job_date,
    last_job_date,
    case
        when job_types_used = 1 then 'single_type'
        when job_types_used <= 3 then 'few_types'
        else 'varied_types'
    end as job_type_preference_category,
    case
        when branches_used = 1 then 'single_branch'
        when branches_used <= 3 then 'few_branches'
        else 'multiple_branches'
    end as branch_preference_category
from
    customer_preferences
where
    total_jobs > 0
order by
    total_revenue desc,
    total_jobs desc;

