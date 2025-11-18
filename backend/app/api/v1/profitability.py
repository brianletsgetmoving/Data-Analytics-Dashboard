"""Profitability analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import apply_filters_to_query
from ...utils.sql_loader import load_sql_query
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/job-margins", response_model=AnalyticsResponse)
async def get_job_margins(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job margin analysis."""
    query = load_sql_query("job_margins", "profitability")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/branch", response_model=AnalyticsResponse)
async def get_branch_profitability(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get branch profitability analysis."""
    query = load_sql_query("branch_profitability", "profitability")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/job-type", response_model=AnalyticsResponse)
async def get_job_type_profitability(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job type profitability analysis."""
    query = load_sql_query("job_type_profitability", "profitability")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/customer", response_model=AnalyticsResponse)
async def get_customer_profitability(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer profitability ranking."""
    query = load_sql_query("customer_profitability", "profitability")
    # Note: customer_profitability query joins customers and jobs tables, 
    # but filters are applied to jobs table (j alias) which is correct
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/roi-by-source", response_model=AnalyticsResponse)
async def get_roi_by_source(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get ROI analysis by referral source."""
    query = load_sql_query("roi_by_referral_source", "profitability")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/cost-efficiency", response_model=AnalyticsResponse)
async def get_cost_efficiency(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get cost efficiency metrics."""
    query = load_sql_query("cost_efficiency_metrics", "profitability")
    
    # Cost efficiency query doesn't have WHERE clause, so we'll execute as-is
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/pricing-optimization", response_model=AnalyticsResponse)
async def get_pricing_optimization(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get pricing optimization analysis."""
    query = load_sql_query("pricing_optimization", "profitability")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

