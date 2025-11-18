-- Sales Person Cross-Module Analysis
-- Links SalesPerformance to Jobs, BookedOpportunities, and LeadStatus using name matching
-- Provides comprehensive view of sales person performance across all modules

with sales_person_jobs as (
    -- Aggregate job data by sales person name
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
sales_person_booked_opportunities as (
    -- Aggregate booked opportunities by sales person
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
sales_person_lead_status as (
    -- Aggregate lead status by sales person
    select
        ls.sales_person,
        count(ls.id) as total_leads,
        count(distinct ls.quote_number) as unique_quote_numbers,
        count(distinct ls.branch_name) as branches_worked,
        count(distinct ls.referral_source) as referral_sources
    from
        lead_status ls
    where
        ls.sales_person is not null
    group by
        ls.sales_person
),
all_sales_person_names as (
    -- Get all unique sales person names from all sources
    select distinct sales_person_name as name from jobs where sales_person_name is not null
    union
    select distinct sales_person as name from booked_opportunities where sales_person is not null
    union
    select distinct sales_person as name from lead_status where sales_person is not null
    union
    select distinct name from sales_performance where name is not null
)
select
    spn.name as sales_person_name,
    -- Sales performance metrics (from sales_performance table)
    sp.name as sales_performance_name,
    sp.leads_received,
    sp.bad,
    sp.percent_bad,
    sp.sent,
    sp.percent_sent,
    sp.pending,
    sp.percent_pending,
    sp.booked,
    sp.percent_booked,
    sp.lost,
    sp.percent_lost,
    sp.cancelled,
    sp.percent_cancelled,
    sp.booked_total,
    sp.average_booking,
    -- Job metrics
    coalesce(spj.total_customer_jobs, 0) as total_customer_jobs,
    coalesce(spj.booked_jobs, 0) as booked_jobs,
    coalesce(spj.closed_jobs, 0) as closed_jobs,
    coalesce(spj.lost_jobs, 0) as lost_jobs,
    coalesce(spj.quoted_jobs, 0) as quoted_jobs,
    coalesce(spj.total_job_revenue, 0) as total_job_revenue,
    coalesce(spj.unique_customers, 0) as unique_customers_from_jobs,
    -- Booked opportunity metrics
    coalesce(spbo.total_booked_opportunities, 0) as total_booked_opportunities,
    coalesce(spbo.booked_opportunities_with_customers, 0) as booked_opportunities_with_customers,
    coalesce(spbo.total_opportunity_revenue, 0) as total_opportunity_revenue,
    coalesce(spbo.unique_customers_from_opportunities, 0) as unique_customers_from_opportunities,
    -- Lead status metrics
    coalesce(spls.total_leads, 0) as total_leads_from_lead_status,
    coalesce(spls.unique_quote_numbers, 0) as unique_quote_numbers,
    coalesce(spls.branches_worked, 0) as branches_worked,
    coalesce(spls.referral_sources, 0) as referral_sources,
    -- Cross-module totals
    coalesce(spj.unique_customers, 0) + coalesce(spbo.unique_customers_from_opportunities, 0) as total_unique_customers,
    coalesce(spj.total_job_revenue, 0) + coalesce(spbo.total_opportunity_revenue, 0) as total_revenue_all_modules
from
    all_sales_person_names spn
left join
    sales_performance sp on lower(trim(spn.name)) = lower(trim(sp.name))
left join
    sales_person_jobs spj on lower(trim(spn.name)) = lower(trim(spj.sales_person_name))
left join
    sales_person_booked_opportunities spbo on lower(trim(spn.name)) = lower(trim(spbo.sales_person))
left join
    sales_person_lead_status spls on lower(trim(spn.name)) = lower(trim(spls.sales_person))
order by
    total_revenue_all_modules desc nulls last,
    total_unique_customers desc nulls last,
    sales_person_name;

