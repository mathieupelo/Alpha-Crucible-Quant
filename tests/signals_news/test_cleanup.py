#!/usr/bin/env python3
"""
Cleanup utilities for tests to ensure no test data remains in the database.
"""

from datetime import date
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class TestDataCleanup:
    """Helper class to track and clean up test data."""
    
    def __init__(self):
        self.inserted_signals: List[dict] = []  # List of (ticker, asof_date, signal_name)
        self.inserted_sentiments: List[int] = []  # List of news_id
        self.inserted_signal_ids: Set[int] = set()  # Set of signal_id that were created
    
    def track_signal(self, ticker: str, asof_date: date, signal_name: str):
        """Track a signal that was inserted."""
        self.inserted_signals.append({
            'ticker': ticker,
            'asof_date': asof_date,
            'signal_name': signal_name
        })
    
    def track_sentiment(self, news_id: int):
        """Track a sentiment that was inserted."""
        self.inserted_sentiments.append(news_id)
    
    def track_signal_id(self, signal_id: int):
        """Track a signal_id that was created."""
        self.inserted_signal_ids.add(signal_id)
    
    def cleanup_signals(self, main_conn):
        """Remove all tracked signals from signal_raw."""
        if not self.inserted_signals:
            return
        
        try:
            with main_conn.cursor() as cursor:
                for signal in self.inserted_signals:
                    cursor.execute("""
                        DELETE FROM signal_raw
                        WHERE ticker = %s 
                        AND asof_date = %s 
                        AND signal_name = %s
                    """, (signal['ticker'], signal['asof_date'], signal['signal_name']))
                main_conn.commit()
                logger.info(f"Cleaned up {len(self.inserted_signals)} test signals")
        except Exception as e:
            logger.error(f"Error cleaning up signals: {e}")
            main_conn.rollback()
    
    def cleanup_sentiments(self, ore_conn):
        """Remove all tracked sentiments from copper.yfinance_news_sentiment."""
        if not self.inserted_sentiments:
            return
        
        try:
            with ore_conn.cursor() as cursor:
                for news_id in self.inserted_sentiments:
                    cursor.execute("""
                        DELETE FROM copper.yfinance_news_sentiment
                        WHERE yfinance_news_id = %s
                    """, (news_id,))
                ore_conn.commit()
                logger.info(f"Cleaned up {len(self.inserted_sentiments)} test sentiments")
        except Exception as e:
            logger.error(f"Error cleaning up sentiments: {e}")
            ore_conn.rollback()
    
    def cleanup_signal_records(self, main_conn):
        """Remove signal records that were created during tests."""
        if not self.inserted_signal_ids:
            return
        
        try:
            with main_conn.cursor() as cursor:
                # Check if signals table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'signal'
                    )
                """)
                if not cursor.fetchone()[0]:
                    return  # signals table doesn't exist
                
                # Delete test signal records (only if they were created by us)
                # Note: We can't easily track which signals we created vs existed,
                # so we'll only delete if we're sure they're test signals
                # For safety, we'll skip this unless we have a way to mark test signals
                logger.info(f"Skipping signal table cleanup (safety: don't delete existing signals)")
        except Exception as e:
            logger.error(f"Error cleaning up signal records: {e}")
            main_conn.rollback()
    
    def cleanup_all(self, main_conn, ore_conn):
        """Clean up all tracked test data."""
        self.cleanup_signals(main_conn)
        self.cleanup_sentiments(ore_conn)
        self.cleanup_signal_records(main_conn)
    
    def reset(self):
        """Reset tracking (useful for reusing the cleanup object)."""
        self.inserted_signals.clear()
        self.inserted_sentiments.clear()
        self.inserted_signal_ids.clear()


def cleanup_test_signals(main_conn, ticker: str, asof_date: date, signal_name: str):
    """Helper function to clean up a specific test signal."""
    try:
        with main_conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM signal_raw
                WHERE ticker = %s 
                AND asof_date = %s 
                AND signal_name = %s
            """, (ticker, asof_date, signal_name))
            main_conn.commit()
    except Exception as e:
        logger.error(f"Error cleaning up signal {ticker}/{asof_date}/{signal_name}: {e}")
        main_conn.rollback()


def cleanup_test_sentiment(ore_conn, news_id: int):
    """Helper function to clean up a specific test sentiment."""
    try:
        with ore_conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM copper.yfinance_news_sentiment
                WHERE yfinance_news_id = %s
            """, (news_id,))
            ore_conn.commit()
    except Exception as e:
        logger.error(f"Error cleaning up sentiment for news_id {news_id}: {e}")
        ore_conn.rollback()

