"""Pagination utilities."""
from typing import Dict, Any


def get_pagination_meta(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """Calculate pagination metadata."""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }

