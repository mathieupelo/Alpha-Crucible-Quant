"""
MACD (Moving Average Convergence Divergence) signal implementation.

Calculates MACD-based signals for stock selection.
"""

import numpy as np
import pandas as pd
import talib as ta
from datetime import date
from typing import Dict, Any

from .base import SignalBase


class MACDSignal(SignalBase):
    """MACD (Moving Average Convergence Divergence) signal implementation."""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        Initialize MACD signal.
        
        Args:
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line EMA period (default: 9)
        """
        super().__init__(
            signal_id="MACD",
            name="Moving Average Convergence Divergence",
            parameters={"fast_period": fast_period, "slow_period": slow_period, "signal_period": signal_period}
        )
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, price_data: pd.DataFrame, ticker: str, target_date: date) -> float:
        """
        Calculate MACD signal value.
        
        Args:
            price_data: DataFrame with OHLCV data, indexed by date
            ticker: Stock ticker symbol
            target_date: Date to calculate signal for
            
        Returns:
            MACD signal value normalized to [-1, 1] range
        """
        if not self.validate_price_data(price_data, target_date):
            return np.nan
        
        try:
            # Get close prices up to target date
            close_prices = price_data.loc[price_data.index <= target_date, 'Close']
            
            if len(close_prices) < self.slow_period + self.signal_period:
                return np.nan
            
            # Calculate MACD
            macd_line, signal_line, histogram = ta.MACD(
                close_prices.values,
                fastperiod=self.fast_period,
                slowperiod=self.slow_period,
                signalperiod=self.signal_period
            )
            
            if len(macd_line) == 0 or len(signal_line) == 0 or len(histogram) == 0:
                return np.nan
            
            macd_value = macd_line[-1]
            signal_value = signal_line[-1]
            histogram_value = histogram[-1]
            
            if np.isnan(macd_value) or np.isnan(signal_value) or np.isnan(histogram_value):
                return np.nan
            
            # Calculate signal based on MACD components
            signal_score = 0.0
            
            # 1. MACD line above/below signal line (50% weight)
            if macd_value > signal_value:
                # Bullish crossover or MACD above signal
                signal_score += 0.5 * min(abs(histogram_value) * 100, 1.0)
            else:
                # Bearish crossover or MACD below signal
                signal_score -= 0.5 * min(abs(histogram_value) * 100, 1.0)
            
            # 2. MACD line above/below zero (30% weight)
            if macd_value > 0:
                signal_score += 0.3 * min(macd_value * 10, 1.0)
            else:
                signal_score -= 0.3 * min(abs(macd_value) * 10, 1.0)
            
            # 3. Histogram momentum (20% weight)
            if len(histogram) >= 2:
                prev_histogram = histogram[-2]
                if not np.isnan(prev_histogram):
                    histogram_change = histogram_value - prev_histogram
                    if histogram_change > 0:
                        signal_score += 0.2 * min(histogram_change * 50, 1.0)
                    else:
                        signal_score -= 0.2 * min(abs(histogram_change) * 50, 1.0)
            
            return np.clip(signal_score, -1.0, 1.0)
            
        except Exception as e:
            print(f"[ERROR] MACD calculation failed for {ticker} on {target_date}: {e}")
            return np.nan
    
    def get_min_lookback_period(self) -> int:
        """Get minimum lookback period for MACD calculation."""
        return self.slow_period + self.signal_period + 10  # Extra buffer
    
    def get_max_lookback_period(self) -> int:
        """Get maximum lookback period for MACD calculation."""
        return self.slow_period * 3  # 3x slow period for sufficient data
    
    def get_macd_values(self, price_data: pd.DataFrame, target_date: date) -> tuple[float, float, float]:
        """
        Get the raw MACD values for a given date.
        
        Args:
            price_data: DataFrame with OHLCV data
            target_date: Date to calculate MACD for
            
        Returns:
            Tuple of (macd_line, signal_line, histogram) or (NaN, NaN, NaN) if calculation fails
        """
        if not self.validate_price_data(price_data, target_date):
            return np.nan, np.nan, np.nan
        
        try:
            close_prices = price_data.loc[price_data.index <= target_date, 'Close']
            
            if len(close_prices) < self.slow_period + self.signal_period:
                return np.nan, np.nan, np.nan
            
            macd_line, signal_line, histogram = ta.MACD(
                close_prices.values,
                fastperiod=self.fast_period,
                slowperiod=self.slow_period,
                signalperiod=self.signal_period
            )
            
            if len(macd_line) == 0 or len(signal_line) == 0 or len(histogram) == 0:
                return np.nan, np.nan, np.nan
            
            macd_value = macd_line[-1]
            signal_value = signal_line[-1]
            histogram_value = histogram[-1]
            
            if np.isnan(macd_value) or np.isnan(signal_value) or np.isnan(histogram_value):
                return np.nan, np.nan, np.nan
            
            return float(macd_value), float(signal_value), float(histogram_value)
            
        except Exception as e:
            print(f"[ERROR] Raw MACD calculation failed: {e}")
            return np.nan, np.nan, np.nan
