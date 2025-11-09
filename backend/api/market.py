"""
Market Data API Routes

FastAPI routes for market data related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
import logging
import pandas as pd
import yfinance as yf

from security.input_validation import validate_ticker, validate_date_range, validate_numeric_range
from models import ErrorResponse
from src.utils.price_fetcher import PriceFetcher

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
        # Validate and sanitize inputs
        validated_symbol = validate_ticker(symbol)
        start_date, end_date = validate_date_range(start_date, end_date)
        
        # Fetch price history
        price_data = price_fetcher.get_price_history(
            validated_symbol, 
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
            "symbol": validated_symbol,
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
        # Validate inputs
        validated_symbol = validate_ticker(symbol)
        start_date, end_date = validate_date_range(start_date, end_date)
        start_value = validate_numeric_range(start_value, 0.01, 1000000.0, "start_value")
        
        # Get raw market data
        market_response = await get_market_data(validated_symbol, start_date, end_date)
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
            "symbol": validated_symbol,
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


@router.get("/market-data/live/{symbol}")
async def get_live_price(symbol: str):
    """Get live/current price and daily variation for a symbol."""
    try:
        # Validate ticker
        validated_symbol = validate_ticker(symbol)
        
        # Fetch live data using yfinance
        ticker = yf.Ticker(validated_symbol)
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        previous_close = info.get('previousClose')
        
        if current_price is None or previous_close is None:
            # Fallback: try to get from history
            try:
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No live price data available for symbol {symbol}"
                    )
            except Exception as e:
                logger.error(f"Error fetching live price for {symbol}: {e}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No live price data available for symbol {symbol}"
                )
        
        # Calculate daily variation
        daily_change = current_price - previous_close
        daily_change_percent = (daily_change / previous_close) * 100 if previous_close > 0 else 0
        
        return {
            "symbol": validated_symbol,
            "price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "daily_change": round(daily_change, 2),
            "daily_change_percent": round(daily_change_percent, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market-data/live/batch")
async def get_live_prices_batch(tickers: List[str]):
    """Get live prices for multiple tickers."""
    try:
        results = []
        
        for ticker_symbol in tickers:
            try:
                validated_symbol = validate_ticker(ticker_symbol)
                ticker = yf.Ticker(validated_symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                previous_close = info.get('previousClose')
                
                if current_price is None or previous_close is None:
                    # Fallback to history
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                    else:
                        results.append({
                            "symbol": validated_symbol,
                            "price": None,
                            "previous_close": None,
                            "daily_change": None,
                            "daily_change_percent": None,
                            "error": "No data available"
                        })
                        continue
                
                daily_change = current_price - previous_close
                daily_change_percent = (daily_change / previous_close) * 100 if previous_close > 0 else 0
                
                results.append({
                    "symbol": validated_symbol,
                    "price": round(current_price, 2),
                    "previous_close": round(previous_close, 2),
                    "daily_change": round(daily_change, 2),
                    "daily_change_percent": round(daily_change_percent, 2),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"Error fetching live price for {ticker_symbol}: {e}")
                results.append({
                    "symbol": ticker_symbol,
                    "price": None,
                    "previous_close": None,
                    "daily_change": None,
                    "daily_change_percent": None,
                    "error": str(e)
                })
        
        return {
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting live prices batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-data/{symbol}/intraday")
async def get_intraday_price_data(symbol: str):
    """
    Get intraday price data for today (5-minute intervals from market open to current time).
    If market is closed, returns the last trading day's data.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Intraday price data with timestamps
    """
    try:
        validated_symbol = validate_ticker(symbol)
        
        # Fetch intraday data using yfinance (5-minute intervals)
        ticker = yf.Ticker(validated_symbol)
        
        # Get intraday data - yfinance will return the last available trading day if market is closed
        # Use '1d' period with '5m' interval for intraday
        intraday_data = ticker.history(period="1d", interval="5m")
        
        if intraday_data.empty:
            # Try to get data from the last 5 days
            intraday_data = ticker.history(period="5d", interval="5m")
            if intraday_data.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No intraday data available for symbol {symbol}"
                )
            # Use the most recent day's data
            last_date = intraday_data.index[-1].date()
            # Filter by date: convert index to date and compare
            intraday_data = intraday_data[[idx.date() == last_date for idx in intraday_data.index]]
        
        # Extract the actual date from the data (use the first timestamp's date)
        if not intraday_data.empty:
            data_date = intraday_data.index[0].date()
        else:
            data_date = date.today()
        
        # Convert to list of dictionaries
        intraday_points = []
        for timestamp, row in intraday_data.iterrows():
            # Convert to ISO format string
            timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            intraday_points.append({
                "timestamp": timestamp_str,
                "datetime": timestamp.isoformat(),
                "open": float(row['Open']) if pd.notna(row['Open']) else None,
                "high": float(row['High']) if pd.notna(row['High']) else None,
                "low": float(row['Low']) if pd.notna(row['Low']) else None,
                "close": float(row['Close']) if pd.notna(row['Close']) else None,
                "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
        
        return {
            "symbol": validated_symbol,
            "date": data_date.isoformat(),
            "data": intraday_points,
            "total_points": len(intraday_points),
            "interval": "5m"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting intraday price data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))