"""
Market Data API Routes

FastAPI routes for market data related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date
import logging
import sys
from pathlib import Path

# Add src to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from models import ErrorResponse
from utils.price_fetcher import PriceFetcher
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize price fetcher
price_fetcher = PriceFetcher()


@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    start_date: date = Query(..., description="Start date for market data"),
    end_date: date = Query(..., description="End date for market data")
):
    """Get market data for a symbol over a date range."""
    try:
        # Validate symbol
        if not symbol or len(symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="Symbol cannot be empty")
        
        # Fetch price history
        price_data = price_fetcher.get_price_history(
            symbol.upper().strip(), 
            start_date, 
            end_date
        )
        
        if price_data is None or price_data.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No market data found for symbol {symbol} in the specified date range"
            )
        
        # Convert to list of dictionaries
        market_data = []
        for date_idx, row in price_data.iterrows():
            market_data.append({
                "date": date_idx.strftime("%Y-%m-%d"),
                "close": float(row['Close']),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
        
        return {
            "symbol": symbol.upper(),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "data": market_data,
            "total_points": len(market_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-data/{symbol}/normalized")
async def get_normalized_market_data(
    symbol: str,
    start_date: date = Query(..., description="Start date for market data"),
    end_date: date = Query(..., description="End date for market data"),
    start_value: float = Query(100.0, description="Starting value for normalization")
):
    """Get normalized market data for a symbol over a date range."""
    try:
        # Get raw market data
        market_response = await get_market_data(symbol, start_date, end_date)
        market_data = market_response["data"]
        
        if not market_data:
            return market_response
        
        # Get the first close price for normalization
        first_close = market_data[0]["close"]
        
        # Normalize all prices to start_value
        normalized_data = []
        for point in market_data:
            normalized_value = (point["close"] / first_close) * start_value
            normalized_data.append({
                "date": point["date"],
                "value": normalized_value,
                "return_since_start": ((point["close"] / first_close) - 1) * 100
            })
        
        return {
            "symbol": symbol.upper(),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "start_value": start_value,
            "data": normalized_data,
            "total_points": len(normalized_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting normalized market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
