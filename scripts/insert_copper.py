#!/usr/bin/env python3
"""
Bulk insert YouTube comments into copper schema.

Fetches comments for all Gamecore 12 tickers' trailers and inserts them into the database.
This script is idempotent and can be run multiple times safely.
"""

import os
import sys
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.copper_service import CopperService
from services.youtube_comments_fetcher import YouTubeCommentsFetcher
from database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_trailer_map(path: str = "data/trailer_map.json") -> dict:
    """Load trailer mapping from JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Trailer map file not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in trailer map file: {e}")
        return {}


def get_gamecore_12_tickers() -> list:
    """Get the Gamecore 12 tickers from the database."""
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to database")
            return []
        
        # Get GameCore-12 universe
        universe = db_manager.get_universe_by_name('GameCore-12 (GC-12)')
        if not universe:
            logger.error("GameCore-12 universe not found")
            return []
        
        # Get tickers for this universe - convert to int to avoid type issues
        tickers_df = db_manager.get_universe_tickers(int(universe.id))
        if tickers_df.empty:
            logger.error("No tickers found for GameCore-12 universe")
            return []
        
        tickers = tickers_df['ticker'].tolist()
        logger.info(f"Found {len(tickers)} GameCore-12 tickers: {tickers}")
        return tickers
        
    except Exception as e:
        logger.error(f"Error getting GameCore-12 tickers: {e}")
        return []


def get_eligible_trailers(trailers: list, as_of_date: date) -> list:
    """
    Filter trailers to only those released on or before the as_of_date.
    Note: Game release date filtering is applied during sentiment calculation, not here.
    """
    eligible = []
    for trailer in trailers:
        try:
            # Check trailer release date (must be on or before as_of_date)
            release_date = datetime.strptime(trailer['release_date'], '%Y-%m-%d').date()
            if release_date <= as_of_date:
                eligible.append(trailer)
                logger.debug(f"Eligible trailer: {trailer['game']} (trailer released {release_date})")
            else:
                logger.debug(f"Excluded trailer: {trailer['game']} (trailer not yet released on {as_of_date})")
                
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid date in trailer {trailer}: {e}")
            continue
    return eligible


def process_ticker_comments(
    ticker: str, 
    trailers: list, 
    as_of_date: date,
    fetcher: YouTubeCommentsFetcher,
    copper_service: CopperService
) -> dict:
    """
    Process comments for a single ticker.
    
    Returns:
        Dictionary with processing results
    """
    logger.info(f"Processing {ticker}...")
    
    # Filter eligible trailers
    eligible_trailers = get_eligible_trailers(trailers, as_of_date)
    
    if not eligible_trailers:
        logger.info(f"No eligible trailers for {ticker} on {as_of_date}")
        return {
            'ticker': ticker,
            'eligible_trailers': 0,
            'videos_processed': 0,
            'total_comments': 0,
            'comments_inserted': 0
        }
    
    logger.info(f"Found {len(eligible_trailers)} eligible trailers for {ticker}")
    
    total_comments_inserted = 0
    videos_processed = 0
    
    for trailer in eligible_trailers:
        try:
            video_url = trailer['trailer_url']
            game_name = trailer['game']
            
            logger.info(f"Processing {game_name} ({video_url})")
            
            # Fetch comments from YouTube API (up to 10,000 per video)
            comments = fetcher.fetch_comments_for_video(video_url, max_comments=10000)
            
            if not comments:
                logger.info(f"No comments found for {game_name}")
                continue
            
            # Insert comments into database
            comments_inserted = copper_service.insert_youtube_comments(comments)
            total_comments_inserted += comments_inserted
            videos_processed += 1
            
            logger.info(f"Inserted {comments_inserted} comments for {game_name}")
            
        except Exception as e:
            logger.error(f"Error processing trailer {trailer}: {e}")
            continue
    
    return {
        'ticker': ticker,
        'eligible_trailers': len(eligible_trailers),
        'videos_processed': videos_processed,
        'total_comments': total_comments_inserted,
        'comments_inserted': total_comments_inserted
    }


def main():
    """Main function to bulk insert YouTube comments."""
    logger.info("Starting YouTube comments bulk insert...")
    
    # Check if YouTube API is available
    fetcher = YouTubeCommentsFetcher()
    if not fetcher.is_api_available():
        logger.error("YouTube API not available. Please check YOUTUBE_API_KEY in .env file.")
        return False
    
    # Load trailer mapping
    trailer_map = load_trailer_map()
    if not trailer_map:
        logger.error("Failed to load trailer map")
        return False
    
    # Get Gamecore 12 tickers
    gamecore_tickers = get_gamecore_12_tickers()
    if not gamecore_tickers:
        logger.error("Failed to get Gamecore 12 tickers")
        return False
    
    # Use today's date as the as_of_date
    as_of_date = date.today()
    logger.info(f"Processing comments up to {as_of_date}")
    
    # Initialize services
    copper_service = CopperService()
    if not copper_service.connect():
        logger.error("Failed to connect to copper database")
        return False
    
    # Process each ticker
    results = []
    total_videos_processed = 0
    total_comments_inserted = 0
    
    for ticker in gamecore_tickers:
        if ticker not in trailer_map:
            logger.info(f"No trailers found for ticker {ticker}")
            continue
        
        result = process_ticker_comments(
            ticker, 
            trailer_map[ticker], 
            as_of_date,
            fetcher,
            copper_service
        )
        results.append(result)
        
        total_videos_processed += result['videos_processed']
        total_comments_inserted += result['comments_inserted']
    
    # Close database connection
    copper_service.disconnect()
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("BULK INSERT SUMMARY")
    logger.info("="*60)
    logger.info(f"Date processed: {as_of_date}")
    logger.info(f"Tickers processed: {len(results)}")
    logger.info(f"Total videos processed: {total_videos_processed}")
    logger.info(f"Total comments inserted: {total_comments_inserted}")
    logger.info("\nPer-ticker breakdown:")
    
    for result in results:
        logger.info(f"  {result['ticker']}: {result['videos_processed']} videos, "
                   f"{result['comments_inserted']} comments")
    
    logger.info("="*60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
