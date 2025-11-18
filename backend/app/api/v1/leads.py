"""Lead analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/demographics", response_model=AnalyticsResponse)
async def get_lead_demographics(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get lead demographics."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            ls.branch_name,
            ls.status,
            COUNT(*) as lead_count,
            COUNT(*) FILTER (WHERE bo.id IS NOT NULL) as converted_count
        FROM lead_status ls
        LEFT JOIN booked_opportunities bo ON ls.quote_number = bo.quote_number
        WHERE {where_clause.replace('job_date', 'ls.created_at').replace('branch_name', 'ls.branch_name')}
        GROUP BY ls.branch_name, ls.status
        ORDER BY lead_count DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/conversion-funnel", response_model=AnalyticsResponse)
async def get_conversion_funnel(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get lead conversion funnel."""
    query = """
        SELECT 
            'Total Leads' as stage,
            COUNT(*) as count
        FROM lead_status
        UNION ALL
        SELECT 
            'Quoted' as stage,
            COUNT(*) as count
        FROM booked_opportunities 
        WHERE status IN ('Quoted', 'Pending')
        UNION ALL
        SELECT 
            'Booked' as stage,
            COUNT(*) as count
        FROM booked_opportunities 
        WHERE status IN ('Booked', 'Closed')
        UNION ALL
        SELECT 
            'Closed' as stage,
            COUNT(*) as count
        FROM booked_opportunities 
        WHERE status = 'Closed'
        UNION ALL
        SELECT 
            'Lost' as stage,
            COUNT(*) as count
        FROM lost_leads
    """
    
    results = db.execute_query(query)
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/response-time", response_model=AnalyticsResponse)
async def get_response_time(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get lead response time analysis."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            ls.time_to_contact,
            COUNT(*) as lead_count,
            COUNT(*) FILTER (WHERE bo.id IS NOT NULL) as converted_count
        FROM lead_status ls
        LEFT JOIN booked_opportunities bo ON ls.quote_number = bo.quote_number
        WHERE {where_clause.replace('job_date', 'ls.created_at').replace('branch_name', 'ls.branch_name')}
        AND ls.time_to_contact IS NOT NULL
        GROUP BY ls.time_to_contact
        ORDER BY lead_count DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/source-performance", response_model=AnalyticsResponse)
async def get_source_performance(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get lead source performance."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            ls.referral_source,
            COUNT(*) as total_leads,
            COUNT(*) FILTER (WHERE bo.id IS NOT NULL) as converted_leads,
            ROUND(COUNT(*) FILTER (WHERE bo.id IS NOT NULL)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as conversion_rate
        FROM lead_status ls
        LEFT JOIN booked_opportunities bo ON ls.quote_number = bo.quote_number
        WHERE {where_clause.replace('job_date', 'ls.created_at').replace('branch_name', 'ls.branch_name')}
        AND ls.referral_source IS NOT NULL
        GROUP BY ls.referral_source
        ORDER BY conversion_rate DESC, total_leads DESC
        LIMIT 30
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/status-distribution", response_model=AnalyticsResponse)
async def get_status_distribution(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get lead status distribution."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) as percentage
        FROM lead_status ls
        WHERE {where_clause.replace('job_date', 'ls.created_at').replace('branch_name', 'ls.branch_name')}
        GROUP BY status
        ORDER BY count DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

