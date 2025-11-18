-- Customer Data Completeness
-- Customer record completeness (email, phone, address)

select
    count(*) as total_customers,
    count(email) as customers_with_email,
    count(phone) as customers_with_phone,
    count(origin_city) as customers_with_origin_city,
    count(origin_state) as customers_with_origin_state,
    count(origin_address) as customers_with_origin_address,
    count(destination_city) as customers_with_destination_city,
    count(destination_state) as customers_with_destination_state,
    count(destination_address) as customers_with_destination_address,
    count(case when email is not null and phone is not null then 1 end) as customers_with_both_email_phone,
    count(case when origin_city is not null and destination_city is not null then 1 end) as customers_with_both_locations,
    round(count(email)::numeric / nullif(count(*), 0) * 100, 2) as email_completeness_percent,
    round(count(phone)::numeric / nullif(count(*), 0) * 100, 2) as phone_completeness_percent,
    round(count(origin_city)::numeric / nullif(count(*), 0) * 100, 2) as origin_city_completeness_percent,
    round(count(destination_city)::numeric / nullif(count(*), 0) * 100, 2) as destination_city_completeness_percent
from
    customers;

