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

from signals import SentimentSignal, SignalReader
from signals.registry import SignalRegistry


class TestSentimentSignal:
    """Test Sentiment signal implementation."""
    
    def setup_method(self):
        """Setup test data."""
        self.signal = SentimentSignal()
        self.ticker = 'AAPL'
        self.target_date = date(2024, 1, 15)
        
        # Create mock price data (sentiment doesn't need price data)
        dates = pd.date_range(start='2023-12-01', end='2024-01-15', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
        
        self.price_data = pd.DataFrame({
            'Close': prices
        }, index=dates.date)
    
    def test_sentiment_initialization(self):
        """Test Sentiment signal initialization."""
        assert self.signal.signal_id == 'SENTIMENT'
        assert self.signal.name == 'Sentiment Signal'
        assert self.signal.get_min_lookback_period() == 0  # Sentiment doesn't need price data
        assert self.signal.get_max_lookback_period() == 0  # Sentiment doesn't need price data
    
    def test_sentiment_calculation_valid_data(self):
        """Test Sentiment calculation with valid data."""
        result = self.signal.calculate(None, self.ticker, self.target_date)
        
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_sentiment_calculation_insufficient_data(self):
        """Test Sentiment calculation with insufficient data."""
        # Sentiment signal doesn't use price data, so insufficient data doesn't matter
        result = self.signal.calculate(None, self.ticker, self.target_date)
        
        # Sentiment signal should work regardless of price data
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_sentiment_calculation_missing_date(self):
        """Test Sentiment calculation with missing target date."""
        # Sentiment signal doesn't use price data, so missing dates don't matter
        result = self.signal.calculate(None, self.ticker, self.target_date)
        
        # Should still work since sentiment doesn't depend on price data
        assert not np.isnan(result)
    
    def test_sentiment_calculation_empty_data(self):
        """Test Sentiment calculation with empty data."""
        # Sentiment signal doesn't use price data, so empty data doesn't matter
        result = self.signal.calculate(None, self.ticker, self.target_date)
        
        # Should still work since sentiment doesn't depend on price data
        assert not np.isnan(result)
    
    def test_sentiment_calculation_none_data(self):
        """Test Sentiment calculation with None data."""
        result = self.signal.calculate(None, self.ticker, self.target_date)
        
        # Sentiment signal should work even with None data
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_sentiment_validation(self):
        """Test Sentiment data validation."""
        # Sentiment signals always return True for validation since they don't use price data
        assert self.signal.validate_price_data(None, self.target_date)
        assert self.signal.validate_price_data(self.price_data, self.target_date)
        
        # Even with insufficient or missing data, validation should pass
        short_data = self.price_data.tail(10)
        assert self.signal.validate_price_data(short_data, self.target_date)
        
        data_without_date = self.price_data[self.price_data.index != self.target_date]
        assert self.signal.validate_price_data(data_without_date, self.target_date)
    
    def test_sentiment_get_required_data_range(self):
        """Test Sentiment required data range calculation."""
        # Sentiment signals don't require price data, so this should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            self.signal.get_required_price_data(self.target_date)


class TestSignalRegistry:
    """Test signal registry functionality."""
    
    def setup_method(self):
        """Setup test registry."""
        self.registry = SignalRegistry()
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        assert len(self.registry) > 0
        assert 'SENTIMENT' in self.registry
        assert 'SENTIMENT_YT' in self.registry
    
    def test_get_signal(self):
        """Test getting signal from registry."""
        signal = self.registry.get_signal('SENTIMENT')
        assert signal is not None
        assert signal.signal_id == 'SENTIMENT'
        
        signal = self.registry.get_signal('SENTIMENT_YT', seed=42)
        assert signal is not None
        assert signal.signal_id == 'SENTIMENT_YT'
    
    def test_get_nonexistent_signal(self):
        """Test getting nonexistent signal."""
        signal = self.registry.get_signal('NONEXISTENT')
        assert signal is None
    
    def test_get_available_signals(self):
        """Test getting available signals."""
        signals = self.registry.get_available_signals()
        assert 'SENTIMENT' in signals
        assert 'SENTIMENT_YT' in signals
    
    def test_get_signal_info(self):
        """Test getting signal information."""
        info = self.registry.get_signal_info('SENTIMENT')
        assert info is not None
        assert info['signal_id'] == 'SENTIMENT'
        assert info['name'] == 'Sentiment Signal'
        assert 'parameters' in info
        assert 'min_lookback' in info
        assert 'max_lookback' in info
        assert info['min_lookback'] == 0
        assert info['max_lookback'] == 0
    
    def test_get_nonexistent_signal_info(self):
        """Test getting information for nonexistent signal."""
        info = self.registry.get_signal_info('NONEXISTENT')
        assert info is None


class TestSignalReader:
    """Test signal calculator functionality."""
    
    def setup_method(self):
        """Setup test calculator."""
        self.price_fetcher = Mock()
        self.database_manager = Mock()
        self.reader = SignalReader(self.database_manager)
        
        # Mock price data
        dates = pd.date_range(start='2023-12-01', end='2024-01-15', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
        
        self.price_data = pd.DataFrame({
            'Close': prices
        }, index=dates.date)
    
    def test_calculator_initialization(self):
        """Test calculator initialization."""
        assert self.calculator.database_manager is not None
        assert self.calculator.registry is not None
    
    def test_calculate_signal_for_ticker(self):
        """Test calculating signal for single ticker."""
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', date(2024, 1, 15)
        )
        
        assert result is not None
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_calculate_signal_for_ticker_no_data(self):
        """Test calculating signal with no price data."""
        # Sentiment signals don't need price data, so this should still work
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', date(2024, 1, 15)
        )
        
        assert result is not None
        assert not np.isnan(result)
    
    def test_calculate_signal_for_ticker_invalid_signal(self):
        """Test calculating signal with invalid signal ID."""
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'INVALID', date(2024, 1, 15)
        )
        
        assert result is None
    
    def test_combine_signals(self):
        """Test signal combination."""
        # Create mock signal scores
        signal_scores = pd.DataFrame([
            {'ticker': 'AAPL', 'date': date(2024, 1, 15), 'signal_id': 'SENTIMENT', 'score': 0.5},
            {'ticker': 'AAPL', 'date': date(2024, 1, 15), 'signal_id': 'SENTIMENT_YT', 'score': 0.3},
            {'ticker': 'MSFT', 'date': date(2024, 1, 15), 'signal_id': 'SENTIMENT', 'score': 0.2},
            {'ticker': 'MSFT', 'date': date(2024, 1, 15), 'signal_id': 'SENTIMENT_YT', 'score': 0.4},
        ])
        
        signal_weights = {'SENTIMENT': 0.6, 'SENTIMENT_YT': 0.4}
        
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
        signal_weights = {'SENTIMENT': 0.6, 'SENTIMENT_YT': 0.4}
        
        combined = self.calculator.combine_signals(empty_scores, signal_weights)
        
        assert combined.empty
    
    def test_combine_signals_zero_weights(self):
        """Test signal combination with zero weights."""
        signal_scores = pd.DataFrame([
            {'ticker': 'AAPL', 'date': date(2024, 1, 15), 'signal_id': 'SENTIMENT', 'score': 0.5},
        ])
        
        signal_weights = {'SENTIMENT': 0.0, 'SENTIMENT_YT': 0.0}
        
        combined = self.calculator.combine_signals(signal_scores, signal_weights)
        
        assert combined.empty


if __name__ == '__main__':
    pytest.main([__file__])
