"""Benchmarking analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import apply_filters_to_query
from ...utils.sql_loader import load_sql_query
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/industry", response_model=AnalyticsResponse)
async def get_industry_benchmarks(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get industry benchmarks."""
    query = load_sql_query("industry_benchmarks", "benchmarking")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/branch", response_model=AnalyticsResponse)
async def get_branch_benchmarking(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get branch performance benchmarking."""
    query = load_sql_query("branch_performance_benchmarking", "benchmarking")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/sales-person", response_model=AnalyticsResponse)
async def get_sales_person_benchmarking(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get sales person performance benchmarking."""
    query = load_sql_query("sales_person_benchmarking", "benchmarking")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/time-period", response_model=AnalyticsResponse)
async def get_time_period_benchmarks(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get time period comparisons."""
    query = load_sql_query("time_period_benchmarks", "benchmarking")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/market-share", response_model=AnalyticsResponse)
async def get_market_share(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get market share analysis."""
    query = load_sql_query("market_share_analysis", "benchmarking")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/competitive-metrics", response_model=AnalyticsResponse)
async def get_competitive_metrics(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get competitive metrics."""
    query = load_sql_query("competitive_metrics", "benchmarking")
    query, params = apply_filters_to_query(query, filters)
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

