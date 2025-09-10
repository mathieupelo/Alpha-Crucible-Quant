"""
Tests for the signal system.

Tests signal calculation, validation, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from signals import RSISignal, SMASignal, MACDSignal, SignalCalculator
from signals.registry import SignalRegistry


class TestRSISignal:
    """Test RSI signal implementation."""
    
    def setup_method(self):
        """Setup test data."""
        self.signal = RSISignal(period=14)
        self.ticker = 'AAPL'
        self.target_date = date(2024, 1, 15)
        
        # Create mock price data
        dates = pd.date_range(start='2023-12-01', end='2024-01-15', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
        
        self.price_data = pd.DataFrame({
            'Close': prices
        }, index=dates.date)
    
    def test_rsi_initialization(self):
        """Test RSI signal initialization."""
        assert self.signal.signal_id == 'RSI'
        assert self.signal.name == 'Relative Strength Index'
        assert self.signal.period == 14
        assert self.signal.get_min_lookback_period() == 24  # 14 + 10
        assert self.signal.get_max_lookback_period() == 42  # 14 * 3
    
    def test_rsi_calculation_valid_data(self):
        """Test RSI calculation with valid data."""
        result = self.signal.calculate(self.price_data, self.ticker, self.target_date)
        
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_rsi_calculation_insufficient_data(self):
        """Test RSI calculation with insufficient data."""
        # Create price data with only 10 days
        short_data = self.price_data.tail(10)
        result = self.signal.calculate(short_data, self.ticker, self.target_date)
        
        assert np.isnan(result)
    
    def test_rsi_calculation_missing_date(self):
        """Test RSI calculation with missing target date."""
        # Remove target date from data
        data_without_date = self.price_data[self.price_data.index != self.target_date]
        result = self.signal.calculate(data_without_date, self.ticker, self.target_date)
        
        assert np.isnan(result)
    
    def test_rsi_calculation_empty_data(self):
        """Test RSI calculation with empty data."""
        empty_data = pd.DataFrame()
        result = self.signal.calculate(empty_data, self.ticker, self.target_date)
        
        assert np.isnan(result)
    
    def test_rsi_calculation_none_data(self):
        """Test RSI calculation with None data."""
        result = self.signal.calculate(None, self.ticker, self.target_date)
        
        assert np.isnan(result)
    
    def test_rsi_validation(self):
        """Test RSI data validation."""
        # Valid data
        assert self.signal.validate_price_data(self.price_data, self.target_date)
        
        # Insufficient data
        short_data = self.price_data.tail(10)
        assert not self.signal.validate_price_data(short_data, self.target_date)
        
        # Missing date
        data_without_date = self.price_data[self.price_data.index != self.target_date]
        assert not self.signal.validate_price_data(data_without_date, self.target_date)
    
    def test_rsi_get_required_data_range(self):
        """Test RSI required data range calculation."""
        start_date, end_date = self.signal.get_required_price_data(self.target_date)
        
        expected_start = self.target_date - timedelta(days=42)
        assert start_date == expected_start
        assert end_date == self.target_date


class TestSMASignal:
    """Test SMA signal implementation."""
    
    def setup_method(self):
        """Setup test data."""
        self.signal = SMASignal(short_period=50, long_period=200)
        self.ticker = 'MSFT'
        self.target_date = date(2024, 1, 15)
        
        # Create mock price data
        dates = pd.date_range(start='2023-06-01', end='2024-01-15', freq='D')
        np.random.seed(42)
        prices = 200 + np.cumsum(np.random.randn(len(dates)) * 0.01)
        
        self.price_data = pd.DataFrame({
            'Close': prices
        }, index=dates.date)
    
    def test_sma_initialization(self):
        """Test SMA signal initialization."""
        assert self.signal.signal_id == 'SMA'
        assert self.signal.name == 'Simple Moving Average'
        assert self.signal.short_period == 50
        assert self.signal.long_period == 200
        assert self.signal.get_min_lookback_period() == 210  # 200 + 10
        assert self.signal.get_max_lookback_period() == 400  # 200 * 2
    
    def test_sma_calculation_valid_data(self):
        """Test SMA calculation with valid data."""
        result = self.signal.calculate(self.price_data, self.ticker, self.target_date)
        
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_sma_calculation_insufficient_data(self):
        """Test SMA calculation with insufficient data."""
        # Create price data with only 100 days
        short_data = self.price_data.tail(100)
        result = self.signal.calculate(short_data, self.ticker, self.target_date)
        
        assert np.isnan(result)
    
    def test_sma_get_sma_values(self):
        """Test SMA raw values calculation."""
        short_sma, long_sma = self.signal.get_sma_values(self.price_data, self.target_date)
        
        assert not np.isnan(short_sma)
        assert not np.isnan(long_sma)
        assert short_sma > 0
        assert long_sma > 0


class TestMACDSignal:
    """Test MACD signal implementation."""
    
    def setup_method(self):
        """Setup test data."""
        self.signal = MACDSignal(fast_period=12, slow_period=26, signal_period=9)
        self.ticker = 'GOOGL'
        self.target_date = date(2024, 1, 15)
        
        # Create mock price data
        dates = pd.date_range(start='2023-06-01', end='2024-01-15', freq='D')
        np.random.seed(42)
        prices = 150 + np.cumsum(np.random.randn(len(dates)) * 0.015)
        
        self.price_data = pd.DataFrame({
            'Close': prices
        }, index=dates.date)
    
    def test_macd_initialization(self):
        """Test MACD signal initialization."""
        assert self.signal.signal_id == 'MACD'
        assert self.signal.name == 'Moving Average Convergence Divergence'
        assert self.signal.fast_period == 12
        assert self.signal.slow_period == 26
        assert self.signal.signal_period == 9
        assert self.signal.get_min_lookback_period() == 45  # 26 + 9 + 10
        assert self.signal.get_max_lookback_period() == 78  # 26 * 3
    
    def test_macd_calculation_valid_data(self):
        """Test MACD calculation with valid data."""
        result = self.signal.calculate(self.price_data, self.ticker, self.target_date)
        
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_macd_calculation_insufficient_data(self):
        """Test MACD calculation with insufficient data."""
        # Create price data with only 30 days
        short_data = self.price_data.tail(30)
        result = self.signal.calculate(short_data, self.ticker, self.target_date)
        
        assert np.isnan(result)
    
    def test_macd_get_macd_values(self):
        """Test MACD raw values calculation."""
        macd_line, signal_line, histogram = self.signal.get_macd_values(self.price_data, self.target_date)
        
        assert not np.isnan(macd_line)
        assert not np.isnan(signal_line)
        assert not np.isnan(histogram)


class TestSignalRegistry:
    """Test signal registry functionality."""
    
    def setup_method(self):
        """Setup test registry."""
        self.registry = SignalRegistry()
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        assert len(self.registry) > 0
        assert 'RSI' in self.registry
        assert 'SMA' in self.registry
        assert 'MACD' in self.registry
    
    def test_get_signal(self):
        """Test getting signal from registry."""
        signal = self.registry.get_signal('RSI')
        assert signal is not None
        assert signal.signal_id == 'RSI'
        
        signal = self.registry.get_signal('SMA', short_period=20, long_period=50)
        assert signal is not None
        assert signal.short_period == 20
        assert signal.long_period == 50
    
    def test_get_nonexistent_signal(self):
        """Test getting nonexistent signal."""
        signal = self.registry.get_signal('NONEXISTENT')
        assert signal is None
    
    def test_get_available_signals(self):
        """Test getting available signals."""
        signals = self.registry.get_available_signals()
        assert 'RSI' in signals
        assert 'SMA' in signals
        assert 'MACD' in signals
    
    def test_get_signal_info(self):
        """Test getting signal information."""
        info = self.registry.get_signal_info('RSI')
        assert info is not None
        assert info['signal_id'] == 'RSI'
        assert info['name'] == 'Relative Strength Index'
        assert 'parameters' in info
        assert 'min_lookback' in info
        assert 'max_lookback' in info
    
    def test_get_nonexistent_signal_info(self):
        """Test getting information for nonexistent signal."""
        info = self.registry.get_signal_info('NONEXISTENT')
        assert info is None


class TestSignalCalculator:
    """Test signal calculator functionality."""
    
    def setup_method(self):
        """Setup test calculator."""
        self.price_fetcher = Mock()
        self.database_manager = Mock()
        self.calculator = SignalCalculator(self.database_manager)
        
        # Mock price data
        dates = pd.date_range(start='2023-12-01', end='2024-01-15', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
        
        self.price_data = pd.DataFrame({
            'Close': prices
        }, index=dates.date)
    
    def test_calculator_initialization(self):
        """Test calculator initialization."""
        assert self.calculator.price_fetcher is not None
        assert self.calculator.database_manager is not None
        assert self.calculator.registry is not None
    
    def test_calculate_signal_for_ticker(self):
        """Test calculating signal for single ticker."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'RSI', date(2024, 1, 15)
        )
        
        assert result is not None
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_calculate_signal_for_ticker_no_data(self):
        """Test calculating signal with no price data."""
        self.price_fetcher.get_price_history.return_value = None
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'RSI', date(2024, 1, 15)
        )
        
        assert result is None
    
    def test_calculate_signal_for_ticker_invalid_signal(self):
        """Test calculating signal with invalid signal ID."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'INVALID', date(2024, 1, 15)
        )
        
        assert result is None
    
    def test_combine_signals(self):
        """Test signal combination."""
        # Create mock signal scores
        signal_scores = pd.DataFrame([
            {'ticker': 'AAPL', 'date': date(2024, 1, 15), 'signal_id': 'RSI', 'score': 0.5},
            {'ticker': 'AAPL', 'date': date(2024, 1, 15), 'signal_id': 'SMA', 'score': 0.3},
            {'ticker': 'MSFT', 'date': date(2024, 1, 15), 'signal_id': 'RSI', 'score': 0.2},
            {'ticker': 'MSFT', 'date': date(2024, 1, 15), 'signal_id': 'SMA', 'score': 0.4},
        ])
        
        signal_weights = {'RSI': 0.6, 'SMA': 0.4}
        
        combined = self.calculator.combine_signals(signal_scores, signal_weights)
        
        assert not combined.empty
        assert 'ticker' in combined.columns
        assert 'date' in combined.columns
        assert 'combined_score' in combined.columns
        
        # Check AAPL combined score: 0.5 * 0.6 + 0.3 * 0.4 = 0.42
        aapl_score = combined[combined['ticker'] == 'AAPL']['combined_score'].iloc[0]
        assert abs(aapl_score - 0.42) < 1e-6
    
    def test_combine_signals_empty_data(self):
        """Test signal combination with empty data."""
        empty_scores = pd.DataFrame()
        signal_weights = {'RSI': 0.6, 'SMA': 0.4}
        
        combined = self.calculator.combine_signals(empty_scores, signal_weights)
        
        assert combined.empty
    
    def test_combine_signals_zero_weights(self):
        """Test signal combination with zero weights."""
        signal_scores = pd.DataFrame([
            {'ticker': 'AAPL', 'date': date(2024, 1, 15), 'signal_id': 'RSI', 'score': 0.5},
        ])
        
        signal_weights = {'RSI': 0.0, 'SMA': 0.0}
        
        combined = self.calculator.combine_signals(signal_scores, signal_weights)
        
        assert combined.empty


if __name__ == '__main__':
    pytest.main([__file__])
