"""
Backtest API Routes

FastAPI routes for backtest-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
import logging

from models import BacktestResponse, BacktestListResponse, BacktestMetricsResponse, ErrorResponse
from services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database service
db_service = DatabaseService()


@router.get("/backtests", response_model=BacktestListResponse)
async def get_backtests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size")
):
    """Get all backtests with pagination."""
    try:
        result = db_service.get_all_backtests(page=page, size=size)
        return BacktestListResponse(**result)
    except Exception as e:
        logger.error(f"Error getting backtests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}", response_model=BacktestResponse)
async def get_backtest(run_id: str):
    """Get specific backtest by run ID."""
    try:
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        return BacktestResponse(**backtest)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backtest {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/metrics", response_model=BacktestMetricsResponse)
async def get_backtest_metrics(run_id: str):
    """Get performance metrics for a backtest."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        metrics = db_service.get_backtest_metrics(run_id)
        if metrics is None:
            raise HTTPException(status_code=404, detail=f"No metrics available for backtest {run_id}")
        
        return BacktestMetricsResponse(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/portfolios")
async def get_backtest_portfolios(run_id: str):
    """Get all portfolios for a backtest."""
    try:
        portfolios = db_service.get_backtest_portfolios(run_id)
        return {
            "portfolios": portfolios,
            "total": len(portfolios),
            "run_id": run_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolios for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/signals")
async def get_backtest_signals(
    run_id: str,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get raw signals for a backtest period."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        signals = db_service.get_backtest_signals(run_id, start_date, end_date)
        return {
            "signals": signals,
            "total": len(signals),
            "run_id": run_id,
            "start_date": start_date,
            "end_date": end_date
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signals for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/scores")
async def get_backtest_scores(
    run_id: str,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get combined scores for a backtest period."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        scores = db_service.get_backtest_scores(run_id, start_date, end_date)
        return {
            "scores": scores,
            "total": len(scores),
            "run_id": run_id,
            "start_date": start_date,
            "end_date": end_date
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scores for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

