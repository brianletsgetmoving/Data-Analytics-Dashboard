"""SQL query loader utility."""
import os
from pathlib import Path
from typing import Optional


def load_sql_query(query_name: str, subdirectory: Optional[str] = None) -> str:
    """
    Load SQL query from sql/queries directory.
    
    Args:
        query_name: Name of the SQL file (without .sql extension)
        subdirectory: Optional subdirectory (e.g., 'profitability', 'forecasting')
    
    Returns:
        SQL query string
    """
    # Get the project root (assuming backend/app is the current location)
    current_dir = Path(__file__).parent.parent.parent.parent
    
    # Build path to SQL queries
    if subdirectory:
        sql_path = current_dir / "sql" / "queries" / subdirectory / f"{query_name}.sql"
    else:
        sql_path = current_dir / "sql" / "queries" / f"{query_name}.sql"
    
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL query not found: {sql_path}")
    
    with open(sql_path, "r", encoding="utf-8") as f:
        return f.read()


def parameterize_query(query: str, filters: dict) -> tuple[str, tuple]:
    """
    Parameterize SQL query with filters.
    
    Args:
        query: SQL query string
        filters: Dictionary of filter parameters
    
    Returns:
        Tuple of (parameterized_query, params_tuple)
    """
    # This is a simplified version - in production, you'd want more robust parameterization
    # For now, we'll rely on the build_where_clause utility from filters.py
    return query, tuple()

