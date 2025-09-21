"""
YouTube Sentiment signal implementation.

Analyzes sentiment from YouTube comments on video game trailers for gaming companies.
Uses point-in-time data - only trailers released on/before the target date and comments
posted on/before the target date.
"""

import json
import logging
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import numpy as np
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from textblob import TextBlob

from .base import SignalBase
import sys
from pathlib import Path
import os
import importlib.util

# Get the absolute path to the src directory
src_path = Path(__file__).parent.parent
copper_service_path = src_path / "services" / "copper_service.py"

# Import copper service using absolute path
if copper_service_path.exists():
    spec = importlib.util.spec_from_file_location("copper_service", copper_service_path)
    copper_service_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copper_service_module)
    CopperService = copper_service_module.CopperService
else:
    # Fallback: try normal import with path manipulation
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    try:
        from services.copper_service import CopperService
    except ImportError:
        raise ImportError(f"Could not find copper_service module at {copper_service_path}")

logger = logging.getLogger(__name__)


class SentimentSignalYT(SignalBase):
    """YouTube sentiment signal implementation for gaming companies."""
    
    def __init__(self, seed: int = None, price_fetcher=None, youtube_api_key: str = None):
        """
        Initialize YouTube Sentiment signal.
        
        Args:
            seed: Random seed for reproducible results (optional)
            price_fetcher: Optional price fetcher for data retrieval
            youtube_api_key: YouTube Data API key (optional, will try env var)
        """
        super().__init__(
            signal_id="SENTIMENT_YT",
            name="YouTube Sentiment Signal",
            parameters={"seed": seed},
            price_fetcher=price_fetcher
        )
        self.seed = seed
        self.youtube_api_key = youtube_api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube_service = None
        self.copper_service = None
        
        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)
    
    def calculate(self, price_data: Optional[pd.DataFrame], ticker: str, target_date: date) -> float:
        """
        Calculate YouTube sentiment signal value for a ticker on a specific date.
        
        Args:
            price_data: DataFrame with OHLCV data (ignored for sentiment)
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            
        Returns:
            Sentiment score between -1 and 1, or NaN if no data available
        """

        print(f"Calculating YouTube sentiment for {ticker} on {target_date}")
        try:
            # Load trailer mapping
            trailer_map = self._load_trailer_map()
            if ticker not in trailer_map:
                logger.debug(f"No trailers found for ticker {ticker}")
                return np.nan
            
            # Filter trailers by release date (point-in-time)
            eligible_trailers = self._eligible_trailers(trailer_map[ticker], target_date)
            if not eligible_trailers:
                logger.debug(f"No eligible trailers for {ticker} on {target_date} (all games may have been released)")
                return np.nan
            
            # Initialize copper service for database access
            if self.copper_service is None:
                self.copper_service = CopperService()
                if not self.copper_service.connect():
                    logger.error("Failed to connect to copper database")
                    return np.nan
            
            # Get video IDs for all eligible trailers
            video_ids = []
            for trailer in eligible_trailers:
                video_id = self._parse_video_id(trailer['trailer_url'])
                if video_id:
                    video_ids.append(video_id)
                else:
                    logger.warning(f"Could not parse video ID from {trailer['trailer_url']}")
            
            if not video_ids:
                logger.debug(f"No valid video IDs found for {ticker}")
                return np.nan
            
            # Fetch comments from database with point-in-time filtering
            comments_df = self.copper_service.get_comments_by_video_ids_and_date(
                video_ids, target_date
            )
            
            if comments_df.empty:
                logger.debug(f"No comments found for {ticker} on {target_date}")
                return np.nan
            
            # Convert DataFrame to list of comment dictionaries for scoring
            all_comments = []
            for _, row in comments_df.iterrows():
                comment_dict = {
                    'text': row['text_content'],
                    'published_at': row['published_at'],
                    'author': row['author_display_name'],
                    'like_count': row['like_count']
                }
                all_comments.append(comment_dict)
            
            videos_used = len(video_ids)
            
            # Score comments and aggregate
            comment_scores = self._score_comments(all_comments)
            if not comment_scores:
                return np.nan
            
            # Calculate mean sentiment
            mean_sentiment = np.mean(comment_scores)
            
            logger.debug(f"YT sentiment for {ticker} on {target_date}: {mean_sentiment:.3f} "
                        f"(videos: {videos_used}, comments: {len(comment_scores)})")
            print(f"YT sentiment for {ticker} on {target_date}: {mean_sentiment:.3f} "
                        f"(videos: {videos_used}, comments: {len(comment_scores)})")
            return float(mean_sentiment)
            
        except Exception as e:
            logger.error(f"Error calculating YouTube sentiment for {ticker} on {target_date}: {e}")
            return np.nan
    
    def get_min_lookback_period(self) -> int:
        """
        Get the minimum number of days of price data needed for calculation.
        
        Returns:
            Minimum lookback period in days (0 for sentiment signal)
        """
        return 0
    
    def get_max_lookback_period(self) -> int:
        """
        Get the maximum number of days of price data needed for calculation.
        
        Returns:
            Maximum lookback period in days (0 for sentiment signal)
        """
        return 0
    
    def get_required_price_data(self, target_date: date) -> Tuple[date, date]:
        """
        Get the required price data date range for signal calculation.
        
        For SENTIMENT signal, this raises NotImplementedError since no price data is needed.
        
        Args:
            target_date: Date to calculate signal for
            
        Raises:
            NotImplementedError: SENTIMENT signal doesn't need price data
        """
        raise NotImplementedError("SENTIMENT_YT signal doesn't require price data")
    
    def validate_price_data(self, price_data: Optional[pd.DataFrame], target_date: date) -> bool:
        """
        Validate price data - always returns True since sentiment signals don't use price data.
        
        Args:
            price_data: DataFrame with price data (ignored)
            target_date: Date to validate (ignored)
            
        Returns:
            Always True since sentiment signals don't require price data
        """
        return True
    
    # Helper methods
    
    def _load_trailer_map(self, path: str = "data/trailer_map.json") -> Dict[str, List[Dict[str, str]]]:
        """
        Load trailer mapping from JSON file.
        
        Args:
            path: Path to trailer mapping JSON file
            
        Returns:
            Dictionary mapping tickers to lists of trailer info
        """
        try:
            # If path is relative, make it relative to project root
            if not os.path.isabs(path):
                # Get the project root (assuming this file is in src/signals/)
                project_root = Path(__file__).parent.parent.parent
                path = str(project_root / path)
            
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Trailer map file not found: {path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in trailer map file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading trailer map: {e}")
            return {}
    
    def _eligible_trailers(self, trailers: List[Dict[str, str]], asof_date: date) -> List[Dict[str, str]]:
        """
        Filter trailers to only those released on or before the asof_date AND 
        where the game hasn't been released yet (with 7-day buffer).
        
        Args:
            trailers: List of trailer dictionaries
            asof_date: Date to filter by
            
        Returns:
            List of eligible trailers
        """
        eligible = []
        for trailer in trailers:
            try:
                # Check trailer release date (must be on or before asof_date)
                release_date = datetime.strptime(trailer['release_date'], '%Y-%m-%d').date()
                if release_date > asof_date:
                    continue
                
                # Check game release date (must be after asof_date + 7 days)
                if 'game_release_date' not in trailer:
                    logger.warning(f"Missing game_release_date in trailer {trailer['game']}")
                    continue
                
                game_release_date = datetime.strptime(trailer['game_release_date'], '%Y-%m-%d').date()
                buffer_date = asof_date + timedelta(days=7)
                
                # Only include trailers for games that haven't been released yet (with 7-day buffer)
                if game_release_date > buffer_date:
                    eligible.append(trailer)
                    logger.debug(f"Eligible trailer: {trailer['game']} (game releases {game_release_date}, buffer until {buffer_date})")
                else:
                    logger.debug(f"Excluded trailer: {trailer['game']} (game released {game_release_date}, within buffer of {buffer_date})")
                    
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid date in trailer {trailer}: {e}")
                continue
        return eligible
    
    def _get_youtube_service(self):
        """
        Initialize YouTube Data API service.
        
        Returns:
            YouTube service object or None if API key not available
        """
        if not self.youtube_api_key:
            logger.warning("YouTube API key not provided")
            return None
        
        try:
            return build('youtube', 'v3', developerKey=self.youtube_api_key)
        except Exception as e:
            logger.error(f"Error initializing YouTube service: {e}")
            return None
    
    def _parse_video_id(self, url: str) -> Optional[str]:
        """
        Parse YouTube video ID from various URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if not found
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/shorts/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    
    def _score_comments(self, comments: List[Dict[str, Any]]) -> List[float]:
        """
        Score comments using sentiment analysis.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            List of sentiment scores between -1 and 1
        """
        scores = []
        
        for comment in comments:
            try:
                text = comment['text']
                # Clean text (remove HTML entities, extra whitespace)
                text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                
                if not text:
                    continue
                
                # Use TextBlob for sentiment analysis
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                # TextBlob returns -1 to 1, which is what we want
                scores.append(polarity)
                
            except Exception as e:
                logger.debug(f"Error scoring comment: {e}")
                continue
        
        return scores
    
    def _get_mock_sentiment(self, ticker: str, target_date: date, num_trailers: int) -> float:
        """
        Generate mock sentiment for testing when database is not available.
        
        Args:
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            num_trailers: Number of eligible trailers
            
        Returns:
            Mock sentiment score between -1 and 1
        """
        # Use ticker and date to create deterministic mock sentiment
        ticker_hash = hash(ticker) % 1000
        date_hash = hash(str(target_date)) % 1000
        combined_seed = (ticker_hash + date_hash) % 1000
        
        # Generate mock sentiment based on ticker and date
        base_sentiment = (combined_seed - 500) / 500.0  # Range: -1 to 1
        
        # Adjust based on number of trailers (more trailers = more data = more reliable)
        trailer_factor = min(1.0, num_trailers / 2.0)  # Cap at 1.0 for 2+ trailers
        final_sentiment = base_sentiment * trailer_factor
        
        # Add some noise to make it more realistic
        noise = (hash(str(target_date) + ticker) % 200 - 100) / 1000.0
        final_sentiment += noise
        
        # Clamp to [-1, 1] range
        final_sentiment = max(-1.0, min(1.0, final_sentiment))
        
        logger.debug(f"Mock sentiment for {ticker} on {target_date}: {final_sentiment:.3f} "
                    f"(trailers: {num_trailers})")
        
        return float(final_sentiment)
