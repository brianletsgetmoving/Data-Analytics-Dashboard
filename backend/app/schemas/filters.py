"""Universal filtering schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class UniversalFilter(BaseModel):
    """Universal filter for all analytics endpoints."""
    
    branch_id: Optional[str] = Field(default=None, description="Branch ID filter")
    branch_name: Optional[str] = Field(default=None, description="Branch name filter")
    date_from: Optional[str] = Field(default=None, description="Start date (ISO format)")
    date_to: Optional[str] = Field(default=None, description="End date (ISO format)")
    sales_person_id: Optional[str] = Field(default=None, description="Sales person ID filter")
    sales_person_name: Optional[str] = Field(default=None, description="Sales person name filter")
    customer_segment: Optional[str] = Field(default=None, description="Customer segment filter")
    job_status: Optional[str] = Field(default=None, description="Comma-separated job statuses")
    aggregation_period: Optional[str] = Field(
        default="monthly",
        description="daily, weekly, monthly, quarterly, yearly"
    )
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
    
    @field_validator('date_from', 'date_to', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date string to datetime."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except:
                return None
        return v
    
    @field_validator('job_status', mode='before')
    @classmethod
    def parse_job_status(cls, v):
        """Parse comma-separated job statuses."""
        if v is None:
            return None
        if isinstance(v, str):
            return [s.strip() for s in v.split(',') if s.strip()]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "branch_name": "NORTH YORK TORONTO",
                "date_from": "2024-01-01T00:00:00",
                "date_to": "2024-12-31T23:59:59",
                "aggregation_period": "monthly"
            }
        }

