"""
Sentiment signal implementation.

A naive signal that returns random values between -1 and 1 for testing purposes.
"""

import numpy as np
import pandas as pd
from datetime import date
from typing import Dict, Any, Tuple

from .base import SignalBase


class SentimentSignal(SignalBase):
    """Sentiment signal implementation - returns random values for testing."""
    
    def __init__(self, seed: int = None, price_fetcher=None):
        """
        Initialize Sentiment signal.
        
        Args:
            seed: Random seed for reproducible results (optional)
            price_fetcher: Optional price fetcher for data retrieval
        """
        super().__init__(
            signal_id="SENTIMENT",
            name="Sentiment Signal",
            parameters={"seed": seed},
            price_fetcher=price_fetcher
        )
        self.seed = seed
        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)
    
    def calculate(self, price_data: pd.DataFrame, ticker: str, target_date: date) -> float:
        """
        Calculate Sentiment signal value.
        
        Args:
            price_data: DataFrame with OHLCV data, indexed by date
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            
        Returns:
            Random signal value in [-1, 1] range
        """
        # SENTIMENT signal doesn't need price data validation
        # Skip validation when price_data is None (for signals that don't need real data)
        if price_data is not None and not self.validate_price_data(price_data, target_date):
            return np.nan
        
        try:
            # Generate a random value between -1 and 1
            # Use ticker and date to create a deterministic seed for reproducible results
            if self.seed is not None:
                # Create a deterministic seed based on ticker and date
                ticker_hash = hash(ticker) % 10000
                date_hash = hash(str(target_date)) % 10000
                combined_seed = (self.seed + ticker_hash + date_hash) % 2**32
                np.random.seed(combined_seed)
            
            # Generate random value between -1 and 1
            signal_value = np.random.uniform(-1.0, 1.0)
            
            return float(signal_value)
            
        except Exception as e:
            # Log error and return NaN
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating Sentiment signal for {ticker} on {target_date}: {e}")
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
        raise NotImplementedError("SENTIMENT signal doesn't require price data")
    
    def validate_price_data(self, price_data: pd.DataFrame, target_date: date) -> bool:
        """
        Validate that price data is available for the target date.
        
        Args:
            price_data: DataFrame with price data
            target_date: Date to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        if price_data is None or price_data.empty:
            return False
        
        if target_date not in price_data.index:
            return False
        
        # Check if we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in price_data.columns for col in required_columns):
            return False
        
        # Check if the data for target_date is valid
        target_row = price_data.loc[target_date]
        if target_row.isnull().any():
            return False
        
        return True
