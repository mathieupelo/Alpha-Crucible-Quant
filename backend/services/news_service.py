"""
News Service

Service for fetching financial news from Yahoo Finance and analyzing sentiment using FinBERT.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import yfinance as yf
import json
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Lazy import transformers to avoid breaking if not installed
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers and torch not available. Sentiment analysis will use fallback method.")

# FinBERT model configuration
# Using yiyanghkust/finbert-tone for sentiment classification
# Alternative models: ProsusAI/finbert, eliseby/FINBERT-Tone-Evaluation
FINBERT_MODEL = "yiyanghkust/finbert-tone"
MAX_NEWS_ITEMS = 10


class NewsService:
    """Service for fetching and analyzing financial news."""
    
    def __init__(self):
        """Initialize news service with FinBERT model."""
        self.tokenizer = None
        self.model = None
        self._model_loaded = False
        
    def _load_model(self):
        """Lazy load FinBERT model."""
        if self._model_loaded:
            return
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available, using simple sentiment fallback")
            self._model_loaded = False
            return
        
        try:
            logger.info("Loading FinBERT model for sentiment analysis...")
            self.tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL)
            
            # Set to evaluation mode
            self.model.eval()
            
            # Use GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            self._model_loaded = True
            logger.info(f"FinBERT model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            logger.warning("Falling back to simple sentiment analysis")
            self._model_loaded = False
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of news text using FinBERT or fallback method.
        
        Args:
            text: News article text
            
        Returns:
            Dictionary with sentiment label and score
        """
        if not TRANSFORMERS_AVAILABLE:
            # Simple keyword-based fallback sentiment
            return self._simple_sentiment_analysis(text)
        
        if not self._model_loaded:
            self._load_model()
        
        # If model loading failed, use simple sentiment
        if not self._model_loaded or self.model is None:
            return self._simple_sentiment_analysis(text)
        
        try:
            # Tokenize and encode
            inputs = self.tokenizer(
                text[:512],  # Limit to 512 tokens
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # FinBERT labels: 0=positive, 1=negative, 2=neutral
            scores = predictions[0].cpu().numpy()
            labels = ["positive", "negative", "neutral"]
            
            # Get highest probability label
            label_idx = scores.argmax()
            label = labels[label_idx]
            score = float(scores[label_idx])
            
            # Format label for display
            label_display = label.capitalize()
            
            return {
                "label": label,
                "score": score,
                "label_display": label_display,
                "scores": {
                    "positive": float(scores[0]),
                    "negative": float(scores[1]),
                    "neutral": float(scores[2])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based sentiment analysis fallback.
        
        Args:
            text: News article text
            
        Returns:
            Dictionary with sentiment label and score
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_keywords = ['up', 'gain', 'rise', 'profit', 'growth', 'strong', 'beat', 'exceed', 'positive', 'bullish', 'surge', 'rally']
        # Negative keywords
        negative_keywords = ['down', 'loss', 'fall', 'decline', 'weak', 'miss', 'drop', 'negative', 'bearish', 'crash', 'plunge', 'slump']
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        total = positive_count + negative_count
        
        if total == 0:
            label = "neutral"
            score = 0.5
        elif positive_count > negative_count:
            label = "positive"
            score = 0.6 + (positive_count / max(total, 5)) * 0.3
        elif negative_count > positive_count:
            label = "negative"
            score = 0.6 + (negative_count / max(total, 5)) * 0.3
        else:
            label = "neutral"
            score = 0.5
        
        return {
            "label": label,
            "score": min(max(score, 0.0), 1.0),
            "label_display": label.capitalize()
        }
    
    def fetch_ticker_news(self, ticker: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch news for a specific ticker from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol
            max_items: Maximum number of news items to fetch
            
        Returns:
            List of news items with sentiment analysis
        """
        try:
            logger.info(f"Fetching news for ticker: {ticker}")
            
            # Create yfinance ticker object
            stock = yf.Ticker(ticker)
            
            # Fetch news
            news_list = stock.news
            
            if not news_list:
                logger.info(f"No news found for {ticker}")
                return []
            
            # Process and analyze news
            processed_news = []
            for news_item in news_list[:max_items]:
                try:
                    # Yahoo Finance news format has changed - data may be in 'content' field as JSON string
                    # Or direct fields like 'title', 'publisher', etc.
                    title = ''
                    summary = ''
                    publisher = 'Unknown'
                    link = ''
                    pub_date = None
                    
                    # Check if data is in 'content' field (new yfinance format)
                    if 'content' in news_item and news_item['content']:
                        try:
                            content = news_item['content']
                            # Handle both string (JSON) and dict content
                            if isinstance(content, str):
                                content = json.loads(content)
                            
                            # Extract fields from content dict
                            title = content.get('title', '') or ''
                            
                            # Description might be HTML, extract text
                            description = content.get('description', '') or content.get('summary', '') or ''
                            # Strip HTML tags if present
                            if description and '<' in description:
                                import re
                                description = re.sub(r'<[^>]+>', '', description)
                            summary = description
                            
                            # Publisher - check multiple locations
                            pub_info = content.get('publisher') or news_item.get('publisher')
                            if isinstance(pub_info, dict):
                                publisher = pub_info.get('name', 'Unknown') or 'Unknown'
                            elif pub_info:
                                publisher = str(pub_info)
                            else:
                                publisher = 'Unknown'
                            
                            # Link/URL - try multiple fields
                            # canonicalUrl is usually the main article URL
                            url_obj = content.get('canonicalUrl') or content.get('url') or content.get('previewUrl') or content.get('clickThroughUrl') or content.get('link') or news_item.get('link')
                            if isinstance(url_obj, dict):
                                link = url_obj.get('url', '') or ''
                            elif url_obj:
                                link = str(url_obj)
                            else:
                                link = ''
                            
                            # Publisher - check provider field (has displayName)
                            provider = content.get('provider')
                            if provider:
                                if isinstance(provider, dict):
                                    # Provider has 'displayName' field
                                    pub_name = provider.get('displayName') or provider.get('name')
                                    if pub_name:
                                        publisher = pub_name
                                elif isinstance(provider, str):
                                    publisher = provider
                            
                            # Timestamp - try multiple fields
                            pub_date = content.get('providerPublishTime') or content.get('pubDate') or content.get('publishedAt') or content.get('publishTime')
                            
                        except (json.JSONDecodeError, TypeError, AttributeError, KeyError) as e:
                            logger.warning(f"Error parsing content field for {ticker}: {e}")
                            # Fall back to direct fields
                            title = news_item.get('title', '')
                            summary = news_item.get('summary', '') or news_item.get('description', '')
                            publisher = news_item.get('publisher', 'Unknown')
                            link = news_item.get('link', '') or news_item.get('url', '')
                            pub_date = news_item.get('providerPublishTime') or news_item.get('pubDate')
                    else:
                        # Old format - direct fields
                        title = news_item.get('title', '') or ''
                        summary = news_item.get('summary', '') or news_item.get('description', '') or ''
                        publisher = news_item.get('publisher', 'Unknown') or 'Unknown'
                        link = news_item.get('link', '') or news_item.get('url', '') or ''
                        pub_date = news_item.get('providerPublishTime') or news_item.get('pubDate') or news_item.get('publishedAt')
                    
                    # Ensure we have at least a title or summary
                    if not title and not summary:
                        # Try to extract from other fields
                        title = news_item.get('headline', '') or content.get('headline', '') or str(news_item.get('id', 'News Article'))
                    
                    # Clean up title - remove any remaining "Unknown" or empty strings
                    if not title or title.strip() == '' or title.strip().lower() == 'unknown':
                        if summary:
                            # Use first part of summary as title
                            title = summary.split('.')[0].strip()[:100] or 'News Article'
                        else:
                            title = 'News Article'
                    
                    # Clean up summary - ensure it's not just "Unknown"
                    if summary and (summary.strip().lower() == 'unknown' or len(summary.strip()) < 5):
                        summary = ''  # Don't show meaningless summary
                    
                    # Convert timestamp to datetime
                    if pub_date:
                        try:
                            # Handle both Unix timestamp (int/float) and ISO string
                            if isinstance(pub_date, (int, float)):
                                pub_date = datetime.fromtimestamp(pub_date)
                            else:
                                # Try parsing ISO format string
                                pub_date = datetime.fromisoformat(str(pub_date).replace('Z', '+00:00'))
                        except (ValueError, TypeError, OSError) as e:
                            logger.warning(f"Error parsing date for {ticker}: {e}, using current time")
                            pub_date = datetime.now()
                    else:
                        pub_date = datetime.now()
                    
                    # Combine title and summary if available for sentiment analysis
                    text_for_sentiment = f"{title}. {summary}".strip()
                    
                    # Skip if no meaningful content
                    if not text_for_sentiment or len(text_for_sentiment) < 10:
                        logger.warning(f"Skipping news item for {ticker} - no meaningful content")
                        continue
                    
                    # Analyze sentiment
                    sentiment = self.analyze_sentiment(text_for_sentiment)
                    
                    processed_item = {
                        "ticker": ticker,
                        "title": title,
                        "summary": summary,
                        "publisher": publisher,
                        "link": link,
                        "pub_date": pub_date.isoformat(),
                        "sentiment": sentiment,
                        "raw_data": news_item
                    }
                    
                    processed_news.append(processed_item)
                    
                except Exception as e:
                    logger.warning(f"Error processing news item for {ticker}: {e}")
                    continue
            
            logger.info(f"Fetched {len(processed_news)} news items for {ticker}")
            return processed_news
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []
    
    def fetch_universe_news(
        self, 
        tickers: List[str], 
        max_items_per_ticker: int = 5,
        total_max_items: int = MAX_NEWS_ITEMS
    ) -> List[Dict[str, Any]]:
        """
        Fetch and aggregate news for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            max_items_per_ticker: Maximum news items per ticker
            total_max_items: Maximum total news items to return
            
        Returns:
            List of aggregated news items sorted by date (newest first)
        """
        all_news = []
        
        for ticker in tickers:
            try:
                ticker_news = self.fetch_ticker_news(ticker, max_items_per_ticker)
                all_news.extend(ticker_news)
            except Exception as e:
                logger.warning(f"Error fetching news for {ticker}: {e}")
                continue
        
        # Sort by publication date (newest first)
        all_news.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        
        # Return top N items
        return all_news[:total_max_items]


# Global instance
news_service = NewsService()

