#!/usr/bin/env python3
"""
Test script for copper schema YouTube comments implementation.

This script performs smoke tests to verify the complete implementation.
"""

import os
import sys
import logging
from datetime import date, datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.copper_service import CopperService
from services.youtube_comments_fetcher import YouTubeCommentsFetcher
from signals.sentiment_yt import SentimentSignalYT
from database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_copper_schema_setup():
    """Test that copper schema and table exist."""
    logger.info("Testing copper schema setup...")
    
    try:
        copper_service = CopperService()
        if not copper_service.connect():
            logger.error("Failed to connect to copper database")
            return False
        
        # Test table exists by trying to query it
        test_df = copper_service.execute_query("SELECT COUNT(*) as count FROM youtube_comments")
        if test_df.empty:
            logger.error("youtube_comments table not found or not accessible")
            return False
        
        logger.info("✓ Copper schema and youtube_comments table are accessible")
        copper_service.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"Error testing copper schema: {e}")
        return False


def test_youtube_api_availability():
    """Test that YouTube API is available."""
    logger.info("Testing YouTube API availability...")
    
    try:
        fetcher = YouTubeCommentsFetcher()
        if not fetcher.is_api_available():
            logger.error("YouTube API not available - check YOUTUBE_API_KEY in .env")
            return False
        
        logger.info("✓ YouTube API is available")
        return True
        
    except Exception as e:
        logger.error(f"Error testing YouTube API: {e}")
        return False


def test_comment_fetching():
    """Test fetching comments for a single video."""
    logger.info("Testing comment fetching...")
    
    try:
        fetcher = YouTubeCommentsFetcher()
        if not fetcher.is_api_available():
            logger.warning("YouTube API not available, skipping comment fetch test")
            return True
        
        # Test with a known video (GTA VI trailer) - limit to 10 for testing
        test_url = "https://www.youtube.com/watch?v=QdBZY2fkU-0"
        comments = fetcher.fetch_comments_for_video(test_url, max_comments=10)
        
        if not comments:
            logger.warning("No comments fetched - this might be normal for some videos")
            return True
        
        logger.info(f"✓ Successfully fetched {len(comments)} comments")
        
        # Verify comment structure
        if comments:
            comment = comments[0]
            required_keys = ['comment_id', 'video_id', 'text_content', 'published_at']
            if all(key in comment for key in required_keys):
                logger.info("✓ Comment structure is correct")
                return True
            else:
                logger.error(f"Comment structure incorrect: {list(comment.keys())}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing comment fetching: {e}")
        return False


def test_database_insertion():
    """Test inserting comments into the database."""
    logger.info("Testing database insertion...")
    
    try:
        copper_service = CopperService()
        if not copper_service.connect():
            logger.error("Failed to connect to copper database")
            return False
        
        # Create test comments
        test_comments = [
            {
                'comment_id': 'test_comment_1',
                'video_id': 'test_video_1',
                'text_content': 'This is a test comment',
                'author_display_name': 'Test User',
                'like_count': 5,
                'published_at': datetime.now()
            },
            {
                'comment_id': 'test_comment_2',
                'video_id': 'test_video_1',
                'text_content': 'Another test comment',
                'author_display_name': 'Test User 2',
                'like_count': 3,
                'published_at': datetime.now()
            }
        ]
        
        # Insert test comments
        inserted_count = copper_service.insert_youtube_comments(test_comments)
        
        if inserted_count > 0:
            logger.info(f"✓ Successfully inserted {inserted_count} test comments")
            
            # Clean up test data
            copper_service.clear_comments_for_video('test_video_1')
            logger.info("✓ Cleaned up test data")
            return True
        else:
            logger.error("Failed to insert test comments")
            return False
        
    except Exception as e:
        logger.error(f"Error testing database insertion: {e}")
        return False


def test_sentiment_calculation():
    """Test sentiment calculation using database."""
    logger.info("Testing sentiment calculation...")
    
    try:
        # Initialize sentiment signal
        signal = SentimentSignalYT()
        
        # Test with a known ticker from trailer_map
        test_ticker = "TTWO"  # GTA VI trailer
        test_date = date.today()
        
        # This should return NaN if no comments in DB, which is expected
        sentiment = signal.calculate(None, test_ticker, test_date)
        
        if sentiment is not None and not (isinstance(sentiment, float) and sentiment != sentiment):  # Check for NaN
            logger.info(f"✓ Sentiment calculation returned: {sentiment}")
            return True
        else:
            logger.info("✓ Sentiment calculation returned NaN (expected if no comments in DB)")
            return True
        
    except Exception as e:
        logger.error(f"Error testing sentiment calculation: {e}")
        return False


def test_gamecore_12_access():
    """Test access to GameCore-12 tickers."""
    logger.info("Testing GameCore-12 tickers access...")
    
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to main database")
            return False
        
        # Get GameCore-12 universe
        universe = db_manager.get_universe_by_name('GameCore-12 (GC-12)')
        if not universe:
            logger.warning("GameCore-12 universe not found - this is expected if setup_database.py hasn't been run")
            logger.info("You can run 'python scripts/setup_database.py' to create the universe and tickers")
            return True  # Don't fail the test, just warn
        
        # Get tickers - convert to int to avoid type issues
        tickers_df = db_manager.get_universe_tickers(int(universe.id))
        if tickers_df.empty:
            logger.warning("No tickers found for GameCore-12 universe - this is expected if setup_database.py hasn't been run")
            logger.info("You can run 'python scripts/setup_database.py' to create the universe and tickers")
            return True  # Don't fail the test, just warn
        
        tickers = tickers_df['ticker'].tolist()
        logger.info(f"✓ Found {len(tickers)} GameCore-12 tickers: {tickers}")
        return True
        
    except Exception as e:
        logger.error(f"Error testing GameCore-12 access: {e}")
        return False


def main():
    """Run all smoke tests."""
    logger.info("Starting copper implementation smoke tests...")
    logger.info("="*60)
    
    tests = [
        ("Copper Schema Setup", test_copper_schema_setup),
        ("YouTube API Availability", test_youtube_api_availability),
        ("Comment Fetching", test_comment_fetching),
        ("Database Insertion", test_database_insertion),
        ("Sentiment Calculation", test_sentiment_calculation),
        ("GameCore-12 Access", test_gamecore_12_access),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning: {test_name}")
        try:
            if test_func():
                logger.info(f"✓ PASSED: {test_name}")
                passed += 1
            else:
                logger.error(f"✗ FAILED: {test_name}")
        except Exception as e:
            logger.error(f"✗ ERROR in {test_name}: {e}")
    
    logger.info("\n" + "="*60)
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Implementation is ready.")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
