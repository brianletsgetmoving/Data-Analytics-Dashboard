"""Filter utility functions for building SQL queries."""
from typing import Optional, List, Tuple
from datetime import datetime

from ..schemas.filters import UniversalFilter


def build_where_clause(filters: UniversalFilter, table_alias: Optional[str] = None) -> tuple[str, list]:
    """
    Build SQL WHERE clause from universal filters.
    
    Args:
        filters: UniversalFilter object
        table_alias: Optional table alias (e.g., 'j' for 'jobs j') to prefix column names
    
    Returns:
        Tuple of (WHERE clause string, parameter list)
    """
    conditions = []
    params = []
    
    # Prefix for column names if table alias is provided
    prefix = f"{table_alias}." if table_alias else ""
    
    if filters.branch_name:
        conditions.append(f"{prefix}branch_name = %s")
        params.append(filters.branch_name)
    
    if filters.branch_id:
        conditions.append(f"{prefix}branch_id = %s")
        params.append(filters.branch_id)
    
    if filters.date_from:
        conditions.append(f"{prefix}job_date >= %s")
        params.append(filters.date_from)
    
    if filters.date_to:
        conditions.append(f"{prefix}job_date <= %s")
        params.append(filters.date_to)
    
    if filters.sales_person_id:
        conditions.append(f"{prefix}sales_person_id = %s")
        params.append(filters.sales_person_id)
    
    if filters.sales_person_name:
        conditions.append(f"{prefix}sales_person_name = %s")
        params.append(filters.sales_person_name)
    
    if filters.job_status:
        placeholders = ",".join(["%s"] * len(filters.job_status))
        conditions.append(f"{prefix}opportunity_status IN ({placeholders})")
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


def apply_filters_to_query(query: str, filters: UniversalFilter, table_alias: Optional[str] = None) -> Tuple[str, tuple]:
    """
    Apply filters to a SQL query.
    
    Args:
        query: SQL query string
        filters: UniversalFilter object
        table_alias: Optional table alias (e.g., 'j' for 'jobs j'). If None, detects from query.
    
    Returns:
        Tuple of (modified_query, params_tuple)
    """
    # Detect table alias from query if not provided
    if table_alias is None:
        if "WHERE j.is_duplicate" in query or "where j.is_duplicate" in query:
            table_alias = "j"
        elif "WHERE jobs.is_duplicate" in query or "where jobs.is_duplicate" in query:
            table_alias = "jobs"
        else:
            table_alias = ""
    
    # Build where clause with detected or provided table alias
    where_clause, params = build_where_clause(filters, table_alias=table_alias if table_alias else None)
    
    # If no filters, return query as-is
    if where_clause == "1=1":
        return query, tuple()
    
    # Apply filters to query
    # Try to find WHERE clause with is_duplicate check
    if table_alias and (f"WHERE {table_alias}.is_duplicate = false" in query or f"where {table_alias}.is_duplicate = false" in query):
        query = query.replace(
            f"WHERE {table_alias}.is_duplicate = false",
            f"WHERE {table_alias}.is_duplicate = false AND {where_clause}"
        ).replace(
            f"where {table_alias}.is_duplicate = false",
            f"where {table_alias}.is_duplicate = false AND {where_clause}"
        )
    elif "WHERE is_duplicate = false" in query or "where is_duplicate = false" in query:
        query = query.replace(
            "WHERE is_duplicate = false",
            f"WHERE is_duplicate = false AND {where_clause}"
        ).replace(
            "where is_duplicate = false",
            f"where is_duplicate = false AND {where_clause}"
        )
    else:
        # If no WHERE clause found, add one before GROUP BY, ORDER BY, or LIMIT
        # This is a fallback - most queries should have WHERE is_duplicate = false
        if "GROUP BY" in query.upper():
            query = query.replace("GROUP BY", f"WHERE {where_clause}\nGROUP BY")
        elif "ORDER BY" in query.upper():
            query = query.replace("ORDER BY", f"WHERE {where_clause}\nORDER BY")
        elif "LIMIT" in query.upper():
            query = query.replace("LIMIT", f"WHERE {where_clause}\nLIMIT")
        else:
            # Last resort: append WHERE clause at the end
            query = f"{query}\nWHERE {where_clause}"
    
    return query, tuple(params)

