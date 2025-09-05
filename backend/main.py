"""
Alpha Crucible Quant - FastAPI Main Application

Main FastAPI application providing REST API endpoints for the quantitative trading system.
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Add src to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from api import backtests, portfolios, signals, nav
from models import ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Alpha Crucible Quant API",
    description="REST API for Alpha Crucible quantitative trading system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(backtests.router, prefix="/api", tags=["backtests"])
app.include_router(portfolios.router, prefix="/api", tags=["portfolios"])
app.include_router(signals.router, prefix="/api", tags=["signals"])
app.include_router(nav.router, prefix="/api", tags=["nav"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Alpha Crucible Quant API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "alpha-crucible-api"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            details=str(exc)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

