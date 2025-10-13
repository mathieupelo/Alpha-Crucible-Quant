"""
Signal API Routes

FastAPI routes for signal-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date
import logging

from models import SignalResponse, ScoreResponse, ErrorResponse
from services.database_service import DatabaseService

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
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        # Get signals from database service
        signals = db_service.get_signals_raw(
            tickers=tickers,
            signal_names=signal_names,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "signals": [SignalResponse(**signal) for signal in signals],
            "total": len(signals),
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
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
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
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        scores = db_service.get_portfolio_scores(portfolio_id)
        return {
            "scores": scores,
            "total": len(scores),
            "portfolio_id": portfolio_id
        }
    except Exception as e:
        logger.error(f"Error getting scores for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signal-types")
async def get_available_signal_types():
    """Get list of available signal types from the database."""
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        # Query distinct signal names from the database
        query = "SELECT DISTINCT signal_name FROM signal_raw ORDER BY signal_name"
        signals_df = db_service.db_manager.execute_query(query)
        
        if signals_df.empty:
            return {
                "signal_types": [],
                "total": 0
            }
        
        # Convert database results to API format
        signal_types = []
        for _, row in signals_df.iterrows():
            signal_name = row['signal_name']
            signal_types.append({
                "signal_id": signal_name.lower().replace('_', '_'),
                "name": signal_name,
                "parameters": {},
                "min_lookback": 1,
                "max_lookback": 252
            })
        
        return {
            "signal_types": signal_types,
            "total": len(signal_types)
        }
    except Exception as e:
        logger.error(f"Error getting available signal types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

