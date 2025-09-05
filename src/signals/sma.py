"""
SMA (Simple Moving Average) signal implementation.

Calculates SMA-based signals for stock selection.
"""

import numpy as np
import pandas as pd
import talib as ta
from datetime import date
from typing import Dict, Any

from .base import SignalBase


class SMASignal(SignalBase):
    """SMA (Simple Moving Average) signal implementation."""
    
    def __init__(self, short_period: int = 50, long_period: int = 200, price_fetcher=None):
        """
        Initialize SMA signal.
        
        Args:
            short_period: Short-term SMA period (default: 50)
            long_period: Long-term SMA period (default: 200)
            price_fetcher: Optional price fetcher for data retrieval
        """
        super().__init__(
            signal_id="SMA",
            name="Simple Moving Average",
            parameters={"short_period": short_period, "long_period": long_period},
            price_fetcher=price_fetcher
        )
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate(self, price_data: pd.DataFrame, ticker: str, target_date: date) -> float:
        """
        Calculate SMA signal value.
        
        Args:
            price_data: DataFrame with OHLCV data, indexed by date
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            
        Returns:
            SMA signal value normalized to [-1, 1] range
        """
        if not self.validate_price_data(price_data, target_date):
            return np.nan
        
        try:
            # Get close prices up to target date
            close_prices = price_data.loc[price_data.index <= target_date, 'Close']
            
            if len(close_prices) < self.long_period:
                return np.nan
            
            # Calculate SMAs
            sma_short = ta.SMA(close_prices.values, timeperiod=self.short_period)
            sma_long = ta.SMA(close_prices.values, timeperiod=self.long_period)
            
            if len(sma_short) == 0 or len(sma_long) == 0:
                return np.nan
            
            sma_short_value = sma_short[-1]
            sma_long_value = sma_long[-1]
            
            if np.isnan(sma_short_value) or np.isnan(sma_long_value):
                return np.nan
            
            # Get current price
            current_price = close_prices.iloc[-1]
            
            # Calculate signal based on price position relative to SMAs
            # and SMA crossover
            
            # 1. Price above/below SMAs
            price_above_short = current_price > sma_short_value
            price_above_long = current_price > sma_long_value
            short_above_long = sma_short_value > sma_long_value
            
            # 2. Calculate percentage distances
            short_distance = (current_price - sma_short_value) / sma_short_value
            long_distance = (current_price - sma_long_value) / sma_long_value
            sma_distance = (sma_short_value - sma_long_value) / sma_long_value
            
            # 3. Combine signals
            signal_value = 0.0
            
            # Price momentum (40% weight)
            if price_above_short and price_above_long:
                signal_value += 0.4 * min(short_distance * 10, 1.0)  # Cap at 1.0
            elif not price_above_short and not price_above_long:
                signal_value -= 0.4 * min(abs(short_distance) * 10, 1.0)
            
            # SMA crossover (40% weight)
            if short_above_long:
                signal_value += 0.4 * min(sma_distance * 20, 1.0)  # Cap at 1.0
            else:
                signal_value -= 0.4 * min(abs(sma_distance) * 20, 1.0)
            
            # Long-term trend (20% weight)
            if price_above_long:
                signal_value += 0.2 * min(long_distance * 5, 1.0)
            else:
                signal_value -= 0.2 * min(abs(long_distance) * 5, 1.0)
            
            return np.clip(signal_value, -1.0, 1.0)
            
        except Exception as e:
            print(f"[ERROR] SMA calculation failed for {ticker} on {target_date}: {e}")
            return np.nan
    
    def get_min_lookback_period(self) -> int:
        """Get minimum lookback period for SMA calculation."""
        return self.long_period + 10  # Extra buffer for calculation stability
    
    def get_max_lookback_period(self) -> int:
        """Get maximum lookback period for SMA calculation."""
        return self.long_period * 2  # 2x long period for sufficient data
    
    def get_sma_values(self, price_data: pd.DataFrame, target_date: date) -> tuple[float, float]:
        """
        Get the raw SMA values for a given date.
        
        Args:
            price_data: DataFrame with OHLCV data
            target_date: Date to calculate SMAs for
            
        Returns:
            Tuple of (short_sma, long_sma) or (NaN, NaN) if calculation fails
        """
        if not self.validate_price_data(price_data, target_date):
            return np.nan, np.nan
        
        try:
            close_prices = price_data.loc[price_data.index <= target_date, 'Close']
            
            if len(close_prices) < self.long_period:
                return np.nan, np.nan
            
            sma_short = ta.SMA(close_prices.values, timeperiod=self.short_period)
            sma_long = ta.SMA(close_prices.values, timeperiod=self.long_period)
            
            if len(sma_short) == 0 or len(sma_long) == 0:
                return np.nan, np.nan
            
            short_value = sma_short[-1]
            long_value = sma_long[-1]
            
            if np.isnan(short_value) or np.isnan(long_value):
                return np.nan, np.nan
            
            return float(short_value), float(long_value)
            
        except Exception as e:
            print(f"[ERROR] Raw SMA calculation failed: {e}")
            return np.nan, np.nan
