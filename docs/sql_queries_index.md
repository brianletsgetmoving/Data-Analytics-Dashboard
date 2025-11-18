# SQL Queries Index

This document provides an index of all SQL queries available in the `sql/queries/` directory, organized by category.

## Customer Analysis Queries

### customer_relationship_summary.sql
- **Purpose**: Overview of all customer relationships across jobs, bad leads, and booked opportunities
- **Key Outputs**: Customer ID, job counts, bad lead counts, booked opportunity counts, customer type classification
- **Relationships Used**: Customer → Jobs, Customer → BadLeads, Customer → BookedOpportunities
- **Optimized**: Changed LEFT JOIN to INNER JOIN where appropriate, added HAVING clauses to reduce aggregation overhead

### customer_lead_journey.sql
- **Purpose**: Tracks customer journey from lead to booking/loss across all modules
- **Key Outputs**: Lead source, conversion status, journey stage, time to conversion
- **Relationships Used**: LeadStatus → BookedOpportunity → Customer → Jobs

### customer_bad_lead_analysis.sql
- **Purpose**: Analyzes customers who have bad leads and their job/booking history
- **Key Outputs**: Bad lead details, customer conversion metrics, linked quote numbers
- **Relationships Used**: Customer → BadLeads, Customer → Jobs, BadLead → LeadStatus (via matching)

### customer_complete_profile.sql
- **Purpose**: Complete customer profile with all related entities across all modules
- **Key Outputs**: JSON aggregates of jobs, bad leads, booked opportunities, lead status, lost leads
- **Relationships Used**: All customer relationships

### customer_lifetime_value.sql
- **Purpose**: Calculates total revenue, job counts, and lifetime duration per customer
- **Key Outputs**: Customer lifetime value, revenue by status, customer lifetime years
- **Relationships Used**: Customer → Jobs
- **Optimized**: Changed LEFT JOIN to INNER JOIN, added early WHERE filter for opportunity_status

## Lead Analysis Queries

### quote_number_linkage.sql
- **Purpose**: Analyzes quote_number matches between LeadStatus, LostLead, and BookedOpportunity
- **Key Outputs**: Quote number, match type, journey status across all three tables
- **Relationships Used**: LeadStatus ↔ BookedOpportunity, LostLead ↔ BookedOpportunity (via quote_number)

### lead_status_to_customer.sql
- **Purpose**: Links LeadStatus to Customers via BookedOpportunity using quote_number
- **Key Outputs**: Lead status details, booked opportunity info, customer conversion status
- **Relationships Used**: LeadStatus → BookedOpportunity → Customer → Jobs

### lost_lead_to_customer.sql
- **Purpose**: Links LostLead to Customers via BookedOpportunity using quote_number
- **Key Outputs**: Lost lead details, conversion status, time from lost to customer
- **Relationships Used**: LostLead → BookedOpportunity → Customer → Jobs

### lead_to_customer_traceability.sql
- **Purpose**: Traces leads through all modules to customers
- **Key Outputs**: Complete lead journey, conversion status, days to conversion
- **Relationships Used**: All lead relationships (LeadStatus, BadLead, LostLead → BookedOpportunity → Customer)

### lead_conversion_funnel.sql
- **Purpose**: Lead to quote to booking conversion funnel
- **Key Outputs**: Total leads, quoted, booked, closed, lost counts and percentages
- **Relationships Used**: Aggregates across Jobs, BookedOpportunities, BadLeads, LostLeads
- **Optimized**: Combined aggregations, optimized UNION ALL structure

### lead_status_distribution.sql
- **Purpose**: Distribution of leads by status across different sources
- **Key Outputs**: Status distribution by source table (jobs, booked_opportunities, lead_status)
- **Relationships Used**: Aggregates from multiple tables

### lead_response_time.sql
- **Purpose**: Time to first contact analysis
- **Key Outputs**: Response time in minutes, response category
- **Relationships Used**: LeadStatus table

### lead_source_performance.sql
- **Purpose**: Performance analysis by referral source
- **Key Outputs**: Leads, conversions, revenue by referral source
- **Relationships Used**: Jobs, BookedOpportunities, LeadStatus

## Sales Person Performance Queries

### sales_person_cross_module.sql
- **Purpose**: Links SalesPerformance to Jobs, BookedOpportunities, and LeadStatus using name matching
- **Key Outputs**: Sales person performance across all modules, total revenue, unique customers
- **Relationships Used**: SalesPerson → Jobs, SalesPerson → BookedOpportunities, SalesPerson → LeadStatus

### user_performance_cross_module.sql
- **Purpose**: Links UserPerformance to Jobs and BookedOpportunities using name matching
- **Key Outputs**: User performance metrics, job counts, opportunity counts, performance ratios
- **Relationships Used**: SalesPerson → Jobs, SalesPerson → BookedOpportunities

### sales_person_customer_analysis.sql
- **Purpose**: Sales person performance broken down by customer relationships
- **Key Outputs**: Sales person per customer metrics, customer relationship type, total customer value
- **Relationships Used**: SalesPerson → Jobs → Customer, SalesPerson → BookedOpportunities → Customer

### sales_person_performance.sql
- **Purpose**: Comprehensive sales person metrics from sales_performance table
- **Key Outputs**: Leads received, booking rates, revenue metrics
- **Relationships Used**: SalesPerformance table

## Relationship Analysis Queries

### module_relationship_matrix.sql
- **Purpose**: Matrix showing all possible relationships between modules
- **Key Outputs**: Relationship type, source count, target count, linked count, linkage percentage
- **Relationships Used**: All relationships between modules

## Job Analysis Queries

### job_volume_trends.sql
- **Purpose**: Job volume trends over time
- **Key Outputs**: Job counts by time period
- **Relationships Used**: Jobs table

### job_status_distribution.sql
- **Purpose**: Distribution of jobs by status
- **Key Outputs**: Count of jobs by opportunity status
- **Relationships Used**: Jobs table

### job_booking_time_analysis.sql
- **Purpose**: Analysis of time from quote to booking
- **Key Outputs**: Days to booking, booking time categories
- **Relationships Used**: Jobs table

### job_conversion_rates.sql
- **Purpose**: Conversion rates from quoted to booked
- **Key Outputs**: Conversion percentages by various dimensions
- **Relationships Used**: Jobs table

### job_geographic_routes.sql
- **Purpose**: Analysis of geographic routes (origin to destination)
- **Key Outputs**: Route frequency, revenue by route
- **Relationships Used**: Jobs table

### job_estimated_vs_actual_cost.sql
- **Purpose**: Comparison of estimated vs actual costs
- **Key Outputs**: Cost variance, accuracy metrics
- **Relationships Used**: Jobs table

## Revenue Analysis Queries

### revenue_trends.sql
- **Purpose**: Revenue trends over time
- **Key Outputs**: Revenue by time period
- **Relationships Used**: Jobs, BookedOpportunities

### revenue_by_branch.sql
- **Purpose**: Revenue breakdown by branch
- **Key Outputs**: Revenue, job counts by branch
- **Relationships Used**: Jobs, BookedOpportunities

### revenue_by_sales_person.sql
- **Purpose**: Revenue breakdown by sales person
- **Key Outputs**: Revenue, job counts by sales person
- **Relationships Used**: Jobs, BookedOpportunities, SalesPerson

### revenue_by_referral_source.sql
- **Purpose**: Revenue breakdown by referral source
- **Key Outputs**: Revenue, job counts by referral source
- **Relationships Used**: Jobs, BookedOpportunities

## Bad Leads Analysis

### bad_leads_analysis.sql
- **Purpose**: Bad leads count, reasons, and trends
- **Key Outputs**: Bad lead counts by provider and reason
- **Relationships Used**: BadLeads table

## Lost Leads Analysis

### lost_leads_analysis.sql
- **Purpose**: Lost leads with reasons and time to contact
- **Key Outputs**: Lost lead details, days to lost
- **Relationships Used**: LostLeads table

## Geographic Analysis Queries

### geographic_coverage.sql
- **Purpose**: Geographic coverage analysis
- **Key Outputs**: Coverage by city, state
- **Relationships Used**: Jobs, Customers

### top_origin_cities.sql
- **Purpose**: Top origin cities by volume
- **Key Outputs**: City rankings, job counts
- **Relationships Used**: Jobs table

### top_destination_cities.sql
- **Purpose**: Top destination cities by volume
- **Key Outputs**: City rankings, job counts
- **Relationships Used**: Jobs table

### city_to_city_routes.sql
- **Purpose**: Most common city-to-city routes
- **Key Outputs**: Route frequency, revenue
- **Relationships Used**: Jobs table

## Time-Based Analysis Queries

### jobs_by_time_period.sql
- **Purpose**: Jobs grouped by time periods
- **Key Outputs**: Job counts by period
- **Relationships Used**: Jobs table

### monthly_metrics_summary.sql
- **Purpose**: Monthly summary of key metrics
- **Key Outputs**: Jobs, revenue, customers by month
- **Relationships Used**: Jobs, Customers

### quarterly_metrics_summary.sql
- **Purpose**: Quarterly summary of key metrics
- **Key Outputs**: Jobs, revenue, customers by quarter
- **Relationships Used**: Jobs, Customers

### year_over_year_growth.sql
- **Purpose**: Year-over-year growth analysis
- **Key Outputs**: Growth percentages by metric
- **Relationships Used**: Jobs, Customers

### seasonal_job_patterns.sql
- **Purpose**: Seasonal patterns in job volume
- **Key Outputs**: Job counts by season/month
- **Relationships Used**: Jobs table

### rolling_window_jobs.sql
- **Purpose**: Rolling window analysis of jobs
- **Key Outputs**: Job counts in rolling windows
- **Relationships Used**: Jobs table

## Performance Analysis Queries

### performance_trends.sql
- **Purpose**: Performance trends over time
- **Key Outputs**: Key performance indicators over time
- **Relationships Used**: Multiple tables

### operational_efficiency.sql
- **Purpose**: Operational efficiency metrics
- **Key Outputs**: Efficiency ratios and metrics
- **Relationships Used**: Jobs table

### job_crew_truck_utilization.sql
- **Purpose**: Crew and truck utilization analysis
- **Key Outputs**: Utilization rates
- **Relationships Used**: Jobs table

## Data Quality Queries

### data_quality_metrics.sql
- **Purpose**: Data quality metrics across tables
- **Key Outputs**: Completeness, accuracy metrics
- **Relationships Used**: All tables

### job_data_completeness.sql
- **Purpose**: Job data completeness analysis
- **Key Outputs**: Field completeness percentages
- **Relationships Used**: Jobs table

### customer_data_completeness.sql
- **Purpose**: Customer data completeness analysis
- **Key Outputs**: Field completeness percentages
- **Relationships Used**: Customers table

### job_duplicate_rate.sql
- **Purpose**: Duplicate job detection and rates
- **Key Outputs**: Duplicate counts and rates
- **Relationships Used**: Jobs table

### customer_deduplication_stats.sql
- **Purpose**: Customer deduplication statistics
- **Key Outputs**: Merge counts, confidence levels
- **Relationships Used**: Customers, CustomerDeduplicationLog

## Customer Segmentation Queries

### customer_segmentation_by_value.sql
- **Purpose**: Customer segmentation by value
- **Key Outputs**: Customer segments, value ranges
- **Relationships Used**: Customer → Jobs

### repeat_customers.sql
- **Purpose**: Analysis of repeat customers
- **Key Outputs**: Repeat customer counts, frequency
- **Relationships Used**: Customer → Jobs

### customer_retention_rate.sql
- **Purpose**: Customer retention rate analysis
- **Key Outputs**: Retention rates by period
- **Relationships Used**: Customer → Jobs

### customer_acquisition_timeline.sql
- **Purpose**: Customer acquisition timeline
- **Key Outputs**: New customers by time period
- **Relationships Used**: Customers table

### customer_geographic_distribution.sql
- **Purpose**: Customer geographic distribution
- **Key Outputs**: Customer counts by location
- **Relationships Used**: Customers table

### customer_job_frequency.sql
- **Purpose**: Customer job frequency analysis
- **Key Outputs**: Job frequency distributions
- **Relationships Used**: Customer → Jobs

## User Performance Queries

### user_call_performance.sql
- **Purpose**: User call performance metrics
- **Key Outputs**: Call counts, handle times, missed percentages
- **Relationships Used**: UserPerformance table

## Branch Analysis Queries

### branch_performance_comparison.sql
- **Purpose**: Branch performance comparison
- **Key Outputs**: Performance metrics by branch
- **Relationships Used**: Jobs, BookedOpportunities

### job_bookings_by_branch.sql
- **Purpose**: Job bookings by branch
- **Key Outputs**: Booking counts and revenue by branch
- **Relationships Used**: Jobs, BookedOpportunities

## Demographics Analytics Queries

### demographics/gender_distribution.sql
- **Purpose**: Customer gender distribution across all customers and by various segments
- **Key Outputs**: Gender distribution, customer counts, job counts, revenue by gender
- **Relationships Used**: Customer → Jobs
- **New Field Used**: Customer.gender

### demographics/gender_revenue_analysis.sql
- **Purpose**: Revenue patterns and job value analysis by customer gender
- **Key Outputs**: Revenue metrics, percentiles, booking rates by gender
- **Relationships Used**: Customer → Jobs
- **New Field Used**: Customer.gender

### demographics/gender_job_preferences.sql
- **Purpose**: Job type, branch, and service preferences by customer gender
- **Key Outputs**: Preferred job types, branches, timing preferences by gender
- **Relationships Used**: Customer → Jobs
- **New Field Used**: Customer.gender

### demographics/gender_conversion_rates.sql
- **Purpose**: Lead to customer conversion rates by gender
- **Key Outputs**: Conversion rates, booking rates, loss rates by gender
- **Relationships Used**: Customer → LeadStatus → BookedOpportunities → Jobs
- **New Field Used**: Customer.gender

## Data Quality Analytics Queries

### data_quality/merge_history_analysis.sql
- **Purpose**: Analyze customer merge patterns and methods from merge_history JSONB field
- **Key Outputs**: Merge methods, confidence levels, merge frequency
- **Relationships Used**: Customer.merge_history (JSONB)
- **New Field Used**: Customer.merge_history, Customer.mergedFromIds

### data_quality/merge_method_performance.sql
- **Purpose**: Performance metrics for different customer merge methods
- **Key Outputs**: Revenue and job metrics by merge method
- **Relationships Used**: Customer.merge_history → Jobs, BookedOpportunities
- **New Field Used**: Customer.merge_history

### data_quality/duplicate_prevention_insights.sql
- **Purpose**: Patterns in duplicate detection and prevention
- **Key Outputs**: Duplicate patterns by month, branch, sales person, customer
- **Relationships Used**: Jobs.is_duplicate
- **New Field Used**: Job.is_duplicate

## Lead Response & Timing Analytics Queries

### leads/response_time_impact.sql
- **Purpose**: Impact of timeToContact on lead conversion rates
- **Key Outputs**: Conversion rates by response time buckets
- **Relationships Used**: LeadStatus.timeToContact → BookedOpportunities
- **New Field Used**: LeadStatus.timeToContact

### leads/lead_response_performance.sql
- **Purpose**: Response time performance by sales person and branch
- **Key Outputs**: Response times, conversion rates by sales person/branch
- **Relationships Used**: LeadStatus.timeToContact → SalesPerson, Branch
- **New Field Used**: LeadStatus.timeToContact

### leads/optimal_response_time.sql
- **Purpose**: Identify optimal response time windows for maximum conversion
- **Key Outputs**: Conversion rates by response time windows, performance categories
- **Relationships Used**: LeadStatus.timeToContact → BookedOpportunities
- **New Field Used**: LeadStatus.timeToContact

## Win/Loss Analysis Queries

### leads/loss_reason_analysis.sql
- **Purpose**: Analyze LostLead.reason patterns and their impact
- **Key Outputs**: Loss reasons, lost value, frequency by reason
- **Relationships Used**: LostLead.reason → BookedOpportunities
- **New Field Used**: LostLead.reason

### leads/bad_lead_reason_patterns.sql
- **Purpose**: Analyze BadLead.leadBadReason patterns
- **Key Outputs**: Bad lead reasons, patterns by provider and lead source
- **Relationships Used**: BadLead.leadBadReason → LeadSource
- **New Field Used**: BadLead.leadBadReason

### leads/win_loss_by_reason.sql
- **Purpose**: Conversion rates by loss reason category
- **Key Outputs**: Win/loss rates, values by reason
- **Relationships Used**: LostLead.reason → BookedOpportunities
- **New Field Used**: LostLead.reason

## Lead Source Category Analytics Queries

### leads/lead_source_category_performance.sql
- **Purpose**: Performance metrics by LeadSource.category
- **Key Outputs**: Leads, conversions, revenue by category
- **Relationships Used**: LeadSource.category → LeadStatus → BookedOpportunities
- **New Field Used**: LeadSource.category

### leads/category_conversion_funnel.sql
- **Purpose**: Conversion funnel analysis by lead source category
- **Key Outputs**: Funnel metrics by category
- **Relationships Used**: LeadSource.category → LeadStatus → BookedOpportunities
- **New Field Used**: LeadSource.category

### leads/category_customer_lifetime_value.sql
- **Purpose**: Customer lifetime value analysis by lead source category
- **Key Outputs**: LTV metrics by category
- **Relationships Used**: LeadSource.category → Customers → Jobs
- **New Field Used**: LeadSource.category

## Geographic Customer Pattern Queries

### geographic/customer_origin_patterns.sql
- **Purpose**: Customer origin city/state analysis
- **Key Outputs**: Customer counts, revenue by origin location
- **Relationships Used**: Customer.originCity/originState → Jobs
- **New Field Used**: Customer.originCity, Customer.originState

### geographic/customer_destination_patterns.sql
- **Purpose**: Customer destination preferences analysis
- **Key Outputs**: Customer counts, revenue by destination location
- **Relationships Used**: Customer.destinationCity/destinationState → Jobs
- **New Field Used**: Customer.destinationCity, Customer.destinationState

### geographic/origin_destination_correlations.sql
- **Purpose**: Common origin-destination pairs and route patterns
- **Key Outputs**: Route frequency, revenue by origin-destination pairs
- **Relationships Used**: Customer origin/destination → Jobs
- **New Field Used**: Customer.originCity, Customer.destinationCity

### geographic/branch_geographic_coverage.sql
- **Purpose**: Branch coverage analysis by city and state
- **Key Outputs**: Cities/states served, coverage metrics by branch
- **Relationships Used**: Branch.city/state → Jobs
- **New Field Used**: Branch.city, Branch.state

## Affiliate & Referral ROI Queries

### referrals/affiliate_performance.sql
- **Purpose**: affiliateName performance analysis
- **Key Outputs**: Jobs, revenue, booking rates by affiliate
- **Relationships Used**: Job.affiliateName → Jobs
- **New Field Used**: Job.affiliateName

### referrals/referral_source_roi.sql
- **Purpose**: ROI analysis by referral source
- **Key Outputs**: Revenue per lead, conversion rates by referral source
- **Relationships Used**: Job.referralSource → Jobs → BookedOpportunities
- **New Field Used**: Job.referralSource

### referrals/affiliate_customer_lifetime_value.sql
- **Purpose**: Customer lifetime value by affiliate
- **Key Outputs**: LTV metrics by affiliate
- **Relationships Used**: Job.affiliateName → Customers → Jobs
- **New Field Used**: Job.affiliateName

## Advanced Operational Analytics Queries

### operational/crew_truck_utilization_by_route.sql
- **Purpose**: Resource utilization analysis by route type (local, intrastate, interstate)
- **Key Outputs**: Crew/truck utilization, revenue per resource hour by route type
- **Relationships Used**: Jobs → route type calculation
- **New Analysis**: Route type classification

### operational/job_type_geographic_profitability.sql
- **Purpose**: Job type profitability analysis by geographic region
- **Key Outputs**: Profitability metrics by job type and region
- **Relationships Used**: Jobs → geographic regions
- **New Analysis**: Geographic profitability patterns

### operational/sales_person_specialization.sql
- **Purpose**: Identify sales person specialization patterns by job type, branch, and customer segment
- **Key Outputs**: Specialization levels, primary job types/branches per sales person
- **Relationships Used**: SalesPerson → Jobs, BookedOpportunities, LeadStatus
- **New Analysis**: Specialization patterns

### operational/branch_capacity_analysis.sql
- **Purpose**: Branch capacity vs demand analysis
- **Key Outputs**: Capacity metrics, demand variance, utilization rates
- **Relationships Used**: Branch → Jobs
- **New Analysis**: Capacity planning metrics

## Customer Cohort Analysis Queries

### customer_behavior/customer_acquisition_cohorts.sql
- **Purpose**: Cohort analysis by customer acquisition date (first_lead_date)
- **Key Outputs**: Active customers, jobs, revenue by cohort and period
- **Relationships Used**: Customer.firstLeadDate → Jobs
- **New Field Used**: Customer.firstLeadDate

### customer_behavior/retention_cohort_analysis.sql
- **Purpose**: Customer retention rates by acquisition cohort
- **Key Outputs**: Retention rates by quarter and cohort
- **Relationships Used**: Customer.firstLeadDate → Jobs
- **New Field Used**: Customer.firstLeadDate

### customer_behavior/cohort_revenue_analysis.sql
- **Purpose**: Revenue patterns by customer acquisition cohort
- **Key Outputs**: Revenue by cohort and months since acquisition
- **Relationships Used**: Customer.firstLeadDate → Jobs
- **New Field Used**: Customer.firstLeadDate

## Query Optimization Notes

### Optimized Queries

1. **customer_lifetime_value.sql**
   - Changed LEFT JOIN to INNER JOIN (only customers with jobs needed)
   - Added early WHERE filter for opportunity_status
   - Reduced dataset size before aggregation

2. **lead_conversion_funnel.sql**
   - Optimized UNION ALL structure
   - Combined status checks using IN clause

3. **customer_relationship_summary.sql**
   - Changed LEFT JOIN to INNER JOIN for jobs
   - Added HAVING clauses to reduce aggregation overhead
   - Only aggregate where relationships exist

4. **operational/bottleneck_identification.sql**
   - Optimized date calculations (using extract(epoch) instead of interval arithmetic)
   - Added early filters for null checks
   - Converted interval comparisons to numeric comparisons

### Performance Improvements

- **Index Usage**: All new queries leverage existing and new composite indexes
- **Filter Early**: All optimized queries filter by `is_duplicate = false` and `opportunity_status` early
- **JOIN Optimization**: Changed unnecessary LEFT JOINs to INNER JOINs where NULLs not needed
- **Aggregation Optimization**: Added HAVING clauses to reduce aggregation overhead

## Query Usage Guidelines

### When to Use Which Query

1. **Customer Analysis**: Use customer relationship queries when analyzing customer behavior and lifetime value
2. **Lead Analysis**: Use lead queries when tracking lead conversion and journey
3. **Sales Performance**: Use sales person queries when analyzing sales team performance
4. **Revenue Analysis**: Use revenue queries for financial reporting
5. **Geographic Analysis**: Use geographic queries for location-based insights
6. **Time-Based Analysis**: Use time-based queries for trend analysis

### Performance Considerations

- Most queries use CTEs for better readability and performance
- All foreign key relationships are indexed
- Filter jobs by `opportunity_status` early (only BOOKED/CLOSED for customers)
- Use `quote_number` for efficient linking between LeadStatus, LostLead, and BookedOpportunity

### Common Patterns

1. **Customer Complete View**: Use `customer_complete_profile.sql` for 360-degree customer view
2. **Lead Journey**: Use `lead_to_customer_traceability.sql` for complete lead journey
3. **Cross-Module Analysis**: Use `module_relationship_matrix.sql` for relationship overview
4. **Sales Performance**: Use `sales_person_cross_module.sql` for comprehensive sales analysis

