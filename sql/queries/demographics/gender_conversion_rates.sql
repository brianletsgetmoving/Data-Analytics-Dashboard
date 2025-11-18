-- Gender Conversion Rates Analysis
-- Lead to customer conversion rates by gender

with gender_leads as (
    select
        c.gender,
        count(distinct ls.id) as total_leads,
        count(distinct case when bo.id is not null then ls.id end) as converted_leads,
        count(distinct case when bl.id is not null then ls.id end) as bad_leads,
        count(distinct case when ll.id is not null then ls.id end) as lost_leads
    from
        customers c
    left join
        booked_opportunities bo on c.id = bo.customer_id
    left join
        lead_status ls on bo.quote_number = ls.quote_number
    left join
        bad_leads bl on c.id = bl.customer_id
    left join
        lost_leads ll on bo.quote_number = ll.quote_number
    where
        c.gender is not null
    group by
        c.gender
),
gender_jobs as (
    select
        c.gender,
        count(distinct j.id) as total_jobs,
        count(distinct case when j.opportunity_status = 'BOOKED' then j.id end) as booked_jobs,
        count(distinct case when j.opportunity_status = 'CLOSED' then j.id end) as closed_jobs,
        count(distinct case when j.opportunity_status = 'LOST' then j.id end) as lost_jobs,
        count(distinct case when j.opportunity_status = 'QUOTED' then j.id end) as quoted_jobs
    from
        customers c
    inner join
        jobs j on c.id = j.customer_id
    where
        j.is_duplicate = false
        and c.gender is not null
    group by
        c.gender
)
select
    coalesce(gl.gender, gj.gender)::text as gender,
    coalesce(gl.total_leads, 0) as total_leads,
    coalesce(gl.converted_leads, 0) as converted_leads,
    coalesce(gl.bad_leads, 0) as bad_leads,
    coalesce(gl.lost_leads, 0) as lost_leads,
    coalesce(gj.total_jobs, 0) as total_jobs,
    coalesce(gj.booked_jobs, 0) as booked_jobs,
    coalesce(gj.closed_jobs, 0) as closed_jobs,
    coalesce(gj.lost_jobs, 0) as lost_jobs,
    coalesce(gj.quoted_jobs, 0) as quoted_jobs,
    round((coalesce(gl.converted_leads, 0)::numeric / nullif(gl.total_leads, 0) * 100), 2) as lead_conversion_rate,
    round((coalesce(gj.booked_jobs, 0)::numeric / nullif(gj.total_jobs, 0) * 100), 2) as job_booking_rate,
    round((coalesce(gj.closed_jobs, 0)::numeric / nullif(gj.booked_jobs, 0) * 100), 2) as booking_to_closed_rate
from
    gender_leads gl
full outer join
    gender_jobs gj on gl.gender = gj.gender
where
    coalesce(gl.gender, gj.gender) is not null
order by
    coalesce(gl.total_leads, gj.total_jobs, 0) desc;

