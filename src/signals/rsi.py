"""
RSI (Relative Strength Index) signal implementation.

Calculates RSI-based signals for stock selection.
"""

import numpy as np
import pandas as pd
import talib as ta
from datetime import date
from typing import Dict, Any

from .base import SignalBase


class RSISignal(SignalBase):
    """RSI (Relative Strength Index) signal implementation."""
    
    def __init__(self, period: int = 14, price_fetcher=None):
        """
        Initialize RSI signal.
        
        Args:
            period: RSI calculation period (default: 14)
            price_fetcher: Optional price fetcher for data retrieval
        """
        super().__init__(
            signal_id="RSI",
            name="Relative Strength Index",
            parameters={"period": period},
            price_fetcher=price_fetcher
        )
        self.period = period
    
    def calculate(self, price_data: pd.DataFrame, ticker: str, target_date: date) -> float:
        """
        Calculate RSI signal value.
        
        Args:
            price_data: DataFrame with OHLCV data, indexed by date
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            
        Returns:
            RSI signal value normalized to [-1, 1] range
        """
        if not self.validate_price_data(price_data, target_date):
            return np.nan
        
        try:
            # Get close prices up to target date
            close_prices = price_data.loc[price_data.index <= target_date, 'Close']
            
            if len(close_prices) < self.period + 1:
                return np.nan
            
            # Calculate RSI
            rsi_values = ta.RSI(close_prices.values, timeperiod=self.period)
            
            if len(rsi_values) == 0 or np.isnan(rsi_values[-1]):
                return np.nan
            
            rsi_value = rsi_values[-1]
            
            # Normalize RSI to [-1, 1] range
            # RSI > 70 is overbought (bearish signal)
            # RSI < 30 is oversold (bullish signal)
            # RSI = 50 is neutral
            
            if rsi_value >= 70:
                # Overbought - bearish signal
                signal_value = -1.0
            elif rsi_value <= 30:
                # Oversold - bullish signal
                signal_value = 1.0
            else:
                # Linear interpolation between 30-70 range
                if rsi_value > 50:
                    # Above 50, scale to [0, -1]
                    signal_value = -((rsi_value - 50) / 20)
                else:
                    # Below 50, scale to [0, 1]
                    signal_value = ((50 - rsi_value) / 20)
            
            return np.clip(signal_value, -1.0, 1.0)
            
        except Exception as e:
            print(f"[ERROR] RSI calculation failed for {ticker} on {target_date}: {e}")
            return np.nan
    
    def get_min_lookback_period(self) -> int:
        """Get minimum lookback period for RSI calculation."""
        return self.period + 10  # Extra buffer for calculation stability
    
    def get_max_lookback_period(self) -> int:
        """Get maximum lookback period for RSI calculation."""
        return self.period * 3  # 3x period for sufficient data
    
    def get_rsi_value(self, price_data: pd.DataFrame, target_date: date) -> float:
        """
        Get the raw RSI value (0-100) for a given date.
        
        Args:
            price_data: DataFrame with OHLCV data
            target_date: Date to calculate RSI for
            
        Returns:
            Raw RSI value (0-100) or NaN if calculation fails
        """
        if not self.validate_price_data(price_data, target_date):
            return np.nan
        
        try:
            close_prices = price_data.loc[price_data.index <= target_date, 'Close']
            
            if len(close_prices) < self.period + 1:
                return np.nan
            
            rsi_values = ta.RSI(close_prices.values, timeperiod=self.period)
            
            if len(rsi_values) == 0 or np.isnan(rsi_values[-1]):
                return np.nan
            
            return float(rsi_values[-1])
            
        except Exception as e:
            print(f"[ERROR] Raw RSI calculation failed: {e}")
            return np.nan
