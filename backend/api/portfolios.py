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

