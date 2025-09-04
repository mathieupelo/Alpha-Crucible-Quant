"""
Base signal class for the Quant Project system.

Defines the interface that all signals must implement.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Any
import pandas as pd


class SignalBase(ABC):
    """Abstract base class for all signals."""
    
    def __init__(self, signal_id: str, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the signal.
        
        Args:
            signal_id: Unique identifier for the signal
            name: Human-readable name for the signal
            parameters: Dictionary of signal parameters
        """
        self.signal_id = signal_id
        self.name = name
        self.parameters = parameters or {}
    
    @abstractmethod
    def calculate(self, price_data: pd.DataFrame, ticker: str, target_date: date) -> float:
        """
        Calculate the signal value for a given ticker on a specific date.
        
        Args:
            price_data: DataFrame with OHLCV data, indexed by date
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            
        Returns:
            Signal value (typically between -1 and 1)
        """
        pass
    
    @abstractmethod
    def get_min_lookback_period(self) -> int:
        """
        Get the minimum number of days of price data needed for calculation.
        
        Returns:
            Minimum lookback period in days
        """
        pass
    
    @abstractmethod
    def get_max_lookback_period(self) -> int:
        """
        Get the maximum number of days of price data needed for calculation.
        
        Returns:
            Maximum lookback period in days
        """
        pass
    
    def validate_price_data(self, price_data: pd.DataFrame, target_date: date) -> bool:
        """
        Validate that price data is sufficient for signal calculation.
        
        Args:
            price_data: DataFrame with OHLCV data
            target_date: Date to calculate signal for
            
        Returns:
            True if data is valid, False otherwise
        """
        if price_data is None or price_data.empty:
            return False
        
        if target_date not in price_data.index:
            return False
        
        # Check if we have enough historical data
        min_lookback = self.get_min_lookback_period()
        available_days = len(price_data[price_data.index <= target_date])
        
        return available_days >= min_lookback
    
    def get_required_price_data(self, target_date: date) -> tuple[date, date]:
        """
        Get the date range required for signal calculation.
        
        Args:
            target_date: Date to calculate signal for
            
        Returns:
            Tuple of (start_date, end_date) for required price data
        """
        from datetime import timedelta
        
        start_date = target_date - timedelta(days=self.get_max_lookback_period())
        end_date = target_date
        
        return start_date, end_date
    
    def __str__(self) -> str:
        """String representation of the signal."""
        return f"{self.name} ({self.signal_id})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the signal."""
        return f"{self.__class__.__name__}(signal_id='{self.signal_id}', name='{self.name}', parameters={self.parameters})"
