"""Forecasting analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...utils.sql_loader import load_sql_query
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/revenue", response_model=AnalyticsResponse)
async def get_revenue_forecast(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get advanced revenue forecasting."""
    query = load_sql_query("revenue_forecast_advanced", "forecasting")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/job-volume", response_model=AnalyticsResponse)
async def get_job_volume_forecast(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get job volume forecasting."""
    query = load_sql_query("job_volume_forecast", "forecasting")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/customer-growth", response_model=AnalyticsResponse)
async def get_customer_growth_forecast(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer growth forecasting."""
    query = load_sql_query("customer_growth_forecast", "forecasting")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/demand", response_model=AnalyticsResponse)
async def get_demand_forecast(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get demand forecasting."""
    query = load_sql_query("demand_forecasting", "forecasting")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/trends", response_model=AnalyticsResponse)
async def get_trend_analysis(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get trend analysis."""
    query = load_sql_query("trend_analysis", "forecasting")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/anomalies", response_model=AnalyticsResponse)
async def get_anomalies(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get anomaly detection."""
    query = load_sql_query("anomaly_detection", "forecasting")
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

