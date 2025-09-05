"""
Signal API Routes

FastAPI routes for signal-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date
import logging

from models import SignalResponse, ScoreResponse, ErrorResponse
from services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database service
db_service = DatabaseService()


@router.get("/signals")
async def get_signals(
    tickers: Optional[List[str]] = Query(None, description="Filter by tickers"),
    signal_names: Optional[List[str]] = Query(None, description="Filter by signal names"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get raw signals with optional filtering."""
    try:
        # This would need to be implemented in the database service
        # For now, return empty list
        return {
            "signals": [],
            "total": 0,
            "filters": {
                "tickers": tickers,
                "signal_names": signal_names,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scores")
async def get_scores(
    tickers: Optional[List[str]] = Query(None, description="Filter by tickers"),
    methods: Optional[List[str]] = Query(None, description="Filter by combination methods"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get combined scores with optional filtering."""
    try:
        # This would need to be implemented in the database service
        # For now, return empty list
        return {
            "scores": [],
            "total": 0,
            "filters": {
                "tickers": tickers,
                "methods": methods,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        logger.error(f"Error getting scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolios/{portfolio_id}/signals")
async def get_portfolio_signals(portfolio_id: int):
    """Get signal scores for a specific portfolio."""
    try:
        signals = db_service.get_portfolio_signals(portfolio_id)
        return {
            "signals": signals,
            "total": len(signals),
            "portfolio_id": portfolio_id
        }
    except Exception as e:
        logger.error(f"Error getting signals for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolios/{portfolio_id}/scores")
async def get_portfolio_scores(portfolio_id: int):
    """Get combined scores for a specific portfolio."""
    try:
        scores = db_service.get_portfolio_scores(portfolio_id)
        return {
            "scores": scores,
            "total": len(scores),
            "portfolio_id": portfolio_id
        }
    except Exception as e:
        logger.error(f"Error getting scores for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

