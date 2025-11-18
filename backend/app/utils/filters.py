"""Filter utility functions for building SQL queries."""
from typing import Optional, List
from datetime import datetime

from ..schemas.filters import UniversalFilter


def build_where_clause(filters: UniversalFilter) -> tuple[str, list]:
    """
    Build SQL WHERE clause from universal filters.
    
    Returns:
        Tuple of (WHERE clause string, parameter list)
    """
    conditions = []
    params = []
    
    if filters.branch_name:
        conditions.append("branch_name = %s")
        params.append(filters.branch_name)
    
    if filters.branch_id:
        conditions.append("branch_id = %s")
        params.append(filters.branch_id)
    
    if filters.date_from:
        conditions.append("job_date >= %s")
        params.append(filters.date_from)
    
    if filters.date_to:
        conditions.append("job_date <= %s")
        params.append(filters.date_to)
    
    if filters.sales_person_id:
        conditions.append("sales_person_id = %s")
        params.append(filters.sales_person_id)
    
    if filters.sales_person_name:
        conditions.append("sales_person_name = %s")
        params.append(filters.sales_person_name)
    
    if filters.job_status:
        placeholders = ",".join(["%s"] * len(filters.job_status))
        conditions.append(f"opportunity_status IN ({placeholders})")
        params.extend(filters.job_status)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, params


def get_aggregation_period_sql(period: str) -> str:
    """Get SQL date truncation for aggregation period."""
    period_map = {
        "daily": "DATE_TRUNC('day', job_date)",
        "weekly": "DATE_TRUNC('week', job_date)",
        "monthly": "DATE_TRUNC('month', job_date)",
        "quarterly": "DATE_TRUNC('quarter', job_date)",
        "yearly": "DATE_TRUNC('year', job_date)",
    }
    return period_map.get(period.lower(), "DATE_TRUNC('month', job_date)")

