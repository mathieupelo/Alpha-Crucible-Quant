"""
Alpha Crucible Quant - FastAPI Main Application

Main FastAPI application providing REST API endpoints for the quantitative trading system.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from typing import List

from api import backtests, portfolios, signals, nav, universes, market
from models import ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080,https://*.ngrok-free.dev").split(",")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
API_KEY = os.getenv("API_KEY", "dev-key-change-in-production")

# Create FastAPI app
app = FastAPI(
    title="Alpha Crucible Quant API",
    description="REST API for Alpha Crucible quantitative trading system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with restricted origins
def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed, including dynamic ngrok domains"""
    if origin in ALLOWED_ORIGINS:
        return True
    # Allow any ngrok domain
    if origin and origin.endswith('.ngrok-free.dev'):
        return True
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.ngrok-free\.dev|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Rate limiting middleware
from collections import defaultdict
import time

request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "message": "Too many requests"}
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

# Authentication
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for protected endpoints."""
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# Include API routers with authentication for sensitive endpoints
app.include_router(backtests.router, prefix="/api", tags=["backtests"], dependencies=[Depends(verify_api_key)])
app.include_router(portfolios.router, prefix="/api", tags=["portfolios"], dependencies=[Depends(verify_api_key)])
app.include_router(signals.router, prefix="/api", tags=["signals"], dependencies=[Depends(verify_api_key)])
app.include_router(nav.router, prefix="/api", tags=["nav"], dependencies=[Depends(verify_api_key)])
app.include_router(universes.router, prefix="/api", tags=["universes"], dependencies=[Depends(verify_api_key)])
app.include_router(market.router, prefix="/api", tags=["market"], dependencies=[Depends(verify_api_key)])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Alpha Crucible Quant API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "alpha-crucible-api"}

@app.get("/api/health/db")
async def health_check_db():
    """Database health check endpoint."""
    try:
        from services.database_service import DatabaseService
        db_service = DatabaseService()
        if db_service.is_connected():
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "degraded", "database": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "error": str(e)}

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

