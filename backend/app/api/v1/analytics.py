"""Analytics overview endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/overview", response_model=AnalyticsResponse)
async def get_overview(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get overview analytics."""
    # Build base query
    where_clause, params = build_where_clause(filters)
    
    # Get KPIs
    kpis_query = f"""
        SELECT 
            COUNT(DISTINCT j.id) as total_jobs,
            COUNT(DISTINCT c.id) as total_customers,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
            AVG(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
        FROM jobs j
        LEFT JOIN customers c ON j.customer_id = c.id
        WHERE {where_clause}
        AND j.opportunity_status IN ('BOOKED', 'CLOSED')
    """
    
    kpi_results = db.execute_query(kpis_query, tuple(params))
    kpi_data = kpi_results[0] if kpi_results else {}
    
    kpis = [
        {
            "label": "Total Revenue",
            "value": float(kpi_data.get("total_revenue", 0)),
            "unit": "USD",
        },
        {
            "label": "Active Customers",
            "value": float(kpi_data.get("total_customers", 0)),
        },
        {
            "label": "Total Jobs",
            "value": float(kpi_data.get("total_jobs", 0)),
        },
        {
            "label": "Avg Job Value",
            "value": float(kpi_data.get("avg_job_value", 0)),
            "unit": "USD",
        },
    ]
    
    return AnalyticsResponse(
        data={"kpis": kpis},
        metadata={"total": len(kpis)},
        filters_applied=filters,
    )


@router.get("/kpis", response_model=AnalyticsResponse)
async def get_kpis(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get detailed KPI metrics."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            COUNT(DISTINCT j.id) as total_jobs,
            COUNT(DISTINCT c.id) as total_customers,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
            AVG(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value,
            COUNT(DISTINCT CASE WHEN j.opportunity_status = 'BOOKED' THEN j.id END) as booked_jobs,
            COUNT(DISTINCT CASE WHEN j.opportunity_status = 'CLOSED' THEN j.id END) as closed_jobs
        FROM jobs j
        LEFT JOIN customers c ON j.customer_id = c.id
        WHERE {where_clause}
    """
    
    results = db.execute_query(query, tuple(params))
    data = results[0] if results else {}
    
    return AnalyticsResponse(
        data=data,
        metadata={},
        filters_applied=filters,
    )


@router.get("/trends", response_model=AnalyticsResponse)
async def get_trends(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get trend data."""
    from ...utils.filters import get_aggregation_period_sql
    
    where_clause, params = build_where_clause(filters)
    period_sql = get_aggregation_period_sql(filters.aggregation_period or "monthly")
    
    query = f"""
        SELECT 
            {period_sql} as period,
            COUNT(DISTINCT j.id) as job_count,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue
        FROM jobs j
        WHERE {where_clause}
        AND j.opportunity_status IN ('BOOKED', 'CLOSED')
        GROUP BY {period_sql}
        ORDER BY period DESC
        LIMIT 24
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"period": filters.aggregation_period, "count": len(results)},
        filters_applied=filters,
    )

