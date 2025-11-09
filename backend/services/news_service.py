"""
News Service

Service for fetching financial news from ORE database (copper.yfinance_news) with sentiment scores.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import warnings
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# Load .env file to ensure environment variables are available
env_path = Path(__file__).parent.parent.parent / '.env'  # Go up to repo root
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    # Fallback to backend/.env or current dir
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        load_dotenv(override=True)

logger = logging.getLogger(__name__)

MAX_NEWS_ITEMS = 10


class NewsService:
    """Service for fetching financial news from ORE database."""
    
    def __init__(self):
        """Initialize news service with ORE database connection."""
        self._ore_conn = None
        
    def _get_ore_connection(self):
        """Get connection to ORE database (lazy connection)."""
        if self._ore_conn is None or (hasattr(self._ore_conn, 'closed') and self._ore_conn.closed):
            try:
                # Try ORE_DATABASE_URL first
                database_url = os.getenv('ORE_DATABASE_URL')
                if not database_url:
                    # Try alternative variable name (used in Airflow)
                    database_url = os.getenv('DATABASE_ORE_URL')
                
                logger.debug(f"ORE_DATABASE_URL present: {database_url is not None}")
                
                if database_url:
                    logger.info("Connecting to ORE database using database URL")
                    self._ore_conn = psycopg2.connect(database_url)
                else:
                    # Fall back to individual connection parameters
                    host = os.getenv('ORE_DB_HOST')
                    port = os.getenv('ORE_DB_PORT', '5432')
                    user = os.getenv('ORE_DB_USER')
                    password = os.getenv('ORE_DB_PASSWORD')
                    database = os.getenv('ORE_DB_NAME')
                    
                    logger.debug(f"ORE_DB_HOST: {host is not None}, ORE_DB_USER: {user is not None}, ORE_DB_NAME: {database is not None}")
                    
                    if not all([host, user, password, database]):
                        missing = []
                        if not host: missing.append('ORE_DB_HOST')
                        if not user: missing.append('ORE_DB_USER')
                        if not password: missing.append('ORE_DB_PASSWORD')
                        if not database: missing.append('ORE_DB_NAME')
                        
                        error_msg = (
                            f"ORE database connection requires either ORE_DATABASE_URL, DATABASE_ORE_URL, or "
                            f"(ORE_DB_HOST, ORE_DB_USER, ORE_DB_PASSWORD, ORE_DB_NAME). "
                            f"Missing variables: {', '.join(missing)}. "
                            f"Please configure ORE database connection in environment variables. "
                            f"Checked .env file at: {env_path}"
                        )
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    logger.info(f"Connecting to ORE database at {host}:{port}")
                    self._ore_conn = psycopg2.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database
                    )
                logger.info("Successfully connected to ORE database")
            except Exception as e:
                logger.error(f"Error connecting to ORE database: {e}", exc_info=True)
                raise
        
        return self._ore_conn
    
    def _format_sentiment_from_db(self, sentiment_label: str, sentiment_score: float, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Format sentiment data from database to match frontend expectations.
        
        Args:
            sentiment_label: Sentiment label from database (positive/negative/neutral)
            sentiment_score: Sentiment score from database
            metadata: Optional metadata JSON from database
            
        Returns:
            Dictionary with sentiment label, score, and display format
        """
        # Normalize label to lowercase
        label = sentiment_label.lower() if sentiment_label else 'neutral'
        
        # Ensure label is one of the expected values
        if label not in ['positive', 'negative', 'neutral']:
            label = 'neutral'
        
        # Format label for display
        label_display = label.capitalize()
        
        # Build sentiment response
        sentiment = {
            "label": label,
            "score": float(sentiment_score) if sentiment_score is not None else 0.5,
            "label_display": label_display
        }
        
        # Add detailed scores from metadata if available
        if metadata:
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            
            if isinstance(metadata, dict):
                # Extract probability scores if available
                positive_prob = metadata.get('positive_prob', 0.0)
                negative_prob = metadata.get('negative_prob', 0.0)
                neutral_prob = metadata.get('neutral_prob', 0.0)
                
                if positive_prob or negative_prob or neutral_prob:
                    sentiment["scores"] = {
                        "positive": float(positive_prob),
                        "negative": float(negative_prob),
                        "neutral": float(neutral_prob)
                    }
        
        return sentiment
    
    def fetch_ticker_news(self, ticker: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch news for a specific ticker from ORE database.
        
        Args:
            ticker: Stock ticker symbol
            max_items: Maximum number of news items to fetch
            
        Returns:
            List of news items with sentiment analysis
        """
        try:
            logger.info(f"Fetching news for ticker: {ticker} from ORE database")
            
            conn = self._get_ore_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Query news with sentiment join
                cursor.execute("""
                    SELECT 
                        n.id,
                        n.ticker,
                        n.title,
                        n.summary,
                        n.publisher,
                        n.link,
                        n.published_date,
                        n.image_url,
                        s.sentiment_label,
                        s.sentiment_score,
                        s.metadata
                    FROM copper.yfinance_news n
                    LEFT JOIN copper.yfinance_news_sentiment s ON n.id = s.yfinance_news_id
                    WHERE n.ticker = %s
                    ORDER BY n.published_date DESC
                    LIMIT %s;
                """, (ticker.upper(), max_items))
                
                rows = cursor.fetchall()
                
                if not rows:
                    logger.info(f"No news found for {ticker} in ORE database")
                    # Debug: Check if there's any news at all for this ticker
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM copper.yfinance_news 
                        WHERE ticker = %s;
                    """, (ticker.upper(),))
                    total_count = cursor.fetchone()[0]
                    logger.debug(f"Total news count for {ticker}: {total_count}")
                    return []
                
                processed_news = []
                for row in rows:
                    try:
                        # Extract sentiment data - handle NULL values
                        sentiment_label = row.get('sentiment_label') or 'neutral'
                        sentiment_score = row.get('sentiment_score')
                        if sentiment_score is None:
                            sentiment_score = 0.5
                        metadata = row.get('metadata')
                        
                        # Format sentiment
                        sentiment = self._format_sentiment_from_db(
                            sentiment_label, 
                            sentiment_score, 
                            metadata
                        )
                        
                        # Format publication date
                        pub_date = row.get('published_date')
                        if pub_date:
                            if isinstance(pub_date, datetime):
                                pub_date_str = pub_date.isoformat()
                            else:
                                pub_date_str = str(pub_date)
                        else:
                            pub_date_str = datetime.now().isoformat()
                        
                        processed_item = {
                            "ticker": str(row.get('ticker', ticker)),
                            "title": str(row.get('title', '')) or 'News Article',
                            "summary": str(row.get('summary', '')) or '',
                            "publisher": str(row.get('publisher', 'Unknown')) or 'Unknown',
                            "link": str(row.get('link', '')) or '',
                            "pub_date": pub_date_str,
                            "sentiment": sentiment,
                            "image_url": str(row.get('image_url', '')) or ''
                        }
                        
                        processed_news.append(processed_item)
                        
                    except Exception as e:
                        logger.warning(f"Error processing news item for {ticker}: {e}", exc_info=True)
                        continue
                
                logger.info(f"Fetched {len(processed_news)} news items for {ticker} from ORE database")
                return processed_news
                
        except Exception as e:
            logger.error(f"Error fetching news for {ticker} from ORE database: {e}", exc_info=True)
            # Return empty list on error to prevent breaking the API
            return []
    
    def fetch_universe_news(
        self, 
        tickers: List[str], 
        max_items_per_ticker: int = 5,
        total_max_items: int = MAX_NEWS_ITEMS,
        days_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch and aggregate news for multiple tickers from ORE database.
        
        Args:
            tickers: List of ticker symbols
            max_items_per_ticker: Maximum news items per ticker (used for per-ticker limit in query)
            total_max_items: Maximum total news items to return
            days_back: Optional number of days to look back (e.g., 7 for last week). If None, returns all news.
            
        Returns:
            List of aggregated news items sorted by date (newest first)
        """
        try:
            if not tickers:
                return []
            
            logger.info(f"Fetching news for {len(tickers)} tickers from ORE database")
            
            conn = self._get_ore_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Convert tickers to uppercase and create placeholders
                ticker_list = [t.upper() for t in tickers]
                placeholders = ','.join(['%s'] * len(ticker_list))
                
                # Build date filter if specified
                date_filter = ""
                date_params = []
                if days_back is not None:
                    from datetime import date, timedelta
                    cutoff_date = date.today() - timedelta(days=days_back)
                    date_filter = "AND n.published_date >= %s"
                    date_params = [cutoff_date]
                
                # Query news with sentiment join for all tickers at once
                # Use a subquery to limit per ticker, then limit overall
                cursor.execute(f"""
                    WITH ranked_news AS (
                        SELECT 
                            n.id,
                            n.ticker,
                            n.title,
                            n.summary,
                            n.publisher,
                            n.link,
                            n.published_date,
                            n.image_url,
                            s.sentiment_label,
                            s.sentiment_score,
                            s.metadata,
                            ROW_NUMBER() OVER (PARTITION BY n.ticker ORDER BY n.published_date DESC) as rn
                        FROM copper.yfinance_news n
                        LEFT JOIN copper.yfinance_news_sentiment s ON n.id = s.yfinance_news_id
                        WHERE n.ticker IN ({placeholders}) {date_filter}
                    )
                    SELECT * FROM ranked_news
                    WHERE rn <= %s
                    ORDER BY published_date DESC
                    LIMIT %s;
                """, ticker_list + date_params + [max_items_per_ticker, total_max_items])
                
                rows = cursor.fetchall()
                
                if not rows:
                    logger.info(f"No news found for tickers {tickers} in ORE database")
                    # Debug: Check if there's any news at all
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM copper.yfinance_news 
                        WHERE ticker IN ({placeholders});
                    """, ticker_list)
                    total_count = cursor.fetchone()[0]
                    logger.debug(f"Total news count for tickers {tickers}: {total_count}")
                    return []
                
                processed_news = []
                for row in rows:
                    try:
                        # Extract sentiment data - handle NULL values
                        sentiment_label = row.get('sentiment_label') or 'neutral'
                        sentiment_score = row.get('sentiment_score')
                        if sentiment_score is None:
                            sentiment_score = 0.5
                        metadata = row.get('metadata')
                        
                        # Format sentiment
                        sentiment = self._format_sentiment_from_db(
                            sentiment_label, 
                            sentiment_score, 
                            metadata
                        )
                        
                        # Format publication date
                        pub_date = row.get('published_date')
                        if pub_date:
                            if isinstance(pub_date, datetime):
                                pub_date_str = pub_date.isoformat()
                            else:
                                pub_date_str = str(pub_date)
                        else:
                            pub_date_str = datetime.now().isoformat()
                        
                        processed_item = {
                            "ticker": str(row.get('ticker', '')),
                            "title": str(row.get('title', '')) or 'News Article',
                            "summary": str(row.get('summary', '')) or '',
                            "publisher": str(row.get('publisher', 'Unknown')) or 'Unknown',
                            "link": str(row.get('link', '')) or '',
                            "pub_date": pub_date_str,
                            "sentiment": sentiment,
                            "image_url": str(row.get('image_url', '')) or ''
                        }
                        
                        processed_news.append(processed_item)
                        
                    except Exception as e:
                        logger.warning(f"Error processing news item: {e}", exc_info=True)
                        continue
                
                # Sort by publication date (newest first) - already sorted by query but ensure it
                processed_news.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
                
                logger.info(f"Fetched {len(processed_news)} news items from ORE database for {len(tickers)} tickers")
                return processed_news
                
        except Exception as e:
            logger.error(f"Error fetching universe news from ORE database: {e}", exc_info=True)
            # Fallback: try fetching per ticker
            logger.info("Falling back to per-ticker fetching")
            all_news = []
            for ticker in tickers:
                try:
                    ticker_news = self.fetch_ticker_news(ticker, max_items_per_ticker)
                    all_news.extend(ticker_news)
                except Exception as e:
                    logger.warning(f"Error fetching news for {ticker}: {e}", exc_info=True)
                    continue
            
            # Sort by publication date (newest first)
            all_news.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
            
            # Return top N items
            return all_news[:total_max_items]


# Global instance
news_service = NewsService()

