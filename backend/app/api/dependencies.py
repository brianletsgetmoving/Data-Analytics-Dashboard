"""API dependencies."""
from fastapi import Query
from typing import Optional

from ..schemas.filters import UniversalFilter


def get_filters(
    branch_id: Optional[str] = Query(None),
    branch_name: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    sales_person_id: Optional[str] = Query(None),
    sales_person_name: Optional[str] = Query(None),
    customer_segment: Optional[str] = Query(None),
    job_status: Optional[str] = Query(None),
    aggregation_period: Optional[str] = Query("monthly"),
    limit: Optional[int] = Query(100, ge=1, le=1000),
    offset: Optional[int] = Query(0, ge=0),
) -> UniversalFilter:
    """Create UniversalFilter from query parameters."""
    return UniversalFilter(
        branch_id=branch_id,
        branch_name=branch_name,
        date_from=date_from,
        date_to=date_to,
        sales_person_id=sales_person_id,
        sales_person_name=sales_person_name,
        customer_segment=customer_segment,
        job_status=job_status,
        aggregation_period=aggregation_period,
        limit=limit,
        offset=offset,
    )

