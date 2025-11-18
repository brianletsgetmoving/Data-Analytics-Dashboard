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
    detected_alias = table_alias
    if detected_alias is None:
        # Look for common patterns: "jobs j", "jobs as j", "FROM jobs j", etc.
        import re
        # Pattern: FROM jobs j or FROM jobs AS j or JOIN jobs j
        from_match = re.search(r'(?:FROM|JOIN)\s+jobs\s+(?:AS\s+)?(\w+)', query, re.IGNORECASE)
        if from_match:
            detected_alias = from_match.group(1)
        # Check for j.is_duplicate or jobs.is_duplicate patterns
        elif "j.is_duplicate" in query or " j." in query:
            detected_alias = "j"
        elif "jobs.is_duplicate" in query:
            detected_alias = "jobs"
        # Check for WHERE clause patterns
        elif "WHERE j." in query or "where j." in query:
            detected_alias = "j"
        elif "WHERE jobs." in query or "where jobs." in query:
            detected_alias = "jobs"
        else:
            # Default: no alias (table name used directly)
            detected_alias = None
    
    # Build where clause with detected or provided table alias
    where_clause, params = build_where_clause(filters, table_alias=detected_alias)
    
    # If no filters, return query as-is
    if where_clause == "1=1":
        return query, tuple()
    
    # Apply filters to query
    # Try to find WHERE clause with is_duplicate check (most common pattern)
    query_upper = query.upper()
    
    # Pattern 1: WHERE table_alias.is_duplicate = false
    if detected_alias:
        pattern1 = f"WHERE {detected_alias}.is_duplicate = false"
        pattern1_lower = f"where {detected_alias}.is_duplicate = false"
        if pattern1 in query or pattern1_lower in query:
            query = query.replace(pattern1, f"{pattern1} AND {where_clause}")
            query = query.replace(pattern1_lower, f"{pattern1_lower} AND {where_clause}")
            return query, tuple(params)
    
    # Pattern 2: WHERE is_duplicate = false (no table alias)
    pattern2 = "WHERE is_duplicate = false"
    pattern2_lower = "where is_duplicate = false"
    if pattern2 in query or pattern2_lower in query:
        query = query.replace(pattern2, f"{pattern2} AND {where_clause}")
        query = query.replace(pattern2_lower, f"{pattern2_lower} AND {where_clause}")
        return query, tuple(params)
    
    # Pattern 3: WHERE clause exists but doesn't have is_duplicate
    # Find the last WHERE clause and append AND
    where_positions = []
    for match in re.finditer(r'\bWHERE\b', query, re.IGNORECASE):
        where_positions.append(match.end())
    
    if where_positions:
        # Find the last WHERE and add AND before the next keyword
        last_where_pos = where_positions[-1]
        # Find the end of the WHERE clause (next AND, GROUP BY, ORDER BY, LIMIT, or end of line)
        where_end_match = re.search(
            r'(?i)(?:\s+AND\s+|\s+GROUP\s+BY\s+|\s+ORDER\s+BY\s+|\s+LIMIT\s+|$)',
            query[last_where_pos:]
        )
        if where_end_match:
            insert_pos = last_where_pos + where_end_match.start()
            # Check if there's already content after WHERE
            where_content = query[last_where_pos:insert_pos].strip()
            if where_content:
                query = query[:insert_pos] + f" AND {where_clause}" + query[insert_pos:]
            else:
                query = query[:insert_pos] + f" {where_clause}" + query[insert_pos:]
        else:
            # Append at end of WHERE clause
            query = query[:last_where_pos] + f" AND {where_clause}" + query[last_where_pos:]
        return query, tuple(params)
    
    # Pattern 4: No WHERE clause found, add one before GROUP BY, ORDER BY, or LIMIT
    if "GROUP BY" in query_upper:
        query = re.sub(r'\bGROUP BY\b', f"WHERE {where_clause}\nGROUP BY", query, flags=re.IGNORECASE, count=1)
    elif "ORDER BY" in query_upper:
        query = re.sub(r'\bORDER BY\b', f"WHERE {where_clause}\nORDER BY", query, flags=re.IGNORECASE, count=1)
    elif "LIMIT" in query_upper:
        query = re.sub(r'\bLIMIT\b', f"WHERE {where_clause}\nLIMIT", query, flags=re.IGNORECASE, count=1)
    else:
        # Last resort: append WHERE clause at the end (before semicolon if present)
        if query.rstrip().endswith(';'):
            query = query.rstrip()[:-1] + f"\nWHERE {where_clause};"
        else:
            query = f"{query}\nWHERE {where_clause}"
    
    return query, tuple(params)

