"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .api.v1 import (
    analytics,
    customers,
    jobs,
    revenue,
    leads,
    sales,
    profitability,
    customer_behavior,
    operational,
    benchmarking,
    forecasting,
    filter_options,
)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix=f"{settings.api_prefix}/analytics", tags=["analytics"])
app.include_router(customers.router, prefix=f"{settings.api_prefix}/customers", tags=["customers"])
app.include_router(jobs.router, prefix=f"{settings.api_prefix}/jobs", tags=["jobs"])
app.include_router(revenue.router, prefix=f"{settings.api_prefix}/revenue", tags=["revenue"])
app.include_router(leads.router, prefix=f"{settings.api_prefix}/leads", tags=["leads"])
app.include_router(sales.router, prefix=f"{settings.api_prefix}/sales", tags=["sales"])
app.include_router(profitability.router, prefix=f"{settings.api_prefix}/profitability", tags=["profitability"])
app.include_router(customer_behavior.router, prefix=f"{settings.api_prefix}/customer-behavior", tags=["customer-behavior"])
app.include_router(operational.router, prefix=f"{settings.api_prefix}/operational", tags=["operational"])
app.include_router(benchmarking.router, prefix=f"{settings.api_prefix}/benchmarking", tags=["benchmarking"])
app.include_router(forecasting.router, prefix=f"{settings.api_prefix}/forecasting", tags=["forecasting"])
app.include_router(filter_options.router, prefix=f"{settings.api_prefix}/filter-options", tags=["filter-options"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Analytics Dashboard API",
        "version": settings.api_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the full error for debugging
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal error details to clients
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )

