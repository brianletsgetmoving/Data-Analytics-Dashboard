"""Sales performance endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/performance", response_model=AnalyticsResponse)
async def get_sales_performance(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get sales person performance metrics."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            sp.name as sales_person_name,
            spf.leads_received,
            spf.bad,
            spf.percent_bad,
            spf.sent,
            spf.percent_sent,
            spf.pending,
            spf.percent_pending,
            spf.booked,
            spf.percent_booked,
            spf.lost,
            spf.percent_lost,
            spf.cancelled,
            spf.percent_cancelled,
            spf.booked_total,
            spf.average_booking
        FROM sales_performance spf
        LEFT JOIN sales_persons sp ON spf.sales_person_id = sp.id
        WHERE {where_clause.replace('job_date', 'spf.created_at').replace('branch_name', 'spf.name')}
        ORDER BY spf.booked_total DESC NULLS LAST
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/rankings", response_model=AnalyticsResponse)
async def get_sales_rankings(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get sales person rankings."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            sp.name as sales_person_name,
            spf.booked_total,
            spf.booked as booked_count,
            spf.percent_booked,
            spf.average_booking,
            ROW_NUMBER() OVER (ORDER BY spf.booked_total DESC NULLS LAST) as rank
        FROM sales_performance spf
        LEFT JOIN sales_persons sp ON spf.sales_person_id = sp.id
        WHERE {where_clause.replace('job_date', 'spf.created_at').replace('branch_name', 'spf.name')}
        ORDER BY spf.booked_total DESC NULLS LAST
        LIMIT 50
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/trends", response_model=AnalyticsResponse)
async def get_sales_trends(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get sales performance trends over time."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            DATE_TRUNC('month', j.job_date) as month,
            sp.name as sales_person_name,
            COUNT(*) as job_count,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue
        FROM jobs j
        LEFT JOIN sales_persons sp ON j.sales_person_id = sp.id
        WHERE {where_clause}
        AND j.opportunity_status IN ('BOOKED', 'CLOSED')
        AND j.job_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', j.job_date), sp.name
        ORDER BY month DESC, revenue DESC
        LIMIT 100
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/comparison", response_model=AnalyticsResponse)
async def get_sales_comparison(
    filters: UniversalFilter = Depends(get_filters),
):
    """Compare sales person performance."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            sp.name as sales_person_name,
            COUNT(DISTINCT j.id) as total_jobs,
            COUNT(DISTINCT j.id) FILTER (WHERE j.opportunity_status = 'BOOKED') as booked_jobs,
            COUNT(DISTINCT j.id) FILTER (WHERE j.opportunity_status = 'CLOSED') as closed_jobs,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
            AVG(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
        FROM jobs j
        LEFT JOIN sales_persons sp ON j.sales_person_id = sp.id
        WHERE {where_clause}
        AND sp.id IS NOT NULL
        GROUP BY sp.name
        ORDER BY total_revenue DESC
        LIMIT 30
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/efficiency", response_model=AnalyticsResponse)
async def get_sales_efficiency(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get sales efficiency metrics."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            sp.name as sales_person_name,
            spf.leads_received,
            spf.booked,
            ROUND(spf.booked::numeric / NULLIF(spf.leads_received, 0) * 100, 2) as conversion_rate,
            spf.booked_total,
            ROUND(spf.booked_total / NULLIF(spf.booked, 0), 2) as avg_booking_value,
            up.total_calls,
            ROUND(up.total_calls::numeric / NULLIF(spf.booked, 0), 2) as calls_per_booking
        FROM sales_performance spf
        LEFT JOIN sales_persons sp ON spf.sales_person_id = sp.id
        LEFT JOIN user_performance up ON sp.id = up.sales_person_id
        WHERE {where_clause.replace('job_date', 'spf.created_at').replace('branch_name', 'spf.name')}
        ORDER BY conversion_rate DESC NULLS LAST
        LIMIT 30
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

