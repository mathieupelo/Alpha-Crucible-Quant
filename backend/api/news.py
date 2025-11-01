"""
News API Routes

FastAPI routes for news and sentiment analysis endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from services.news_service import news_service
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
db_service = DatabaseService()


@router.get("/news/universe/{universe_name}")
async def get_universe_news(
    universe_name: str,
    max_items: int = Query(10, ge=1, le=50, description="Maximum number of news items to return")
):
    """
    Get aggregated news for all tickers in a universe.
    
    Args:
        universe_name: Name of the universe (e.g., "GameCore-12 (GC-12)" or URL-encoded)
        max_items: Maximum number of news items to return
        
    Returns:
        List of news items with sentiment analysis
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        # URL decode the universe name
        from urllib.parse import unquote
        decoded_name = unquote(universe_name)
        logger.info(f"Fetching news for universe: '{decoded_name}' (original: '{universe_name}')")
        
        # Get universe by name
        universe = db_service.db_manager.get_universe_by_name(decoded_name)
        
        # If not found, try to find by similar name (e.g., "GameCore-12" instead of "GameCore-12 (GC-12)")
        if universe is None:
            logger.warning(f"Universe '{decoded_name}' not found, searching for similar names...")
            all_universes = db_service.get_all_universes()
            logger.info(f"Available universes: {[u['name'] for u in all_universes]}")
            
            # Try to find by partial match (e.g., "GameCore" in "GameCore-12 (GC-12)")
            for u in all_universes:
                if "GameCore" in decoded_name or decoded_name in u['name'] or "GameCore" in u['name']:
                    logger.info(f"Found similar universe: {u['name']}, using it")
                    universe_id = u['id']
                    # Get universe by ID instead
                    universe_dict = db_service.get_universe_by_id(universe_id)
                    if universe_dict:
                        # Create a minimal universe object for compatibility
                        from src.database.models import Universe
                        universe = Universe(
                            id=universe_dict['id'],
                            name=universe_dict['name'],
                            description=universe_dict.get('description'),
                            created_at=None,
                            updated_at=None
                        )
                        break
            
            if universe is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Universe '{decoded_name}' not found. Available universes: {[u['name'] for u in all_universes]}"
                )
        
        # Get universe tickers
        # Convert universe.id to native Python int (may be numpy.int64)
        universe_id = int(universe.id)
        tickers_df = db_service.db_manager.get_universe_tickers(universe_id)
        if tickers_df.empty:
            logger.warning(f"No tickers found for universe {universe.name}")
            return {
                "universe_name": universe.name,
                "tickers": [],
                "news": [],
                "total": 0
            }
        
        tickers = tickers_df['ticker'].tolist()
        logger.info(f"Fetching news for {len(tickers)} tickers: {tickers}")
        
        # Fetch news for all tickers
        news_items = news_service.fetch_universe_news(
            tickers=tickers,
            max_items_per_ticker=5,
            total_max_items=max_items
        )
        
        logger.info(f"Retrieved {len(news_items)} news items")
        
        return {
            "universe_name": universe.name,
            "tickers": tickers,
            "news": news_items,
            "total": len(news_items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news for universe {universe_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/ticker/{ticker}")
async def get_ticker_news(
    ticker: str,
    max_items: int = Query(10, ge=1, le=50, description="Maximum number of news items to return")
):
    """
    Get news for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        max_items: Maximum number of news items to return
        
    Returns:
        List of news items with sentiment analysis
    """
    try:
        news_items = news_service.fetch_ticker_news(ticker, max_items)
        
        return {
            "ticker": ticker,
            "news": news_items,
            "total": len(news_items)
        }
        
    except Exception as e:
        logger.error(f"Error fetching news for ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/tickers")
async def get_multiple_tickers_news(
    tickers: str = Query(..., description="Comma-separated list of ticker symbols"),
    max_items: int = Query(10, ge=1, le=50, description="Maximum number of news items to return")
):
    """
    Get aggregated news for multiple tickers.
    
    Args:
        tickers: Comma-separated list of ticker symbols
        max_items: Maximum number of news items to return
        
    Returns:
        List of aggregated news items with sentiment analysis
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(',') if t.strip()]
        
        if not ticker_list:
            raise HTTPException(status_code=400, detail="No valid tickers provided")
        
        news_items = news_service.fetch_universe_news(
            tickers=ticker_list,
            max_items_per_ticker=5,
            total_max_items=max_items
        )
        
        return {
            "tickers": ticker_list,
            "news": news_items,
            "total": len(news_items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news for tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

