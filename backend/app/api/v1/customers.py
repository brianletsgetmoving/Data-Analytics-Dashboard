"""Customer analytics endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Optional
from pydantic import BaseModel, EmailStr

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...api.dependencies import get_filters

router = APIRouter()


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    origin_city: Optional[str] = None
    origin_state: Optional[str] = None
    origin_zip: Optional[str] = None
    origin_address: Optional[str] = None
    destination_city: Optional[str] = None
    destination_state: Optional[str] = None
    destination_zip: Optional[str] = None
    destination_address: Optional[str] = None


@router.get("", response_model=AnalyticsResponse)
async def get_customers(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get list of customers with optional filtering."""
    # Build where clause - filters can apply to customers directly or via jobs
    where_clause, params = build_where_clause(filters, table_alias="c")
    
    # If filters include job-related filters, we need to join with jobs
    has_job_filters = any([
        filters.job_status,
        filters.date_from,
        filters.date_to,
    ])
    
    if has_job_filters:
        # Join with jobs table when job filters are present
        where_clause_job, params_job = build_where_clause(filters, table_alias="j")
        query = f"""
            SELECT DISTINCT
                c.id,
                c.name,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.origin_city,
                c.origin_state,
                c.destination_city,
                c.destination_state,
                c.gender,
                c.created_at,
                c.updated_at
            FROM customers c
            LEFT JOIN jobs j ON c.id = j.customer_id
            WHERE {where_clause_job}
            ORDER BY c.name
            LIMIT %s OFFSET %s
        """
        limit = filters.limit or 100
        offset = filters.offset or 0
        all_params = list(params_job) + [limit, offset]
    else:
        # Simple customer query without job join
        query = f"""
            SELECT 
                c.id,
                c.name,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.origin_city,
                c.origin_state,
                c.destination_city,
                c.destination_state,
                c.gender,
                c.created_at,
                c.updated_at
            FROM customers c
            WHERE {where_clause}
            ORDER BY c.name
            LIMIT %s OFFSET %s
        """
        limit = filters.limit or 100
        offset = filters.offset or 0
        all_params = list(params) + [limit, offset]
    
    results = db.execute_query(query, tuple(all_params))
    
    # Get total count for metadata
    if has_job_filters:
        count_query = f"""
            SELECT COUNT(DISTINCT c.id)
            FROM customers c
            LEFT JOIN jobs j ON c.id = j.customer_id
            WHERE {where_clause_job}
        """
        count_params = params_job
    else:
        count_query = f"""
            SELECT COUNT(*)
            FROM customers c
            WHERE {where_clause}
        """
        count_params = params
    
    count_result = db.execute_query(count_query, tuple(count_params))
    total_count = count_result[0]['count'] if count_result else len(results)
    
    return AnalyticsResponse(
        data=results,
        metadata={
            "count": len(results),
            "total": total_count,
            "limit": limit,
            "offset": offset,
        },
        filters_applied=filters,
    )


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


@router.get("/gender", response_model=AnalyticsResponse)
async def get_gender(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer gender breakdown (alias for /gender-breakdown)."""
    # Reuse the same logic as gender-breakdown
    return await get_gender_breakdown(filters)


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


@router.get("/{customer_id}/jobs", response_model=AnalyticsResponse)
async def get_customer_jobs(
    customer_id: str = Path(..., description="Customer ID"),
    filters: UniversalFilter = Depends(get_filters),
):
    """Get jobs for a specific customer."""
    # First verify customer exists
    customer_check = db.execute_query(
        "SELECT id, name FROM customers WHERE id = %s",
        (customer_id,)
    )
    
    if not customer_check:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Build where clause for jobs, but always include customer_id filter
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    # Add customer_id to where clause
    if where_clause:
        where_clause = f"j.customer_id = %s AND {where_clause}"
        all_params = [customer_id] + list(params)
    else:
        where_clause = "j.customer_id = %s"
        all_params = [customer_id]
    
    query = f"""
        SELECT 
            j.id,
            j.job_id,
            j.job_number,
            j.opportunity_status,
            j.job_date,
            j.job_type,
            j.sales_person_name,
            j.branch_name,
            j.total_estimated_cost,
            j.total_actual_cost,
            j.created_at_utc,
            j.booked_at_utc
        FROM jobs j
        WHERE {where_clause}
        ORDER BY j.job_date DESC NULLS LAST, j.created_at_utc DESC NULLS LAST
        LIMIT %s OFFSET %s
    """
    
    limit = filters.limit or 100
    offset = filters.offset or 0
    all_params = all_params + [limit, offset]
    
    results = db.execute_query(query, tuple(all_params))
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*)
        FROM jobs j
        WHERE {where_clause.replace('LIMIT %s OFFSET %s', '')}
    """
    count_result = db.execute_query(count_query, tuple(all_params[:-2]))
    total_count = count_result[0]['count'] if count_result else len(results)
    
    return AnalyticsResponse(
        data=results,
        metadata={
            "count": len(results),
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "customer_id": customer_id,
            "customer_name": customer_check[0]['name'],
        },
        filters_applied=filters,
    )


@router.post("", response_model=AnalyticsResponse)
async def create_customer(
    customer: CustomerCreate,
):
    """Create a new customer."""
    # Check for duplicate email if provided
    if customer.email:
        existing = db.execute_query(
            "SELECT id FROM customers WHERE email = %s",
            (customer.email,)
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Customer with email {customer.email} already exists"
            )
    
    # Check for duplicate phone if provided
    if customer.phone:
        existing = db.execute_query(
            "SELECT id FROM customers WHERE phone = %s",
            (customer.phone,)
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Customer with phone {customer.phone} already exists"
            )
    
    # Insert new customer
    insert_query = """
        INSERT INTO customers (
            name, first_name, last_name, email, phone,
            origin_city, origin_state, origin_zip, origin_address,
            destination_city, destination_state, destination_zip, destination_address
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, name, first_name, last_name, email, phone,
                  origin_city, origin_state, destination_city, destination_state,
                  created_at, updated_at
    """
    
    params = (
        customer.name,
        customer.first_name,
        customer.last_name,
        customer.email,
        customer.phone,
        customer.origin_city,
        customer.origin_state,
        customer.origin_zip,
        customer.origin_address,
        customer.destination_city,
        customer.destination_state,
        customer.destination_zip,
        customer.destination_address,
    )
    
    try:
        result = db.execute_query(insert_query, params)
        if result:
            created_customer = result[0]
            return AnalyticsResponse(
                data=created_customer,
                metadata={"created": True},
                filters_applied=UniversalFilter(),
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create customer")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating customer: {str(e)}"
        )

