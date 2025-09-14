"""
NAV API Routes

FastAPI routes for NAV (Net Asset Value) related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
import logging

from models import NavResponse, NavListResponse, ErrorResponse
from services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database service
db_service = DatabaseService()


@router.get("/backtests/{run_id}/nav", response_model=NavListResponse)
async def get_backtest_nav(
    run_id: str,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get NAV data for a backtest."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        nav_data = db_service.get_backtest_nav(run_id, start_date, end_date)
        
        # Determine actual date range
        actual_start_date = backtest["start_date"]
        actual_end_date = backtest["end_date"]
        
        if nav_data:
            actual_start_date = min(record["nav_date"] for record in nav_data)
            actual_end_date = max(record["nav_date"] for record in nav_data)
        
        return NavListResponse(
            nav_data=nav_data,
            total=len(nav_data),
            run_id=run_id,
            start_date=actual_start_date,
            end_date=actual_end_date
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NAV data for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

