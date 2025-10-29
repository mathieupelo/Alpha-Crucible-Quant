"""
Stock price fetcher using yfinance.

Replaces the database-stored stock prices with real-time fetching from Yahoo Finance.
This module now uses the enhanced RealTimeDataFetcher for better performance and reliability.
"""

import os
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PriceFetcher:
    """
    Fetches stock prices using yfinance API.
    
    This class now wraps the enhanced RealTimeDataFetcher for better performance
    and maintains backward compatibility with existing code.
    """
    
    # Configuration constants
    DEFAULT_FALLBACK_DAYS = 5
    
    def __init__(self, timeout: Optional[int] = None, retries: Optional[int] = None):
        """Initialize price fetcher with configuration."""
        # Import here to avoid circular imports
        from src.data import RealTimeDataFetcher
        
        # Configuration constants
        DEFAULT_TIMEOUT_SECONDS = 10
        DEFAULT_RETRY_ATTEMPTS = 3
        
        self.timeout = timeout or int(os.getenv('YFINANCE_TIMEOUT', str(DEFAULT_TIMEOUT_SECONDS)))
        self.retries = retries or int(os.getenv('YFINANCE_RETRIES', str(DEFAULT_RETRY_ATTEMPTS)))
        
        # Use the enhanced real-time data fetcher
        self._real_fetcher = RealTimeDataFetcher(
            timeout=self.timeout,
            retries=self.retries
        )
        
        # Maintain backward compatibility
        self._cache = self._real_fetcher._cache
    
    def get_price(self, ticker: str, target_date: date) -> Optional[float]:
        """
        Get the closing price for a ticker on a specific date.
        
        Args:
            ticker: Stock ticker symbol
            target_date: Date to get price for
            
        Returns:
            Closing price or None if not available
        """
        return self._real_fetcher.get_price(ticker, target_date)
    
    def get_prices(self, tickers: List[str], target_date: date) -> Dict[str, Optional[float]]:
        """
        Get closing prices for multiple tickers on a specific date.
        
        Args:
            tickers: List of stock ticker symbols
            target_date: Date to get prices for
            
        Returns:
            Dictionary mapping ticker to price (or None if not available)
        """
        return self._real_fetcher.get_prices(tickers, target_date)
    
    def get_price_history(self, ticker: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """
        Get price history for a ticker over a date range.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for price history
            end_date: End date for price history
            
        Returns:
            DataFrame with OHLCV data or None if not available
        """
        return self._real_fetcher.get_price_history(ticker, start_date, end_date)
    
    def get_price_history_batch(self, tickers: List[str], start_date: date, end_date: date) -> Dict[str, pd.DataFrame]:
        """
        Get price history for multiple tickers over a date range.
        
        Args:
            tickers: List of stock ticker symbols
            start_date: Start date for price history
            end_date: End date for price history
            
        Returns:
            Dictionary mapping ticker to DataFrame with OHLCV data
        """
        price_histories = {}
        
        for ticker in tickers:
            price_histories[ticker] = self.get_price_history(ticker, start_date, end_date)
        
        return price_histories
    
    def get_price_matrix(self, tickers: List[str], start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get a price matrix with dates as index and tickers as columns.
        
        Args:
            tickers: List of stock ticker symbols
            start_date: Start date for price history
            end_date: End date for price history
            
        Returns:
            DataFrame with dates as index and tickers as columns
        """
        return self._real_fetcher.get_price_matrix(tickers, start_date, end_date)
    
    def _fetch_price_data(self, ticker: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """
        Fetch price data from yfinance with error handling and retries.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with price data or None if failed
        """
        for attempt in range(self.retries):
            try:
                # Create yfinance ticker object
                stock = yf.Ticker(ticker)
                
                # Fetch data
                data = stock.history(
                    start=start_date,
                    end=end_date + timedelta(days=1),  # Add 1 day to include end_date
                    timeout=self.timeout
                )
                
                if data.empty:
                    logger.warning(f"No data returned for {ticker} from {start_date} to {end_date}")
                    return None
                
                # Convert index to date and filter to requested range
                data.index = data.index.date
                data = data[(data.index >= start_date) & (data.index <= end_date)]
                
                return data
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                if attempt == self.retries - 1:
                    logger.error(f"All attempts failed for {ticker}")
                    return None
                
                # Wait before retry
                import time
                RETRY_DELAY_SECONDS = 1
                time.sleep(RETRY_DELAY_SECONDS)
        
        return None
    
    def get_trading_days(self, start_date: date, end_date: date, ticker: str = 'SPY') -> List[date]:
        """
        Get list of trading days between start and end dates.
        
        Args:
            start_date: Start date
            end_date: End date
            ticker: Ticker to use for determining trading days (default: SPY)
            
        Returns:
            List of trading dates
        """
        try:
            # Use SPY as a proxy for trading days
            price_data = self.get_price_history(ticker, start_date, end_date)
            
            if price_data is not None and not price_data.empty:
                return sorted(price_data.index.tolist())
            
            # Fallback: return all weekdays
            logger.warning(f"Could not determine trading days for {ticker}, using weekdays")
            trading_days = []
            current_date = start_date
            
            while current_date <= end_date:
                WEEKDAY_FRIDAY = 4  # Friday is weekday 4
                if current_date.weekday() < WEEKDAY_FRIDAY + 1:  # Monday = 0, Friday = 4
                    trading_days.append(current_date)
                current_date += timedelta(days=1)
            
            return trading_days
            
        except Exception as e:
            logger.error(f"Error getting trading days: {e}")
            # Fallback: return all weekdays
            trading_days = []
            current_date = start_date
            
            while current_date <= end_date:
                WEEKDAY_FRIDAY = 4  # Friday is weekday 4
                if current_date.weekday() < WEEKDAY_FRIDAY + 1:  # Monday = 0, Friday = 4
                    trading_days.append(current_date)
                current_date += timedelta(days=1)
            
            return trading_days
    
    def clear_cache(self):
        """Clear the price cache."""
        self._real_fetcher.clear_cache()
        logger.info("Price cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the cache."""
        return self._real_fetcher.get_cache_info()


class PriceFetcherWithFallback(PriceFetcher):
    """Price fetcher with fallback to previous trading day if data is missing."""
    
    def __init__(self, timeout: Optional[int] = None, retries: Optional[int] = None):
        """Initialize price fetcher with fallback capabilities."""
        # Import here to avoid circular imports
        from src.data import RealTimeDataFetcherWithFallback
        
        self.timeout = timeout or int(os.getenv('YFINANCE_TIMEOUT', '10'))
        self.retries = retries or int(os.getenv('YFINANCE_RETRIES', '3'))
        
        # Use the enhanced real-time data fetcher with fallback
        self._real_fetcher = RealTimeDataFetcherWithFallback(
            timeout=self.timeout,
            retries=self.retries
        )
        
        # Maintain backward compatibility
        self._cache = self._real_fetcher._cache
    
    def get_price(self, ticker: str, target_date: date, fallback_days: int = PriceFetcher.DEFAULT_FALLBACK_DAYS) -> Optional[float]:
        """
        Get price with fallback to previous trading days.
        
        Args:
            ticker: Stock ticker symbol
            target_date: Date to get price for
            fallback_days: Number of previous days to check for fallback
            
        Returns:
            Closing price or None if not available
        """
        return self._real_fetcher.get_price(ticker, target_date, fallback_days)
