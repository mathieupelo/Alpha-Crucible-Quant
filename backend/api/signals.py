"""
Signal API Routes

FastAPI routes for signal-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date
import logging

from models import SignalResponse, ScoreResponse, ErrorResponse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
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


@router.get("/signal-types")
async def get_available_signal_types():
    """Get list of available signal types."""
    try:
        # Get available signal types from the signal registry
        import sys
        import os
        from pathlib import Path
        
        # Add src to path
        src_path = Path(__file__).parent.parent.parent / 'src'
        sys.path.insert(0, str(src_path))
        
        from signals.registry import SignalRegistry
        registry = SignalRegistry()
        available_signals = registry.get_available_signals()
        
        # Get signal information for each available signal
        signals_info = []
        for signal_id in available_signals:
            signal_info = registry.get_signal_info(signal_id)
            if signal_info:
                signals_info.append({
                    "signal_id": signal_info["signal_id"],
                    "name": signal_info["name"],
                    "parameters": signal_info["parameters"],
                    "min_lookback": signal_info["min_lookback"],
                    "max_lookback": signal_info["max_lookback"]
                })
        
        return {
            "signal_types": signals_info,
            "total": len(signals_info)
        }
    except Exception as e:
        logger.error(f"Error getting available signal types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

