"""Customer analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...api.dependencies import get_filters

router = APIRouter()

# TODO: [Agent 2] Add GET /api/v1/customers endpoint
# Returns: List of all customers with name, email, phone, branch_id
# Supports filtering by branch_id query parameter
# Response format: AnalyticsResponse with customer data array

# TODO: [Agent 2] Add GET /api/v1/customers/{id} endpoint
# Returns: Single customer details by ID
# Response format: AnalyticsResponse with single customer object

# TODO: [Agent 2] Add GET /api/v1/customers/{id}/jobs endpoint
# Returns: List of jobs for a specific customer
# Response format: AnalyticsResponse with job data array

# TODO: [Agent 2] Add POST /api/v1/customers endpoint
# Request body: { name: string, email?: string, phone?: string, branch_id?: string, ... }
# Response format: AnalyticsResponse with created customer object


@router.get("/demographics", response_model=AnalyticsResponse)
async def get_customer_demographics(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer demographics data."""
    # Build where clause with job table alias since filters apply to jobs
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            c.origin_city,
            c.origin_state,
            c.destination_city,
            c.destination_state,
            COUNT(DISTINCT c.id) as customer_count,
            COUNT(DISTINCT j.id) as total_jobs
        FROM customers c
        LEFT JOIN jobs j ON c.id = j.customer_id
        WHERE {where_clause}
        GROUP BY c.origin_city, c.origin_state, c.destination_city, c.destination_state
        ORDER BY customer_count DESC
        LIMIT 100
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/segmentation", response_model=AnalyticsResponse)
async def get_customer_segmentation(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer segmentation by value."""
    # Build where clause with job table alias since filters apply to jobs
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        WITH customer_revenue AS (
            SELECT 
                c.id as customer_id,
                SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue
            FROM customers c
            LEFT JOIN jobs j ON c.id = j.customer_id
            WHERE {where_clause}
            AND j.opportunity_status IN ('BOOKED', 'CLOSED')
            GROUP BY c.id
        )
        SELECT 
            CASE 
                WHEN total_revenue < 500 THEN '<$500'
                WHEN total_revenue < 1000 THEN '$500-$1000'
                WHEN total_revenue < 1500 THEN '$1000-$1500'
                WHEN total_revenue < 2000 THEN '$1500-$2000'
                WHEN total_revenue < 2500 THEN '$2000-$2500'
                ELSE '>$2500'
            END as segment,
            COUNT(*) as customer_count,
            SUM(total_revenue) as segment_revenue,
            AVG(total_revenue) as avg_revenue
        FROM customer_revenue
        WHERE total_revenue > 0
        GROUP BY segment
        ORDER BY 
            CASE segment
                WHEN '<$500' THEN 1
                WHEN '$500-$1000' THEN 2
                WHEN '$1000-$1500' THEN 3
                WHEN '$1500-$2000' THEN 4
                WHEN '$2000-$2500' THEN 5
                ELSE 6
            END
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/gender-breakdown", response_model=AnalyticsResponse)
async def get_gender_breakdown(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer gender breakdown."""
    # Build where clause with job table alias since filters apply to jobs
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            COALESCE(c.gender::text, 'UNKNOWN') as gender,
            COUNT(DISTINCT c.id) as customer_count,
            COUNT(DISTINCT j.id) as job_count,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue
        FROM customers c
        LEFT JOIN jobs j ON c.id = j.customer_id
        WHERE {where_clause}
        GROUP BY c.gender
        ORDER BY customer_count DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/lifetime-value", response_model=AnalyticsResponse)
async def get_customer_lifetime_value(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer lifetime value analysis."""
    # Build where clause with job table alias since filters apply to jobs
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            c.id as customer_id,
            c.name as customer_name,
            COUNT(DISTINCT j.id) as total_jobs,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as lifetime_value,
            MIN(j.job_date) as first_job_date,
            MAX(j.job_date) as last_job_date
        FROM customers c
        LEFT JOIN jobs j ON c.id = j.customer_id
        WHERE {where_clause}
        AND j.opportunity_status IN ('BOOKED', 'CLOSED')
        GROUP BY c.id, c.name
        HAVING COUNT(DISTINCT j.id) > 0
        ORDER BY lifetime_value DESC
        LIMIT 100
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/retention", response_model=AnalyticsResponse)
async def get_customer_retention(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer retention metrics."""
    # Build where clause with job table alias since filters apply to jobs
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        WITH customer_jobs AS (
            SELECT 
                c.id as customer_id,
                COUNT(DISTINCT j.id) as job_count,
                COUNT(DISTINCT DATE_TRUNC('year', j.job_date)) as active_years
            FROM customers c
            LEFT JOIN jobs j ON c.id = j.customer_id
            WHERE {where_clause}
            AND j.opportunity_status IN ('BOOKED', 'CLOSED')
            GROUP BY c.id
        )
        SELECT 
            CASE 
                WHEN job_count = 1 THEN 'Single Job'
                WHEN job_count BETWEEN 2 AND 3 THEN 'Repeat (2-3)'
                WHEN job_count BETWEEN 4 AND 5 THEN 'Repeat (4-5)'
                ELSE 'Loyal (6+)'
            END as retention_segment,
            COUNT(*) as customer_count,
            AVG(job_count) as avg_jobs,
            AVG(active_years) as avg_active_years
        FROM customer_jobs
        GROUP BY retention_segment
        ORDER BY 
            CASE retention_segment
                WHEN 'Single Job' THEN 1
                WHEN 'Repeat (2-3)' THEN 2
                WHEN 'Repeat (4-5)' THEN 3
                ELSE 4
            END
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/geographic-distribution", response_model=AnalyticsResponse)
async def get_geographic_distribution(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer geographic distribution."""
    # Build where clause with job table alias since filters apply to jobs
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            c.origin_city,
            c.origin_state,
            COUNT(DISTINCT c.id) as origin_customer_count,
            c.destination_city,
            c.destination_state,
            COUNT(DISTINCT c.id) as destination_customer_count
        FROM customers c
        LEFT JOIN jobs j ON c.id = j.customer_id
        WHERE {where_clause}
        GROUP BY c.origin_city, c.origin_state, c.destination_city, c.destination_state
        ORDER BY origin_customer_count DESC, destination_customer_count DESC
        LIMIT 100
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

