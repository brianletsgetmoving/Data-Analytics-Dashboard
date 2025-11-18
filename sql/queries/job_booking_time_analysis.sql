-- Job Booking Time Analysis
-- Time from quote creation to booking

select
    id,
    job_id,
    job_number,
    customer_id,
    opportunity_status,
    created_at_utc as quote_created,
    booked_at_utc as booked_date,
    booked_at_utc - created_at_utc as time_to_booking,
    extract(epoch from (booked_at_utc - created_at_utc)) / 3600 as hours_to_booking,
    extract(epoch from (booked_at_utc - created_at_utc)) / 86400 as days_to_booking,
    case
        when extract(epoch from (booked_at_utc - created_at_utc)) / 3600 <= 24 then 'Same Day'
        when extract(epoch from (booked_at_utc - created_at_utc)) / 3600 <= 48 then '1-2 Days'
        when extract(epoch from (booked_at_utc - created_at_utc)) / 3600 <= 168 then '3-7 Days'
        when extract(epoch from (booked_at_utc - created_at_utc)) / 3600 <= 720 then '1-4 Weeks'
        else 'Over 4 Weeks'
    end as booking_time_category
from
    jobs
where
    is_duplicate = false
    and opportunity_status in ('BOOKED', 'CLOSED')
    and created_at_utc is not null
    and booked_at_utc is not null
order by
    time_to_booking desc;

