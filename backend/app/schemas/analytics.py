"""Analytics response schemas."""
from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from .filters import UniversalFilter


class AnalyticsResponse(BaseModel):
    """Standard analytics API response."""
    
    data: Any
    metadata: Dict[str, Any] = {}
    filters_applied: UniversalFilter
    timestamp: datetime = Field(default_factory=datetime.now)
    cache_ttl: int = 300
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "metadata": {"total": 0, "page": 1, "page_size": 100},
                "filters_applied": {},
                "timestamp": "2024-01-01T00:00:00",
                "cache_ttl": 300
            }
        }


class KPIMetric(BaseModel):
    """KPI metric card data."""
    
    label: str
    value: float
    unit: Optional[str] = None
    change: Optional[float] = None
    change_type: Optional[str] = None  # "increase", "decrease", "neutral"
    trend: Optional[List[float]] = None


class ChartDataPoint(BaseModel):
    """Single chart data point."""
    
    label: str
    value: float
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChartSeries(BaseModel):
    """Chart series data."""
    
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

