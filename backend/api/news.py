"""
News API Routes

FastAPI routes for news and sentiment analysis endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
import logging
from collections import defaultdict
import os

from services.news_service import news_service
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
db_service = DatabaseService()

# OpenAI setup - Load .env first if not already loaded
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env file (in case main.py hasn't loaded it yet)
env_path = Path(__file__).parent.parent.parent / '.env'  # Go up to repo root
if env_path.exists():
    load_dotenv(env_path, override=True)  # Override to ensure latest .env values are used
else:
    # Fallback to backend/.env or current dir
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    # Strip whitespace in case .env has extra spaces
    OPENAI_API_KEY = OPENAI_API_KEY.strip()
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except ImportError:
        logger.warning("OpenAI package not installed. GPT analysis will not be available.")
        openai_client = None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        openai_client = None
else:
    logger.warning("OPENAI_API_KEY not found in environment. GPT analysis will not be available.")
    openai_client = None


@router.get("/news/universe/{universe_name}/today-aggregated")
async def get_today_news_aggregated(universe_name: str):
    """
    Get today's news aggregated by ticker for a universe.
    
    Args:
        universe_name: Name of the universe
        
    Returns:
        Dictionary with tickers as keys and lists of news items as values
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        from urllib.parse import unquote
        decoded_name = unquote(universe_name)
        
        # Get universe
        universe = db_service.db_manager.get_universe_by_name(decoded_name)
        if universe is None:
            # Try similar matching like in get_universe_news
            all_universes = db_service.get_all_universes()
            base_name = decoded_name.split('(')[0].strip()
            
            for u in all_universes:
                universe_name_lower = u['name'].lower()
                decoded_name_lower = decoded_name.lower()
                base_name_lower = base_name.lower()
                universe_base = u['name'].split('(')[0].strip().lower()
                
                if (decoded_name_lower == universe_name_lower or
                    decoded_name_lower in universe_name_lower or
                    universe_name_lower in decoded_name_lower or
                    base_name_lower == universe_base or
                    base_name_lower in universe_name_lower or
                    universe_base in decoded_name_lower):
                    from src.database.models import Universe
                    universe = Universe(
                        id=u['id'],
                        name=u['name'],
                        description=u.get('description'),
                        created_at=None,
                        updated_at=None
                    )
                    break
            
            if universe is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Universe '{decoded_name}' not found"
                )
        
        universe_id = int(universe.id)
        tickers_df = db_service.db_manager.get_universe_tickers(universe_id)
        if tickers_df.empty:
            return {
                "universe_name": universe.name,
                "date": date.today().isoformat(),
                "tickers": {}
            }
        
        tickers = tickers_df['ticker'].tolist()
        
        # Get today's date
        today = date.today()
        
        # Fetch news for all tickers
        news_items = news_service.fetch_universe_news(
            tickers=tickers,
            max_items_per_ticker=50,
            total_max_items=500
        )
        
        # Filter to today's news and aggregate by ticker
        aggregated = defaultdict(list)
        for item in news_items:
            try:
                pub_date = datetime.fromisoformat(item['pub_date'].replace('Z', '+00:00')).date()
                if pub_date == today:
                    aggregated[item['ticker']].append(item)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing date for news item: {e}")
                continue
        
        # Sort news within each ticker by publication date (newest first)
        for ticker in aggregated:
            aggregated[ticker].sort(
                key=lambda x: datetime.fromisoformat(x['pub_date'].replace('Z', '+00:00')),
                reverse=True
            )
        
        return {
            "universe_name": universe.name,
            "date": today.isoformat(),
            "tickers": dict(aggregated)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching today's aggregated news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/universe/{universe_name}/statistics")
async def get_news_statistics(universe_name: str):
    """
    Get aggregate statistics for today's news.
    
    Returns:
        Top/bottom tickers by sentiment, sector trends, time-based changes
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        from urllib.parse import unquote
        decoded_name = unquote(universe_name)
        
        # Get universe
        universe = db_service.db_manager.get_universe_by_name(decoded_name)
        if universe is None:
            all_universes = db_service.get_all_universes()
            base_name = decoded_name.split('(')[0].strip()
            
            for u in all_universes:
                universe_name_lower = u['name'].lower()
                decoded_name_lower = decoded_name.lower()
                base_name_lower = base_name.lower()
                universe_base = u['name'].split('(')[0].strip().lower()
                
                if (decoded_name_lower == universe_name_lower or
                    decoded_name_lower in universe_name_lower or
                    universe_name_lower in decoded_name_lower or
                    base_name_lower == universe_base):
                    from src.database.models import Universe
                    universe = Universe(
                        id=u['id'],
                        name=u['name'],
                        description=u.get('description'),
                        created_at=None,
                        updated_at=None
                    )
                    break
            
            if universe is None:
                raise HTTPException(status_code=404, detail=f"Universe '{decoded_name}' not found")
        
        universe_id = int(universe.id)
        tickers_df = db_service.db_manager.get_universe_tickers(universe_id)
        if tickers_df.empty:
            return {
                "universe_name": universe.name,
                "date": date.today().isoformat(),
                "top_tickers": [],
                "bottom_tickers": [],
                "sector_trends_today": {},
                "sector_trends_week": {},
                "time_based_changes": []
            }
        
        tickers = tickers_df['ticker'].tolist()
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # Get today's news
        today_news = news_service.fetch_universe_news(
            tickers=tickers,
            max_items_per_ticker=50,
            total_max_items=500
        )
        
        # Filter to today and this week
        today_items = []
        week_items = []
        
        for item in today_news:
            try:
                pub_date = datetime.fromisoformat(item['pub_date'].replace('Z', '+00:00')).date()
                if pub_date == today:
                    today_items.append(item)
                if pub_date >= week_ago:
                    week_items.append(item)
            except (ValueError, KeyError):
                continue
        
        # Calculate ticker sentiment scores for today
        ticker_sentiments_today = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "total": 0, "avg_score": 0.0})
        
        for item in today_items:
            ticker = item['ticker']
            sentiment = item.get('sentiment', {})
            label = sentiment.get('label', 'neutral')
            score = sentiment.get('score', 0.5)
            
            ticker_sentiments_today[ticker][label] += 1
            ticker_sentiments_today[ticker]["total"] += 1
            ticker_sentiments_today[ticker]["avg_score"] += score
        
        # Calculate average scores
        ticker_scores = []
        for ticker, data in ticker_sentiments_today.items():
            if data["total"] > 0:
                avg_score = data["avg_score"] / data["total"]
                # Normalize: positive=1, neutral=0.5, negative=0
                normalized_score = avg_score
                ticker_scores.append({
                    "ticker": ticker,
                    "avg_sentiment_score": normalized_score,
                    "positive_count": data["positive"],
                    "negative_count": data["negative"],
                    "neutral_count": data["neutral"],
                    "total_news": data["total"]
                })
        
        # Sort by sentiment score
        ticker_scores.sort(key=lambda x: x["avg_sentiment_score"], reverse=True)
        top_tickers = ticker_scores[:5] if len(ticker_scores) >= 5 else ticker_scores
        bottom_tickers = ticker_scores[-5:] if len(ticker_scores) >= 5 else []
        bottom_tickers.reverse()
        
        # Sector trends (today and week)
        def calculate_trend(items):
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for item in items:
                sentiment = item.get('sentiment', {})
                label = sentiment.get('label', 'neutral')
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
            total = sum(sentiment_counts.values())
            if total > 0:
                return {
                    "positive_percent": (sentiment_counts["positive"] / total) * 100,
                    "negative_percent": (sentiment_counts["negative"] / total) * 100,
                    "neutral_percent": (sentiment_counts["neutral"] / total) * 100,
                    "total_news": total
                }
            return {"positive_percent": 0, "negative_percent": 0, "neutral_percent": 0, "total_news": 0}
        
        sector_trends_today = calculate_trend(today_items)
        sector_trends_week = calculate_trend(week_items)
        
        # Time-based changes (group by hour for today)
        hourly_changes = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        for item in today_items:
            try:
                pub_datetime = datetime.fromisoformat(item['pub_date'].replace('Z', '+00:00'))
                hour = pub_datetime.hour
                sentiment = item.get('sentiment', {})
                label = sentiment.get('label', 'neutral')
                if label in hourly_changes[hour]:
                    hourly_changes[hour][label] += 1
            except (ValueError, KeyError):
                continue
        
        time_based_changes = []
        for hour in sorted(hourly_changes.keys()):
            data = hourly_changes[hour]
            total = sum(data.values())
            time_based_changes.append({
                "hour": hour,
                "positive": data["positive"],
                "negative": data["negative"],
                "neutral": data["neutral"],
                "total": total
            })
        
        return {
            "universe_name": universe.name,
            "date": today.isoformat(),
            "top_tickers": top_tickers,
            "bottom_tickers": bottom_tickers,
            "sector_trends_today": sector_trends_today,
            "sector_trends_week": sector_trends_week,
            "time_based_changes": time_based_changes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
            
            # Extract base name (e.g., "MovieCore-8" from "MovieCore-8 (MC-8)")
            base_name = decoded_name.split('(')[0].strip()
            
            # Try to find by partial match - check if names overlap in either direction
            for u in all_universes:
                universe_name_lower = u['name'].lower()
                decoded_name_lower = decoded_name.lower()
                base_name_lower = base_name.lower()
                
                # Check various matching conditions:
                # 1. Exact match (case-insensitive)
                # 2. One name contains the other
                # 3. Base name matches (e.g., "MovieCore-8" matches "MovieCore-8 (MC-8)")
                # 4. Universe name base matches (extract base from universe name too)
                universe_base = u['name'].split('(')[0].strip().lower()
                
                if (decoded_name_lower == universe_name_lower or
                    decoded_name_lower in universe_name_lower or
                    universe_name_lower in decoded_name_lower or
                    base_name_lower == universe_base or
                    base_name_lower in universe_name_lower or
                    universe_base in decoded_name_lower):
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


@router.post("/news/analyze")
async def analyze_news_with_gpt(request: Dict):
    """
    Analyze a news article with GPT-4o-mini, providing trading insights.
    
    Args:
        request: Dictionary with 'ticker', 'title', 'summary', 'sentiment', 'sentiment_score', 'price_data', 'pub_date'
        
    Returns:
        Analysis from GPT-4o-mini
    """
    # Re-check the API key in case environment changed
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        current_key = current_key.strip()
    
    # Update the key if it changed
    global OPENAI_API_KEY, openai_client
    if current_key and current_key != OPENAI_API_KEY:
        OPENAI_API_KEY = current_key
        try:
            from openai import OpenAI
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client re-initialized with new key")
        except Exception as e:
            logger.error(f"Failed to re-initialize OpenAI client: {e}")
    
    if not openai_client:
        logger.error(f"OpenAI client not available. Key present: {OPENAI_API_KEY is not None}, Key length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}")
        raise HTTPException(
            status_code=503,
            detail="OpenAI API not configured. Please set OPENAI_API_KEY in environment."
        )
    
    # Verify API key is still valid before making the request
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        logger.error("OPENAI_API_KEY is empty or whitespace only")
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is empty or not configured."
        )
    
    try:
        ticker = request.get('ticker', 'UNKNOWN')
        title = request.get('title', '')
        summary = request.get('summary', '')
        sentiment = request.get('sentiment', {})
        price_data = request.get('price_data', {})
        pub_date = request.get('pub_date', '')
        
        # Build prompt
        sentiment_label = sentiment.get('label_display', sentiment.get('label', 'Unknown'))
        sentiment_score = sentiment.get('score', 0)
        
        price_info = ""
        if price_data:
            current_price = price_data.get('price', 'N/A')
            prev_close = price_data.get('previous_close', 'N/A')
            change = price_data.get('daily_change', 'N/A')
            change_pct = price_data.get('daily_change_percent', 'N/A')
            price_info = f"""
Current Price: ${current_price}
Previous Close: ${prev_close}
Daily Change: ${change} ({change_pct}%)
"""
        
        prompt = f"""You are a quantitative finance analyst specializing in alternative data and sentiment analysis for stock trading.

Analyze the following news article and provide insights in exactly 3 categories:

Stock Ticker: {ticker}
Publication Date: {pub_date}
Sentiment Analysis: {sentiment_label} (confidence: {sentiment_score:.2%})

Price Data:
{price_info}

News Article:
Title: {title}
Summary: {summary}

Provide your analysis in EXACTLY this format (use these exact section headers):

## Brief Summary
[Provide a concise 2-3 sentence summary of the news and its key implications]

## Price Impact
[VERY CONCISE: 1-2 sentences maximum. Briefly state how this news has influenced or might influence the stock price, including immediate impact (if any) and potential future movements. Be specific about direction if possible.]

## Sentiment Analysis
[VERY CONCISE: 1-2 sentences maximum. Briefly explain the overall sentiment from different perspectives and why the sentiment is {sentiment_label}. Focus on the key factors.]

Keep Brief Summary detailed but keep Price Impact and Sentiment Analysis extremely concise (1-2 sentences each). Format using markdown.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a quantitative finance analyst specializing in alternative data and sentiment analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "ticker": ticker,
            "analysis": analysis,
            "model": "gpt-4o-mini",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error analyzing news with GPT: {e}", exc_info=True)
        
        # Provide more helpful error messages
        if "401" in error_msg or "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            key_preview = OPENAI_API_KEY[:20] + "..." if OPENAI_API_KEY and len(OPENAI_API_KEY) > 20 else "NOT SET"
            logger.error(f"OpenAI API key appears to be invalid. Key length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}, Key preview: {key_preview}")
            logger.error(f"Key starts with: {OPENAI_API_KEY[:10] if OPENAI_API_KEY and len(OPENAI_API_KEY) > 10 else 'N/A'}")
            
            # Check if key might have quotes
            if OPENAI_API_KEY and (OPENAI_API_KEY.startswith('"') or OPENAI_API_KEY.startswith("'")):
                logger.error("WARNING: API key appears to have quotes at the start!")
            
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API authentication failed. The API key in your .env file appears to be invalid or expired. "
                       "Please verify your OPENAI_API_KEY at https://platform.openai.com/account/api-keys. "
                       "Make sure it starts with 'sk-' or 'sk-proj-' and doesn't have extra quotes or whitespace. "
                       "If you recently updated the key, restart the backend server."
            )
        
        raise HTTPException(status_code=500, detail=f"Error analyzing news: {error_msg}")


@router.get("/news/universe/{universe_name}/statistics")
async def get_news_statistics(universe_name: str):
    """
    Get aggregate statistics for today's news.
    
    Returns:
        Top/bottom tickers by sentiment, sector trends, time-based changes
    """
    try:
        if not db_service.ensure_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        from urllib.parse import unquote
        decoded_name = unquote(universe_name)
        
        # Get universe
        universe = db_service.db_manager.get_universe_by_name(decoded_name)
        if universe is None:
            all_universes = db_service.get_all_universes()
            base_name = decoded_name.split('(')[0].strip()
            
            for u in all_universes:
                universe_name_lower = u['name'].lower()
                decoded_name_lower = decoded_name.lower()
                base_name_lower = base_name.lower()
                universe_base = u['name'].split('(')[0].strip().lower()
                
                if (decoded_name_lower == universe_name_lower or
                    decoded_name_lower in universe_name_lower or
                    universe_name_lower in decoded_name_lower or
                    base_name_lower == universe_base):
                    from src.database.models import Universe
                    universe = Universe(
                        id=u['id'],
                        name=u['name'],
                        description=u.get('description'),
                        created_at=None,
                        updated_at=None
                    )
                    break
            
            if universe is None:
                raise HTTPException(status_code=404, detail=f"Universe '{decoded_name}' not found")
        
        universe_id = int(universe.id)
        tickers_df = db_service.db_manager.get_universe_tickers(universe_id)
        if tickers_df.empty:
            return {
                "universe_name": universe.name,
                "date": date.today().isoformat(),
                "top_tickers": [],
                "bottom_tickers": [],
                "sector_trends_today": {},
                "sector_trends_week": {},
                "time_based_changes": []
            }
        
        tickers = tickers_df['ticker'].tolist()
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # Get today's news
        today_news = news_service.fetch_universe_news(
            tickers=tickers,
            max_items_per_ticker=50,
            total_max_items=500
        )
        
        # Filter to today and this week
        today_items = []
        week_items = []
        
        for item in today_news:
            try:
                pub_date = datetime.fromisoformat(item['pub_date'].replace('Z', '+00:00')).date()
                if pub_date == today:
                    today_items.append(item)
                if pub_date >= week_ago:
                    week_items.append(item)
            except (ValueError, KeyError):
                continue
        
        # Calculate ticker sentiment scores for today
        ticker_sentiments_today = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "total": 0, "avg_score": 0.0})
        
        for item in today_items:
            ticker = item['ticker']
            sentiment = item.get('sentiment', {})
            label = sentiment.get('label', 'neutral')
            score = sentiment.get('score', 0.5)
            
            ticker_sentiments_today[ticker][label] += 1
            ticker_sentiments_today[ticker]["total"] += 1
            ticker_sentiments_today[ticker]["avg_score"] += score
        
        # Calculate average scores
        ticker_scores = []
        for ticker, data in ticker_sentiments_today.items():
            if data["total"] > 0:
                avg_score = data["avg_score"] / data["total"]
                # Normalize: positive=1, neutral=0.5, negative=0
                normalized_score = avg_score
                ticker_scores.append({
                    "ticker": ticker,
                    "avg_sentiment_score": normalized_score,
                    "positive_count": data["positive"],
                    "negative_count": data["negative"],
                    "neutral_count": data["neutral"],
                    "total_news": data["total"]
                })
        
        # Sort by sentiment score
        ticker_scores.sort(key=lambda x: x["avg_sentiment_score"], reverse=True)
        top_tickers = ticker_scores[:5] if len(ticker_scores) >= 5 else ticker_scores
        bottom_tickers = ticker_scores[-5:] if len(ticker_scores) >= 5 else []
        bottom_tickers.reverse()
        
        # Sector trends (today and week)
        def calculate_trend(items):
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for item in items:
                sentiment = item.get('sentiment', {})
                label = sentiment.get('label', 'neutral')
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
            total = sum(sentiment_counts.values())
            if total > 0:
                return {
                    "positive_percent": (sentiment_counts["positive"] / total) * 100,
                    "negative_percent": (sentiment_counts["negative"] / total) * 100,
                    "neutral_percent": (sentiment_counts["neutral"] / total) * 100,
                    "total_news": total
                }
            return {"positive_percent": 0, "negative_percent": 0, "neutral_percent": 0, "total_news": 0}
        
        sector_trends_today = calculate_trend(today_items)
        sector_trends_week = calculate_trend(week_items)
        
        # Time-based changes (group by hour for today)
        hourly_changes = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        for item in today_items:
            try:
                pub_datetime = datetime.fromisoformat(item['pub_date'].replace('Z', '+00:00'))
                hour = pub_datetime.hour
                sentiment = item.get('sentiment', {})
                label = sentiment.get('label', 'neutral')
                if label in hourly_changes[hour]:
                    hourly_changes[hour][label] += 1
            except (ValueError, KeyError):
                continue
        
        time_based_changes = []
        for hour in sorted(hourly_changes.keys()):
            data = hourly_changes[hour]
            total = sum(data.values())
            time_based_changes.append({
                "hour": hour,
                "positive": data["positive"],
                "negative": data["negative"],
                "neutral": data["neutral"],
                "total": total
            })
        
        return {
            "universe_name": universe.name,
            "date": today.isoformat(),
            "top_tickers": top_tickers,
            "bottom_tickers": bottom_tickers,
            "sector_trends_today": sector_trends_today,
            "sector_trends_week": sector_trends_week,
            "time_based_changes": time_based_changes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

