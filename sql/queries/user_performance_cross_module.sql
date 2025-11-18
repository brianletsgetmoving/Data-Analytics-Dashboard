-- User Performance Cross-Module Analysis
-- Links UserPerformance to Jobs and BookedOpportunities using name matching
-- Provides comprehensive view of user (call center) performance across modules

with user_jobs as (
    -- Aggregate job data by sales person name (users may be sales people too)
    select
        j.sales_person_name,
        count(j.id) filter (where j.opportunity_status in ('BOOKED', 'CLOSED')) as total_customer_jobs,
        count(j.id) filter (where j.opportunity_status = 'BOOKED') as booked_jobs,
        count(j.id) filter (where j.opportunity_status = 'CLOSED') as closed_jobs,
        count(j.id) filter (where j.opportunity_status = 'LOST') as lost_jobs,
        count(j.id) filter (where j.opportunity_status = 'QUOTED') as quoted_jobs,
        sum(coalesce(j.total_actual_cost, j.total_estimated_cost, 0)) filter (
            where j.opportunity_status in ('BOOKED', 'CLOSED')
        ) as total_job_revenue,
        count(distinct j.customer_id) filter (
            where j.opportunity_status in ('BOOKED', 'CLOSED')
        ) as unique_customers
    from
        jobs j
    where
        j.is_duplicate = false
        and j.sales_person_name is not null
    group by
        j.sales_person_name
),
user_booked_opportunities as (
    -- Aggregate booked opportunities by sales person (users may handle these)
    select
        bo.sales_person,
        count(bo.id) as total_booked_opportunities,
        count(bo.customer_id) as booked_opportunities_with_customers,
        sum(coalesce(bo.invoiced_amount, bo.estimated_amount, 0)) as total_opportunity_revenue,
        count(distinct bo.customer_id) as unique_customers_from_opportunities
    from
        booked_opportunities bo
    where
        bo.sales_person is not null
    group by
        bo.sales_person
),
user_lead_status as (
    -- Aggregate lead status by sales person (users may handle leads)
    select
        ls.sales_person,
        count(ls.id) as total_leads_handled,
        count(distinct ls.quote_number) as unique_quote_numbers,
        count(distinct ls.branch_name) as branches_worked
    from
        lead_status ls
    where
        ls.sales_person is not null
    group by
        ls.sales_person
),
all_user_names as (
    -- Get all unique user names from all sources
    select distinct sales_person_name as name from jobs where sales_person_name is not null
    union
    select distinct sales_person as name from booked_opportunities where sales_person is not null
    union
    select distinct sales_person as name from lead_status where sales_person is not null
    union
    select distinct name from user_performance where name is not null
)
select
    aun.name as user_name,
    -- User performance metrics (from user_performance table)
    up.name as user_performance_name,
    up.user_status,
    up.total_calls,
    up.avg_calls_per_day,
    up.inbound_count,
    up.outbound_count,
    up.missed_percent,
    up.avg_handle_time,
    -- Job metrics
    coalesce(uj.total_customer_jobs, 0) as total_customer_jobs,
    coalesce(uj.booked_jobs, 0) as booked_jobs,
    coalesce(uj.closed_jobs, 0) as closed_jobs,
    coalesce(uj.lost_jobs, 0) as lost_jobs,
    coalesce(uj.quoted_jobs, 0) as quoted_jobs,
    coalesce(uj.total_job_revenue, 0) as total_job_revenue,
    coalesce(uj.unique_customers, 0) as unique_customers_from_jobs,
    -- Booked opportunity metrics
    coalesce(ubo.total_booked_opportunities, 0) as total_booked_opportunities,
    coalesce(ubo.booked_opportunities_with_customers, 0) as booked_opportunities_with_customers,
    coalesce(ubo.total_opportunity_revenue, 0) as total_opportunity_revenue,
    coalesce(ubo.unique_customers_from_opportunities, 0) as unique_customers_from_opportunities,
    -- Lead status metrics
    coalesce(uls.total_leads_handled, 0) as total_leads_handled,
    coalesce(uls.unique_quote_numbers, 0) as unique_quote_numbers,
    coalesce(uls.branches_worked, 0) as branches_worked,
    -- Cross-module totals
    coalesce(uj.unique_customers, 0) + coalesce(ubo.unique_customers_from_opportunities, 0) as total_unique_customers,
    coalesce(uj.total_job_revenue, 0) + coalesce(ubo.total_opportunity_revenue, 0) as total_revenue_all_modules,
    -- Performance ratios
    case
        when up.total_calls > 0
        then round(coalesce(uj.total_customer_jobs, 0)::numeric / up.total_calls * 100, 2)
        else null
    end as jobs_per_call_percent,
    case
        when up.total_calls > 0
        then round(coalesce(ubo.total_booked_opportunities, 0)::numeric / up.total_calls * 100, 2)
        else null
    end as opportunities_per_call_percent
from
    all_user_names aun
left join
    user_performance up on lower(trim(aun.name)) = lower(trim(up.name))
left join
    user_jobs uj on lower(trim(aun.name)) = lower(trim(uj.sales_person_name))
left join
    user_booked_opportunities ubo on lower(trim(aun.name)) = lower(trim(ubo.sales_person))
left join
    user_lead_status uls on lower(trim(aun.name)) = lower(trim(uls.sales_person))
order by
    total_revenue_all_modules desc nulls last,
    total_unique_customers desc nulls last,
    user_name;

