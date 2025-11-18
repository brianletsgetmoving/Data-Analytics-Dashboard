"""Job analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause, get_aggregation_period_sql
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/metrics", response_model=AnalyticsResponse)
async def get_job_metrics(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job metrics summary."""
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            COUNT(*) as total_jobs,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'QUOTED') as quoted_jobs,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'BOOKED') as booked_jobs,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'CLOSED') as closed_jobs,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'LOST') as lost_jobs,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'CANCELLED') as cancelled_jobs,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
            AVG(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as avg_job_value
        FROM jobs j
        WHERE {where_clause}
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results[0] if results else {},
        metadata={},
        filters_applied=filters,
    )


@router.get("/volume-trends", response_model=AnalyticsResponse)
async def get_volume_trends(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job volume trends."""
    where_clause, params = build_where_clause(filters, table_alias="j")
    period_sql = get_aggregation_period_sql(filters.aggregation_period or "monthly")
    # Update period_sql to use table alias
    period_sql = period_sql.replace("job_date", "j.job_date")
    
    query = f"""
        SELECT 
            {period_sql} as period,
            COUNT(*) as job_count,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'BOOKED') as booked_count,
            COUNT(*) FILTER (WHERE j.opportunity_status = 'CLOSED') as closed_count,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue
        FROM jobs j
        WHERE {where_clause}
        AND j.job_date IS NOT NULL
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


@router.get("/status-distribution", response_model=AnalyticsResponse)
async def get_status_distribution(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job status distribution."""
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            j.opportunity_status as status,
            COUNT(*) as count,
            ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) as percentage
        FROM jobs j
        WHERE {where_clause}
        GROUP BY j.opportunity_status
        ORDER BY count DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/type-distribution", response_model=AnalyticsResponse)
async def get_type_distribution(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job type distribution."""
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            j.job_type,
            COUNT(*) as count,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue
        FROM jobs j
        WHERE {where_clause}
        AND j.job_type IS NOT NULL
        GROUP BY j.job_type
        ORDER BY count DESC
        LIMIT 20
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/seasonal-patterns", response_model=AnalyticsResponse)
async def get_seasonal_patterns(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get seasonal job patterns."""
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            EXTRACT(MONTH FROM j.job_date) as month,
            EXTRACT(QUARTER FROM j.job_date) as quarter,
            COUNT(*) as job_count,
            SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as revenue
        FROM jobs j
        WHERE {where_clause}
        AND j.job_date IS NOT NULL
        GROUP BY EXTRACT(MONTH FROM j.job_date), EXTRACT(QUARTER FROM j.job_date)
        ORDER BY month
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/crew-utilization", response_model=AnalyticsResponse)
async def get_crew_utilization(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get crew and truck utilization metrics."""
    where_clause, params = build_where_clause(filters, table_alias="j")
    
    query = f"""
        SELECT 
            AVG(j.actual_number_crew) as avg_crew,
            AVG(j.actual_number_trucks) as avg_trucks,
            SUM(j.actual_number_crew) as total_crew_hours,
            SUM(j.actual_number_trucks) as total_truck_hours,
            COUNT(*) FILTER (WHERE j.actual_number_crew IS NOT NULL) as jobs_with_crew_data,
            COUNT(*) FILTER (WHERE j.actual_number_trucks IS NOT NULL) as jobs_with_truck_data
        FROM jobs j
        WHERE {where_clause}
        AND j.opportunity_status IN ('BOOKED', 'CLOSED')
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results[0] if results else {},
        metadata={},
        filters_applied=filters,
    )

