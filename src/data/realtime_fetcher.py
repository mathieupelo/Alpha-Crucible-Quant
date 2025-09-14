"""
Enhanced real-time data fetcher for the Alpha Crucible Quant system.

Provides comprehensive market data fetching using yfinance with advanced features:
- Real-time price data
- Market status and trading calendar
- Data validation and error handling
- Caching and performance optimization
- Fallback mechanisms for missing data
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
import yfinance as yf
from dotenv import load_dotenv
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Suppress yfinance warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='yfinance')


class RealTimeDataFetcher:
    """
    Enhanced real-time data fetcher with comprehensive market data capabilities.
    
    Features:
    - Real-time price fetching
    - Market status checking
    - Trading calendar integration
    - Data validation and cleaning
    - Performance optimization with caching
    - Error handling and fallback mechanisms
    """
    
    def __init__(self, 
                 timeout: Optional[int] = None, 
                 retries: Optional[int] = None,
                 cache_duration: int = 300,  # 5 minutes
                 max_workers: int = 5):
        """
        Initialize real-time data fetcher.
        
        Args:
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            cache_duration: Cache duration in seconds
            max_workers: Maximum number of concurrent workers
        """
        self.timeout = timeout or int(os.getenv('YFINANCE_TIMEOUT', '30'))
        self.retries = retries or int(os.getenv('YFINANCE_RETRIES', '3'))
        self.cache_duration = cache_duration
        self.max_workers = max_workers
        
        # Enhanced caching with timestamps
        self._cache = {}
        self._cache_timestamps = {}
        
        # Market status cache
        self._market_status_cache = {}
        self._market_status_timestamp = None
        
        logger.info(f"RealTimeDataFetcher initialized with timeout={self.timeout}s, retries={self.retries}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[cache_key]
        return (datetime.now() - cache_time).total_seconds() < self.cache_duration
    
    def _get_cache(self, cache_key: str) -> Optional[any]:
        """Get data from cache if valid."""
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        return None
    
    def _set_cache(self, cache_key: str, data: any) -> None:
        """Set data in cache with timestamp."""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()
    
    def get_price(self, ticker: str, target_date: date) -> Optional[float]:
        """
        Get the closing price for a ticker on a specific date.
        
        Args:
            ticker: Stock ticker symbol
            target_date: Date to get price for
            
        Returns:
            Closing price or None if not available
        """
        try:
            # Check cache first
            cache_key = f"price_{ticker}_{target_date}"
            cached_price = self._get_cache(cache_key)
            if cached_price is not None:
                return cached_price
            
            # Get price data
            price_data = self._fetch_price_data(ticker, target_date, target_date)
            
            if price_data is not None and not price_data.empty:
                price = price_data['Close'].iloc[0]
                if pd.notna(price) and price > 0:
                    # Cache the result
                    self._set_cache(cache_key, float(price))
                    return float(price)
            
            logger.warning(f"No valid price data available for {ticker} on {target_date}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {ticker} on {target_date}: {e}")
            return None
    
    def get_prices(self, tickers: List[str], target_date: date) -> Dict[str, Optional[float]]:
        """
        Get closing prices for multiple tickers on a specific date.
        
        Args:
            tickers: List of stock ticker symbols
            target_date: Date to get prices for
            
        Returns:
            Dictionary mapping ticker to price (or None if not available)
        """
        prices = {}
        
        # Use concurrent fetching for better performance
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ticker = {
                executor.submit(self.get_price, ticker, target_date): ticker 
                for ticker in tickers
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    price = future.result()
                    prices[ticker] = price
                except Exception as e:
                    logger.error(f"Error fetching price for {ticker}: {e}")
                    prices[ticker] = None
        
        return prices
    
    def get_price_history(self, ticker: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """
        Get historical price data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            DataFrame with OHLCV data or None if not available
        """
        try:
            # Check cache first
            cache_key = f"history_{ticker}_{start_date}_{end_date}"
            cached_data = self._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Fetch data
            price_data = self._fetch_price_data(ticker, start_date, end_date)
            
            if price_data is not None and not price_data.empty:
                # Clean and validate data
                cleaned_data = self._clean_price_data(price_data)
                if not cleaned_data.empty:
                    # Convert timezone-aware datetime index to date index
                    if hasattr(cleaned_data.index, 'date'):
                        cleaned_data.index = cleaned_data.index.date
                    self._set_cache(cache_key, cleaned_data)
                    return cleaned_data
            
            logger.warning(f"No valid historical data available for {ticker} from {start_date} to {end_date}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None
    
    def get_price_matrix(self, tickers: List[str], start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """
        Get price matrix for multiple tickers.
        
        Args:
            tickers: List of stock ticker symbols
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            DataFrame with tickers as columns and dates as index
        """
        try:
            # Check cache first
            cache_key = f"matrix_{'_'.join(sorted(tickers))}_{start_date}_{end_date}"
            cached_data = self._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Fetch data for all tickers
            price_data = {}
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_ticker = {
                    executor.submit(self.get_price_history, ticker, start_date, end_date): ticker 
                    for ticker in tickers
                }
                
                for future in as_completed(future_to_ticker):
                    ticker = future_to_ticker[future]
                    try:
                        data = future.result()
                        if data is not None and not data.empty:
                            price_data[ticker] = data['Close']
                    except Exception as e:
                        logger.error(f"Error fetching data for {ticker}: {e}")
            
            if price_data:
                # Combine all price data
                price_matrix = pd.DataFrame(price_data)
                price_matrix = self._clean_price_data(price_matrix)
                
                if not price_matrix.empty:
                    # Convert timezone-aware datetime index to date index
                    if hasattr(price_matrix.index, 'date'):
                        price_matrix.index = price_matrix.index.date
                    self._set_cache(cache_key, price_matrix)
                    return price_matrix
            
            logger.warning(f"No valid price matrix data available for tickers {tickers}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price matrix: {e}")
            return None
    
    def get_market_status(self) -> Dict[str, bool]:
        """
        Get current market status for major exchanges.
        
        Returns:
            Dictionary mapping exchange to market status (True = open, False = closed)
        """
        try:
            # Check cache first (market status changes infrequently)
            if (self._market_status_timestamp and 
                (datetime.now() - self._market_status_timestamp).total_seconds() < 3600):  # 1 hour cache
                return self._market_status_cache
            
            # Check major US exchanges
            exchanges = {
                'NYSE': '^GSPC',  # S&P 500
                'NASDAQ': '^IXIC',  # NASDAQ
                'DOW': '^DJI'  # Dow Jones
            }
            
            market_status = {}
            for exchange, ticker in exchanges.items():
                try:
                    # Get current data
                    ticker_obj = yf.Ticker(ticker)
                    info = ticker_obj.info
                    
                    # Check if market is open
                    if 'marketState' in info:
                        market_status[exchange] = info['marketState'] == 'REGULAR'
                    else:
                        # Fallback: check if we can get recent data
                        recent_data = ticker_obj.history(period='1d', interval='1m')
                        market_status[exchange] = not recent_data.empty
                        
                except Exception as e:
                    logger.warning(f"Could not determine market status for {exchange}: {e}")
                    market_status[exchange] = False
            
            # Cache the result
            self._market_status_cache = market_status
            self._market_status_timestamp = datetime.now()
            
            return market_status
            
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return {'NYSE': False, 'NASDAQ': False, 'DOW': False}
    
    def get_trading_calendar(self, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get trading calendar for the specified date range.
        
        Args:
            start_date: Start date for calendar
            end_date: End date for calendar
            
        Returns:
            DataFrame with trading days and market status
        """
        try:
            # Check cache first
            cache_key = f"calendar_{start_date}_{end_date}"
            cached_data = self._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Generate date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Check each date
            trading_days = []
            for date_val in date_range:
                date_obj = date_val.date()
                
                # Check if it's a weekend
                is_weekend = date_val.weekday() >= 5
                
                # Check if it's a holiday (simplified check)
                is_holiday = self._is_holiday(date_obj)
                
                # Market is open if not weekend and not holiday
                is_trading_day = not is_weekend and not is_holiday
                
                trading_days.append({
                    'date': date_obj,
                    'is_trading_day': is_trading_day,
                    'is_weekend': is_weekend,
                    'is_holiday': is_holiday,
                    'day_of_week': date_val.strftime('%A')
                })
            
            calendar_df = pd.DataFrame(trading_days)
            calendar_df.set_index('date', inplace=True)
            
            # Cache the result
            self._set_cache(cache_key, calendar_df)
            
            return calendar_df
            
        except Exception as e:
            logger.error(f"Error generating trading calendar: {e}")
            return pd.DataFrame()
    
    def _fetch_price_data(self, ticker: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """Fetch raw price data from yfinance."""
        try:
            ticker_obj = yf.Ticker(ticker)
            
            # Fetch data with retries
            for attempt in range(self.retries):
                try:
                    data = ticker_obj.history(
                        start=start_date,
                        end=end_date + timedelta(days=1),  # Include end date
                        timeout=self.timeout
                    )
                    
                    if not data.empty:
                        return data
                    
                except Exception as e:
                    if attempt == self.retries - 1:
                        raise e
                    time.sleep(1)  # Wait before retry
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def _clean_price_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate price data."""
        if data.empty:
            return data
        
        # Remove rows with NaN values
        cleaned = data.dropna()
        
        # Remove rows with negative prices
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in cleaned.columns:
                cleaned = cleaned[cleaned[col] > 0]
        
        # Remove rows with invalid OHLC relationships
        if all(col in cleaned.columns for col in ['Open', 'High', 'Low', 'Close']):
            cleaned = cleaned[
                (cleaned['High'] >= cleaned['Low']) &
                (cleaned['High'] >= cleaned['Open']) &
                (cleaned['High'] >= cleaned['Close']) &
                (cleaned['Low'] <= cleaned['Open']) &
                (cleaned['Low'] <= cleaned['Close'])
            ]
        
        return cleaned
    
    def _is_holiday(self, date_obj: date) -> bool:
        """Check if a date is a US market holiday (simplified)."""
        # Major US holidays (simplified list)
        holidays = [
            (1, 1),   # New Year's Day
            (7, 4),   # Independence Day
            (12, 25), # Christmas Day
        ]
        
        # Check if it's a holiday
        for month, day in holidays:
            if date_obj.month == month and date_obj.day == day:
                return True
        
        # Check for Thanksgiving (4th Thursday in November)
        if date_obj.month == 11:
            # Find 4th Thursday
            first_thursday = date(date_obj.year, 11, 1)
            while first_thursday.weekday() != 3:  # Thursday is 3
                first_thursday += timedelta(days=1)
            fourth_thursday = first_thursday + timedelta(days=21)
            if date_obj == fourth_thursday:
                return True
        
        return False
    
    def get_cache_info(self) -> Dict[str, any]:
        """Get cache information."""
        return {
            'cache_size': len(self._cache),
            'cache_keys': list(self._cache.keys())[:10],  # First 10 keys as sample
            'oldest_cache': min(self._cache_timestamps.values()) if self._cache_timestamps else None,
            'newest_cache': max(self._cache_timestamps.values()) if self._cache_timestamps else None
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        self._market_status_cache.clear()
        self._market_status_timestamp = None
        logger.info("Cache cleared")
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol is valid.
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            True if ticker is valid, False otherwise
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            # Check if we can get basic info
            return 'symbol' in info and info['symbol'] is not None
            
        except Exception as e:
            logger.warning(f"Ticker validation failed for {ticker}: {e}")
            return False
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, any]]:
        """
        Get detailed information about a ticker.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary with ticker information or None if not available
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            # Extract relevant information
            relevant_info = {
                'symbol': info.get('symbol'),
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'currency': info.get('currency'),
                'exchange': info.get('exchange'),
                'country': info.get('country'),
                'website': info.get('website'),
                'description': info.get('longBusinessSummary')
            }
            
            return {k: v for k, v in relevant_info.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error fetching ticker info for {ticker}: {e}")
            return None


class RealTimeDataFetcherWithFallback(RealTimeDataFetcher):
    """Real-time data fetcher with fallback to previous trading day if data is missing."""
    
    def get_price(self, ticker: str, target_date: date, fallback_days: int = 5) -> Optional[float]:
        """
        Get price with fallback to previous trading days.
        
        Args:
            ticker: Stock ticker symbol
            target_date: Date to get price for
            fallback_days: Number of previous days to check for fallback
            
        Returns:
            Closing price or None if not available
        """
        # Try the target date first
        price = super().get_price(ticker, target_date)
        if price is not None:
            return price
        
        # Try previous trading days
        for i in range(1, fallback_days + 1):
            fallback_date = target_date - timedelta(days=i)
            price = super().get_price(ticker, fallback_date)
            if price is not None:
                logger.info(f"Using fallback price for {ticker} on {fallback_date} (target: {target_date})")
                return price
        
        logger.warning(f"No price data available for {ticker} on {target_date} or {fallback_days} previous days")
        return None


# Create default instances
default_fetcher = RealTimeDataFetcher()
fallback_fetcher = RealTimeDataFetcherWithFallback()
