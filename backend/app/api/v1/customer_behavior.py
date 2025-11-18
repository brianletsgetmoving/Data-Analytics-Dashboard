"""Customer behavior analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import apply_filters_to_query
from ...utils.sql_loader import load_sql_query
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/churn-prediction", response_model=AnalyticsResponse)
async def get_churn_prediction(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get at-risk customers (churn prediction)."""
    query = load_sql_query("customer_churn_prediction", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/ltv-forecast", response_model=AnalyticsResponse)
async def get_ltv_forecast(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get predictive LTV forecast."""
    query = load_sql_query("customer_lifetime_value_forecast", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/journey", response_model=AnalyticsResponse)
async def get_customer_journey(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer journey analysis."""
    query = load_sql_query("customer_journey_analysis", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/rfm-segmentation", response_model=AnalyticsResponse)
async def get_rfm_segmentation(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get RFM (Recency, Frequency, Monetary) segmentation."""
    query = load_sql_query("customer_segmentation_advanced", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/preferences", response_model=AnalyticsResponse)
async def get_customer_preferences(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer preferences analysis."""
    query = load_sql_query("customer_preferences_analysis", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/acquisition-cost", response_model=AnalyticsResponse)
async def get_acquisition_cost(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get customer acquisition cost (CAC) analysis."""
    query = load_sql_query("customer_acquisition_cost", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/repeat-patterns", response_model=AnalyticsResponse)
async def get_repeat_patterns(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get repeat customer patterns."""
    query = load_sql_query("repeat_customer_patterns", "customer_behavior")
    # Query uses jobs j table alias, so filters should be applied with j prefix
    query, params = apply_filters_to_query(query, filters, table_alias="j")
    results = db.execute_query(query, params if params else None)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

