"""Revenue analytics endpoints."""
from fastapi import APIRouter, Depends

from ...schemas.analytics import AnalyticsResponse
from ...schemas.filters import UniversalFilter
from ...database import db
from ...utils.filters import build_where_clause, get_aggregation_period_sql
from ...api.dependencies import get_filters

router = APIRouter()


@router.get("/trends", response_model=AnalyticsResponse)
async def get_revenue_trends(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get revenue trends over time."""
    where_clause, params = build_where_clause(filters)
    period_sql = get_aggregation_period_sql(filters.aggregation_period or "monthly")
    
    query = f"""
        SELECT 
            {period_sql} as period,
            COUNT(*) as job_count,
            SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) as revenue,
            SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) FILTER (WHERE opportunity_status = 'BOOKED') as booked_revenue,
            SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) FILTER (WHERE opportunity_status = 'CLOSED') as closed_revenue
        FROM jobs j
        WHERE {where_clause}
        AND job_date IS NOT NULL
        GROUP BY {period_sql}
        ORDER BY {period_sql} DESC
        LIMIT 24
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"period": filters.aggregation_period, "count": len(results)},
        filters_applied=filters,
    )


@router.get("/by-branch", response_model=AnalyticsResponse)
async def get_revenue_by_branch(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get revenue by branch."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            branch_name,
            COUNT(*) as job_count,
            SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
            AVG(COALESCE(total_actual_cost, total_estimated_cost, 0)) as avg_job_value
        FROM jobs j
        WHERE {where_clause}
        AND opportunity_status IN ('BOOKED', 'CLOSED')
        AND branch_name IS NOT NULL
        GROUP BY branch_name
        ORDER BY total_revenue DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/by-region", response_model=AnalyticsResponse)
async def get_revenue_by_region(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get revenue by geographic region."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            origin_state as state,
            origin_city as city,
            COUNT(*) as job_count,
            SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) as total_revenue
        FROM jobs j
        WHERE {where_clause}
        AND opportunity_status IN ('BOOKED', 'CLOSED')
        AND origin_state IS NOT NULL
        GROUP BY origin_state, origin_city
        ORDER BY total_revenue DESC
        LIMIT 50
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/by-source", response_model=AnalyticsResponse)
async def get_revenue_by_source(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get revenue by referral source."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            referral_source,
            COUNT(*) as job_count,
            SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) as total_revenue,
            AVG(COALESCE(total_actual_cost, total_estimated_cost, 0)) as avg_job_value
        FROM jobs j
        WHERE {where_clause}
        AND opportunity_status IN ('BOOKED', 'CLOSED')
        AND referral_source IS NOT NULL
        GROUP BY referral_source
        ORDER BY total_revenue DESC
        LIMIT 30
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/forecasts", response_model=AnalyticsResponse)
async def get_revenue_forecasts(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get revenue forecasts based on historical trends."""
    where_clause, params = build_where_clause(filters)
    
    # Simple moving average forecast
    query = f"""
        WITH monthly_revenue AS (
            SELECT 
                DATE_TRUNC('month', job_date) as month,
                SUM(COALESCE(total_actual_cost, total_estimated_cost, 0)) as revenue
            FROM jobs j
            WHERE {where_clause}
            AND job_date IS NOT NULL
            AND opportunity_status IN ('BOOKED', 'CLOSED')
            GROUP BY DATE_TRUNC('month', job_date)
            ORDER BY month DESC
            LIMIT 12
        )
        SELECT 
            month,
            revenue,
            AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as forecast_3month_avg,
            AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) as forecast_6month_avg
        FROM monthly_revenue
        ORDER BY month DESC
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )


@router.get("/by-segment", response_model=AnalyticsResponse)
async def get_revenue_by_segment(
    filters: UniversalFilter = Depends(get_filters),
):
    """Get revenue by customer value segment."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        WITH customer_segments AS (
            SELECT 
                c.id as customer_id,
                SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) as total_revenue,
                CASE 
                    WHEN SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) < 500 THEN '<$500'
                    WHEN SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) < 1000 THEN '$500-$1000'
                    WHEN SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) < 1500 THEN '$1000-$1500'
                    WHEN SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) < 2000 THEN '$1500-$2000'
                    WHEN SUM(COALESCE(j.total_actual_cost, j.total_estimated_cost, 0)) < 2500 THEN '$2000-$2500'
                    ELSE '>$2500'
                END as segment
            FROM customers c
            LEFT JOIN jobs j ON c.id = j.customer_id
            WHERE {where_clause.replace('job_date', 'j.job_date').replace('branch_name', 'j.branch_name')}
            AND j.opportunity_status IN ('BOOKED', 'CLOSED')
            GROUP BY c.id
        )
        SELECT 
            segment,
            COUNT(*) as customer_count,
            SUM(total_revenue) as segment_revenue,
            AVG(total_revenue) as avg_revenue_per_customer
        FROM customer_segments
        WHERE total_revenue > 0
        GROUP BY segment
        ORDER BY 
            CASE segment
                WHEN '<$500' THEN 1
                WHEN '$500-$1000' THEN 2
                WHEN '$1000-$1500' THEN 3
                WHEN '$1500-$2000' THEN 4
                WHEN '$2000-$2500' THEN 5
                ELSE 6
            END
    """
    
    results = db.execute_query(query, tuple(params))
    
    return AnalyticsResponse(
        data=results,
        metadata={"count": len(results)},
        filters_applied=filters,
    )

