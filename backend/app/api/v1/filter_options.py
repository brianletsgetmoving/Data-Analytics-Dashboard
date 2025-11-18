"""Filter options endpoints for dropdowns and selectors."""
from fastapi import APIRouter

from ...schemas.analytics import AnalyticsResponse
from ...database import db

router = APIRouter()


@router.get("/branches", response_model=AnalyticsResponse)
async def get_branches():
    """Get list of all branches for filter dropdowns."""
    query = """
        SELECT 
            id,
            name
        FROM branches
        WHERE is_active = true
        ORDER BY name ASC
    """
    
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied={},
    )


@router.get("/sales-persons", response_model=AnalyticsResponse)
async def get_sales_persons():
    """Get list of all sales persons for filter dropdowns."""
    query = """
        SELECT 
            id,
            name
        FROM sales_persons
        ORDER BY name ASC
    """
    
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied={},
    )

