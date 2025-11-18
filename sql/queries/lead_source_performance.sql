-- Lead Source Performance
-- Performance metrics by referral source

with job_leads as (
    select
        referral_source,
        affiliate_name,
        count(*) as total_leads,
        count(*) filter (where opportunity_status = 'QUOTED') as quoted,
        count(*) filter (where opportunity_status = 'BOOKED') as booked,
        count(*) filter (where opportunity_status = 'CLOSED') as closed,
        count(*) filter (where opportunity_status = 'LOST') as lost,
        sum(coalesce(total_actual_cost, total_estimated_cost, 0)) as total_revenue
    from
        jobs
    where
        is_duplicate = false
        and referral_source is not null
    group by
        referral_source,
        affiliate_name
),
booked_opp_leads as (
    select
        referral_source,
        null as affiliate_name,
        count(*) as total_leads,
        count(*) filter (where status in ('Quoted', 'Pending')) as quoted,
        count(*) filter (where status in ('Booked', 'Closed')) as booked,
        count(*) filter (where status = 'Closed') as closed,
        count(*) filter (where status = 'Lost') as lost,
        sum(coalesce(invoiced_amount, estimated_amount, 0)) as total_revenue
    from
        booked_opportunities
    where
        referral_source is not null
    group by
        referral_source
)
select
    referral_source,
    affiliate_name,
    sum(total_leads) as total_leads,
    sum(quoted) as quoted,
    sum(booked) as booked,
    sum(closed) as closed,
    sum(lost) as lost,
    sum(total_revenue) as total_revenue,
    round(sum(booked)::numeric / nullif(sum(total_leads), 0) * 100, 2) as booking_rate_percent,
    round(sum(closed)::numeric / nullif(sum(booked), 0) * 100, 2) as completion_rate_percent,
    round(sum(total_revenue) / nullif(sum(booked), 0), 2) as avg_booking_value
from
    (
        select * from job_leads
        union all
        select * from booked_opp_leads
    ) combined
group by
    referral_source,
    affiliate_name
order by
    total_revenue desc;

