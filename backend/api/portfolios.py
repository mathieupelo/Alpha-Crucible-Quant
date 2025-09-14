"""
Portfolio API Routes

FastAPI routes for portfolio-related endpoints.
"""

from fastapi import APIRouter, HTTPException
import logging

from models import PortfolioResponse, PositionResponse, ErrorResponse
from services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database service
db_service = DatabaseService()


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int):
    """Get specific portfolio by ID."""
    try:
        portfolio = db_service.get_portfolio_details(portfolio_id)
        if portfolio is None:
            raise HTTPException(status_code=404, detail=f"Portfolio {portfolio_id} not found")
        return PortfolioResponse(**portfolio)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolios/{portfolio_id}/positions")
async def get_portfolio_positions(portfolio_id: int):
    """Get all positions for a portfolio."""
    try:
        portfolio = db_service.get_portfolio_details(portfolio_id)
        if portfolio is None:
            raise HTTPException(status_code=404, detail=f"Portfolio {portfolio_id} not found")
        
        positions = portfolio.get("positions", [])
        return {
            "positions": positions,
            "total": len(positions),
            "portfolio_id": portfolio_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting positions for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolios/{portfolio_id}/signals")
async def get_portfolio_signals(portfolio_id: int):
    """Get signal scores for a portfolio."""
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
    """Get combined scores for a portfolio."""
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


@router.get("/portfolios/{portfolio_id}/universe-tickers")
async def get_portfolio_universe_tickers(portfolio_id: int):
    """Get all universe tickers for a portfolio."""
    try:
        portfolio = db_service.get_portfolio_details(portfolio_id)
        if portfolio is None:
            raise HTTPException(status_code=404, detail=f"Portfolio {portfolio_id} not found")
        
        universe_tickers = db_service.get_universe_tickers(int(portfolio["universe_id"]))
        return {
            "tickers": [ticker["ticker"] for ticker in universe_tickers],
            "total": len(universe_tickers),
            "portfolio_id": portfolio_id,
            "universe_id": int(portfolio["universe_id"])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting universe tickers for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))