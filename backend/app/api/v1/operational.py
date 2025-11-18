"""Operational analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...utils.sql_loader import load_sql_query
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/capacity-utilization", response_model=AnalyticsResponse)
async def get_capacity_utilization(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get capacity utilization analysis."""
    query = load_sql_query("capacity_utilization", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/routing-efficiency", response_model=AnalyticsResponse)
async def get_routing_efficiency(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get routing efficiency analysis."""
    query = load_sql_query("routing_efficiency", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/job-duration", response_model=AnalyticsResponse)
async def get_job_duration(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job duration analysis."""
    query = load_sql_query("job_duration_analysis", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/bottlenecks", response_model=AnalyticsResponse)
async def get_bottlenecks(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get bottleneck identification."""
    query = load_sql_query("bottleneck_identification", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/resource-allocation", response_model=AnalyticsResponse)
async def get_resource_allocation(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get resource allocation analysis."""
    query = load_sql_query("resource_allocation", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/capacity-planning", response_model=AnalyticsResponse)
async def get_capacity_planning(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get seasonal capacity planning."""
    query = load_sql_query("seasonal_capacity_planning", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/scheduling-efficiency", response_model=AnalyticsResponse)
async def get_scheduling_efficiency(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get scheduling efficiency analysis."""
    query = load_sql_query("job_scheduling_efficiency", "operational")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

