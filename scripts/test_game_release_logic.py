#!/usr/bin/env python3
"""
Test script for the new game release date logic in sentiment calculation.

This script tests the filtering logic to ensure trailers are only considered
for games that haven't been released yet (with 7-day buffer).
"""

import os
import sys
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from signals.sentiment_yt import SentimentSignalYT

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_trailer_filtering():
    """Test the trailer filtering logic with various scenarios."""
    logger.info("Testing trailer filtering logic...")
    
    # Load trailer map
    try:
        with open('data/trailer_map.json', 'r', encoding='utf-8') as f:
            trailer_map = json.load(f)
    except FileNotFoundError:
        logger.error("Trailer map file not found")
        return False
    
    # Initialize signal
    signal = SentimentSignalYT()
    
    # Test different dates
    test_dates = [
        date(2023, 12, 1),   # Before GTA VI release
        date(2024, 1, 1),    # After GTA VI release
        date(2025, 1, 1),    # Future date
        date(2022, 1, 1),    # Past date
    ]
    
    for test_date in test_dates:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing date: {test_date}")
        logger.info(f"{'='*50}")
        
        # Test TTWO (GTA VI)
        if 'TTWO' in trailer_map:
            eligible_trailers = signal._eligible_trailers(trailer_map['TTWO'], test_date)
            logger.info(f"TTWO eligible trailers for {test_date}: {len(eligible_trailers)}")
            
            for trailer in trailer_map['TTWO']:
                game_release = datetime.strptime(trailer['game_release_date'], '%Y-%m-%d').date()
                buffer_date = test_date + timedelta(days=7)
                is_eligible = game_release > buffer_date
                
                logger.info(f"  {trailer['game']}: game_release={game_release}, buffer_until={buffer_date}, eligible={is_eligible}")
        
        # Test EA (Skate, Battlefield)
        if 'EA' in trailer_map:
            eligible_trailers = signal._eligible_trailers(trailer_map['EA'], test_date)
            logger.info(f"EA eligible trailers for {test_date}: {len(eligible_trailers)}")
            
            for trailer in trailer_map['EA']:
                game_release = datetime.strptime(trailer['game_release_date'], '%Y-%m-%d').date()
                buffer_date = test_date + timedelta(days=7)
                is_eligible = game_release > buffer_date
                
                logger.info(f"  {trailer['game']}: game_release={game_release}, buffer_until={buffer_date}, eligible={is_eligible}")
    
    return True


def test_sentiment_calculation():
    """Test sentiment calculation with the new logic."""
    logger.info("\nTesting sentiment calculation with new logic...")
    
    signal = SentimentSignalYT()
    
    # Test with different dates
    test_cases = [
        ('TTWO', date(2023, 12, 1)),  # Should include GTA VI (releases 2025-12-31)
        ('TTWO', date(2024, 1, 1)),   # Should still include GTA VI
        ('EA', date(2025, 1, 1)),     # Should include both Skate and Battlefield
        ('MSFT', date(2023, 1, 1)),   # Should exclude Halo Infinite and Starfield (already released)
    ]
    
    for ticker, test_date in test_cases:
        logger.info(f"\nTesting {ticker} on {test_date}:")
        try:
            sentiment = signal.calculate(None, ticker, test_date)
            logger.info(f"  Sentiment result: {sentiment}")
        except Exception as e:
            logger.error(f"  Error: {e}")


def main():
    """Run all tests."""
    logger.info("Starting game release logic tests...")
    
    # Test trailer filtering
    if not test_trailer_filtering():
        logger.error("Trailer filtering test failed")
        return False
    
    # Test sentiment calculation
    test_sentiment_calculation()
    
    logger.info("\nGame release logic tests completed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
