"""
Universe API Routes

FastAPI routes for universe management endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from models import (
    UniverseResponse, UniverseListResponse, UniverseTickerResponse, 
    UniverseTickerListResponse, TickerValidationResponse,
    UniverseCreateRequest, UniverseUpdateRequest, UniverseTickerUpdateRequest,
    ErrorResponse, SuccessResponse
)
from services import DatabaseService
from services.ticker_validation_service import TickerValidationService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
db_service = DatabaseService()
ticker_validator = TickerValidationService()


@router.get("/universes", response_model=UniverseListResponse)
async def get_universes():
    """Get all universes."""
    try:
        universes = db_service.get_all_universes()
        return UniverseListResponse(
            universes=[UniverseResponse(**universe) for universe in universes],
            total=len(universes)
        )
    except Exception as e:
        logger.error(f"Error getting universes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/universes/{universe_id}", response_model=UniverseResponse)
async def get_universe(universe_id: int):
    """Get a specific universe by ID."""
    try:
        universe = db_service.get_universe_by_id(universe_id)
        if universe is None:
            raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
        return UniverseResponse(**universe)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/universes", response_model=UniverseResponse)
async def create_universe(request: UniverseCreateRequest):
    """Create a new universe."""
    try:
        universe = db_service.create_universe(
            name=request.name,
            description=request.description
        )
        return UniverseResponse(**universe)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating universe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/universes/{universe_id}", response_model=UniverseResponse)
async def update_universe(universe_id: int, request: UniverseUpdateRequest):
    """Update an existing universe."""
    try:
        universe = db_service.update_universe(
            universe_id=universe_id,
            name=request.name,
            description=request.description
        )
        if universe is None:
            raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
        return UniverseResponse(**universe)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/universes/{universe_id}", response_model=SuccessResponse)
async def delete_universe(universe_id: int):
    """Delete a universe and all its tickers."""
    try:
        success = db_service.delete_universe(universe_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
        return SuccessResponse(message=f"Universe {universe_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/universes/{universe_id}/tickers", response_model=UniverseTickerListResponse)
async def get_universe_tickers(universe_id: int):
    """Get all tickers for a universe."""
    try:
        # Check if universe exists
        universe = db_service.get_universe_by_id(universe_id)
        if universe is None:
            raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
        
        tickers = db_service.get_universe_tickers(universe_id)
        return UniverseTickerListResponse(
            tickers=[UniverseTickerResponse(**ticker) for ticker in tickers],
            total=len(tickers),
            universe_id=universe_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tickers for universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/universes/{universe_id}/tickers", response_model=UniverseTickerListResponse)
async def update_universe_tickers(universe_id: int, request: UniverseTickerUpdateRequest):
    """Update all tickers for a universe."""
    try:
        # Check if universe exists
        universe = db_service.get_universe_by_id(universe_id)
        if universe is None:
            raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
        
        # Update tickers
        tickers = db_service.update_universe_tickers(universe_id, request.tickers)
        return UniverseTickerListResponse(
            tickers=[UniverseTickerResponse(**ticker) for ticker in tickers],
            total=len(tickers),
            universe_id=universe_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tickers for universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/universes/{universe_id}/tickers", response_model=UniverseTickerResponse)
async def add_universe_ticker(universe_id: int, ticker: str = Query(..., description="Ticker symbol to add")):
    """Add a single ticker to a universe."""
    try:
        ticker_data = db_service.add_universe_ticker(universe_id, ticker)
        return UniverseTickerResponse(**ticker_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding ticker {ticker} to universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/universes/{universe_id}/tickers/{ticker}", response_model=SuccessResponse)
async def remove_universe_ticker(universe_id: int, ticker: str):
    """Remove a ticker from a universe."""
    try:
        success = db_service.remove_universe_ticker(universe_id, ticker)
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found in universe {universe_id}")
        return SuccessResponse(message=f"Ticker {ticker} removed from universe {universe_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing ticker {ticker} from universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickers/validate", response_model=List[TickerValidationResponse])
async def validate_tickers(tickers: List[str]):
    """Validate multiple ticker symbols."""
    try:
        if not tickers:
            return []
        
        # Clean and deduplicate tickers
        clean_tickers = list(set(ticker.strip().upper() for ticker in tickers if ticker.strip()))
        
        if not clean_tickers:
            return []
        
        # Validate tickers
        results = ticker_validator.validate_tickers_batch(clean_tickers)
        
        return [TickerValidationResponse(**result) for result in results]
    except Exception as e:
        logger.error(f"Error validating tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
