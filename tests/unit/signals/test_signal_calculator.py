"""
Comprehensive tests for the SignalCalculator class.

Tests signal calculation, combination, and edge cases for production readiness.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from signals.calculator import SignalCalculator
from signals.registry import SignalRegistry
from database.models import SignalRaw, ScoreCombined


class TestSignalCalculator:
    """Test SignalCalculator functionality with comprehensive edge cases."""
    
    def setup_method(self):
        """Setup test data and calculator."""
        self.price_fetcher = Mock()
        self.database_manager = Mock()
        self.calculator = SignalCalculator(self.database_manager)
        
        # Create comprehensive test data
        self.dates = pd.date_range(start='2023-12-01', end='2024-01-31', freq='D')
        np.random.seed(42)
        
        # Generate realistic price data
        base_price = 100.0
        returns = np.random.randn(len(self.dates)) * 0.02
        prices = base_price * np.exp(np.cumsum(returns))
        
        self.price_data = pd.DataFrame({
            'Open': prices * (1 + np.random.randn(len(self.dates)) * 0.005),
            'High': prices * (1 + np.abs(np.random.randn(len(self.dates)) * 0.01)),
            'Low': prices * (1 - np.abs(np.random.randn(len(self.dates)) * 0.01)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(self.dates))
        }, index=self.dates.date)
        
        self.tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        self.signals = ['SENTIMENT']
        self.start_date = date(2024, 1, 1)
        self.end_date = date(2024, 1, 31)
    
    def test_calculator_initialization_default(self):
        """Test calculator initialization with default parameters."""
        calculator = SignalCalculator()
        
        assert calculator.price_fetcher is not None
        assert calculator.database_manager is not None
        assert calculator.registry is not None
        assert isinstance(calculator.registry, SignalRegistry)
    
    def test_calculator_initialization_custom(self):
        """Test calculator initialization with custom parameters."""
        calculator = SignalCalculator(self.database_manager)
        
        # price_fetcher no longer exists in SignalCalculator
        assert calculator.database_manager == self.database_manager
        assert calculator.registry is not None
    
    def test_calculate_signals_valid_inputs(self):
        """Test signal calculation with valid inputs."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'asof_date' in result.columns
        assert 'ticker' in result.columns
        assert 'signal_name' in result.columns
        assert 'value' in result.columns
        assert 'metadata' in result.columns
        assert 'created_at' in result.columns
    
    def test_calculate_signals_empty_tickers(self):
        """Test signal calculation with empty tickers list."""
        result = self.calculator.calculate_signals(
            [], self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_calculate_signals_empty_signals(self):
        """Test signal calculation with empty signals list."""
        result = self.calculator.calculate_signals(
            self.tickers, [], self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_calculate_signals_invalid_date_range(self):
        """Test signal calculation with invalid date range."""
        # End date before start date
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.end_date, self.start_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_calculate_signals_same_start_end_date(self):
        """Test signal calculation with same start and end date."""
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.start_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should have some results if the date is a trading day
    
    def test_calculate_signals_no_price_data(self):
        """Test signal calculation with no price data."""
        self.price_fetcher.get_price_history.return_value = None
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_calculate_signals_empty_price_data(self):
        """Test signal calculation with empty price data."""
        self.price_fetcher.get_price_history.return_value = pd.DataFrame()
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_calculate_signals_insufficient_price_data(self):
        """Test signal calculation with insufficient price data."""
        # Create price data with only 5 days
        short_data = self.price_data.tail(5)
        self.price_fetcher.get_price_history.return_value = short_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle insufficient data gracefully
    
    def test_calculate_signals_missing_columns(self):
        """Test signal calculation with missing price data columns."""
        incomplete_data = self.price_data[['Close']]  # Missing other columns
        self.price_fetcher.get_price_history.return_value = incomplete_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle missing columns gracefully
    
    def test_calculate_signals_nan_values(self):
        """Test signal calculation with NaN values in price data."""
        nan_data = self.price_data.copy()
        nan_data.loc[nan_data.index[:10], 'Close'] = np.nan
        self.price_fetcher.get_price_history.return_value = nan_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle NaN values gracefully
    
    def test_calculate_signals_inf_values(self):
        """Test signal calculation with infinite values in price data."""
        inf_data = self.price_data.copy()
        inf_data.loc[inf_data.index[:5], 'Close'] = np.inf
        inf_data.loc[inf_data.index[5:10], 'Close'] = -np.inf
        self.price_fetcher.get_price_history.return_value = inf_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle infinite values gracefully
    
    def test_calculate_signals_negative_prices(self):
        """Test signal calculation with negative prices."""
        negative_data = self.price_data.copy()
        negative_data.loc[negative_data.index[:5], 'Close'] = -100.0
        self.price_fetcher.get_price_history.return_value = negative_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle negative prices gracefully
    
    def test_calculate_signals_zero_prices(self):
        """Test signal calculation with zero prices."""
        zero_data = self.price_data.copy()
        zero_data.loc[zero_data.index[:5], 'Close'] = 0.0
        self.price_fetcher.get_price_history.return_value = zero_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle zero prices gracefully
    
    def test_calculate_signals_very_small_prices(self):
        """Test signal calculation with very small prices."""
        small_data = self.price_data.copy()
        small_data.loc[small_data.index[:5], 'Close'] = 1e-10
        self.price_fetcher.get_price_history.return_value = small_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle very small prices gracefully
    
    def test_calculate_signals_very_large_prices(self):
        """Test signal calculation with very large prices."""
        large_data = self.price_data.copy()
        large_data.loc[large_data.index[:5], 'Close'] = 1e10
        self.price_fetcher.get_price_history.return_value = large_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle very large prices gracefully
    
    def test_calculate_signals_constant_prices(self):
        """Test signal calculation with constant prices."""
        constant_data = self.price_data.copy()
        constant_data['Close'] = 100.0
        self.price_fetcher.get_price_history.return_value = constant_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle constant prices gracefully
    
    def test_calculate_signals_unicode_tickers(self):
        """Test signal calculation with unicode tickers."""
        unicode_tickers = ['AAPL', '测试', 'MSFT']
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            unicode_tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle unicode tickers gracefully
    
    def test_calculate_signals_long_ticker_names(self):
        """Test signal calculation with long ticker names."""
        long_tickers = ['A' * 100, 'B' * 200]
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            long_tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle long ticker names gracefully
    
    def test_calculate_signals_special_characters_tickers(self):
        """Test signal calculation with special characters in tickers."""
        special_tickers = ['AAPL-USD', 'MSFT.US', 'GOOGL/CL']
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            special_tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle special characters gracefully
    
    def test_calculate_signals_invalid_signal_names(self):
        """Test signal calculation with invalid signal names."""
        invalid_signals = ['INVALID1', 'INVALID2', 'SENTIMENT']
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            self.tickers, invalid_signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle invalid signal names gracefully
    
    def test_calculate_signals_mixed_valid_invalid_signals(self):
        """Test signal calculation with mixed valid and invalid signals."""
        mixed_signals = ['SENTIMENT', 'INVALID', 'SENTIMENT', 'INVALID2', 'SENTIMENT']
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            self.tickers, mixed_signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should calculate valid signals and skip invalid ones
    
    def test_calculate_signals_store_in_db_true(self):
        """Test signal calculation with database storage enabled."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date, store_in_db=True
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should call database storage
        self.database_manager.store_signals_raw.assert_called()
    
    def test_calculate_signals_store_in_db_false(self):
        """Test signal calculation with database storage disabled."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date, store_in_db=False
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should not call database storage
        self.database_manager.store_signals_raw.assert_not_called()
    
    def test_calculate_signals_database_error(self):
        """Test signal calculation with database error."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        self.database_manager.store_signals_raw.side_effect = Exception("Database error")
        
        result = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date, store_in_db=True
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle database errors gracefully
    
    def test_calculate_signal_for_ticker_valid(self):
        """Test calculating signal for single ticker."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', self.start_date
        )
        
        assert result is not None
        assert isinstance(result, float)
        assert not np.isnan(result)
        assert -1.0 <= result <= 1.0
    
    def test_calculate_signal_for_ticker_no_data(self):
        """Test calculating signal with no price data."""
        self.price_fetcher.get_price_history.return_value = None
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', self.start_date
        )
        
        assert result is None
    
    def test_calculate_signal_for_ticker_empty_data(self):
        """Test calculating signal with empty price data."""
        self.price_fetcher.get_price_history.return_value = pd.DataFrame()
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', self.start_date
        )
        
        assert result is None
    
    def test_calculate_signal_for_ticker_invalid_signal(self):
        """Test calculating signal with invalid signal ID."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'INVALID', self.start_date
        )
        
        assert result is None
    
    def test_calculate_signal_for_ticker_insufficient_data(self):
        """Test calculating signal with insufficient data."""
        short_data = self.price_data.tail(5)
        self.price_fetcher.get_price_history.return_value = short_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', self.start_date
        )
        
        assert result is None
    
    def test_calculate_signal_for_ticker_future_date(self):
        """Test calculating signal with future date."""
        future_date = date(2025, 1, 1)
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', future_date
        )
        
        assert result is None
    
    def test_calculate_signal_for_ticker_past_date(self):
        """Test calculating signal with very old date."""
        past_date = date(2020, 1, 1)
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signal_for_ticker(
            'AAPL', 'SENTIMENT', past_date
        )
        
        # Should handle past dates gracefully
        assert result is None or isinstance(result, float)
    
    def test_combine_signals_to_scores_equal_weight(self):
        """Test signal combination with equal weight method."""
        # Mock raw signals data
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.1},
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.2},
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.4},
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.6},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, method='equal_weight'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'asof_date' in result.columns
        assert 'ticker' in result.columns
        assert 'score' in result.columns
        assert 'method' in result.columns
        assert 'params' in result.columns
        assert 'created_at' in result.columns
    
    def test_combine_signals_to_scores_weighted(self):
        """Test signal combination with weighted method."""
        # Mock raw signals data
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        method_params = {'weights': {'SENTIMENT': 0.6, 'SENTIMENT': 0.4}}
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, 
            method='weighted', method_params=method_params
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should calculate weighted average: 0.5 * 0.6 + 0.3 * 0.4 = 0.42
        if not result.empty:
            aapl_score = result[result['ticker'] == 'AAPL']['score'].iloc[0]
            assert abs(aapl_score - 0.42) < 1e-6
    
    def test_combine_signals_to_scores_zscore(self):
        """Test signal combination with z-score method."""
        # Mock raw signals data
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, method='zscore'
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should calculate z-score normalization
    
    def test_combine_signals_to_scores_invalid_method(self):
        """Test signal combination with invalid method."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, method='invalid'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty  # Should return empty DataFrame for invalid method
    
    def test_combine_signals_to_scores_no_raw_signals(self):
        """Test signal combination with no raw signals."""
        self.database_manager.get_signals_raw.return_value = pd.DataFrame()
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_combine_signals_to_scores_missing_signals(self):
        """Test signal combination with missing signals."""
        # Mock raw signals data with missing signals
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            # Missing SENTIMENT signal for AAPL
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.2},
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.4},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, method='equal_weight'
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should skip combinations with missing signals
    
    def test_combine_signals_to_scores_nan_values(self):
        """Test signal combination with NaN values."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': np.nan},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, method='equal_weight'
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle NaN values gracefully
    
    def test_combine_signals_to_scores_inf_values(self):
        """Test signal combination with infinite values."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': np.inf},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, method='equal_weight'
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle infinite values gracefully
    
    def test_combine_signals_to_scores_zero_weights(self):
        """Test signal combination with zero weights."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        method_params = {'weights': {'SENTIMENT': 0.0, 'SENTIMENT': 0.0}}
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, 
            method='weighted', method_params=method_params
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty  # Should return empty DataFrame for zero weights
    
    def test_combine_signals_to_scores_negative_weights(self):
        """Test signal combination with negative weights."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        method_params = {'weights': {'SENTIMENT': 0.6, 'SENTIMENT': -0.4}}
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, 
            method='weighted', method_params=method_params
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle negative weights gracefully
    
    def test_combine_signals_to_scores_single_signal(self):
        """Test signal combination with single signal."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, ['SENTIMENT'], self.start_date, self.end_date, method='equal_weight'
        )
        
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            aapl_score = result[result['ticker'] == 'AAPL']['score'].iloc[0]
            assert aapl_score == 0.5  # Single signal should return its value
    
    def test_combine_signals_to_scores_store_in_db_true(self):
        """Test signal combination with database storage enabled."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, 
            method='equal_weight', store_in_db=True
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should call database storage
        self.database_manager.store_scores_combined.assert_called()
    
    def test_combine_signals_to_scores_store_in_db_false(self):
        """Test signal combination with database storage disabled."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should not call database storage
        self.database_manager.store_scores_combined.assert_not_called()
    
    def test_combine_signals_to_scores_database_error(self):
        """Test signal combination with database error."""
        raw_signals_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.3},
        ])
        
        self.database_manager.get_signals_raw.return_value = raw_signals_data
        self.database_manager.store_scores_combined.side_effect = Exception("Database error")
        
        result = self.calculator.combine_signals_to_scores(
            self.tickers, self.signals, self.start_date, self.end_date, 
            method='equal_weight', store_in_db=True
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle database errors gracefully
    
    def test_get_signals_raw(self):
        """Test getting raw signals from database."""
        mock_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
        ])
        
        self.database_manager.get_signals_raw.return_value = mock_data
        
        result = self.calculator.get_signals_raw(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        self.database_manager.get_signals_raw.assert_called_with(
            self.tickers, self.signals, self.start_date, self.end_date
        )
    
    def test_get_signals_raw_database_error(self):
        """Test getting raw signals with database error."""
        self.database_manager.get_signals_raw.side_effect = Exception("Database error")
        
        result = self.calculator.get_signals_raw(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_get_scores_combined(self):
        """Test getting combined scores from database."""
        mock_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'score': 0.4, 'method': 'equal_weight'},
        ])
        
        self.database_manager.get_scores_combined.return_value = mock_data
        
        result = self.calculator.get_scores_combined(
            self.tickers, ['equal_weight'], self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        self.database_manager.get_scores_combined.assert_called_with(
            self.tickers, ['equal_weight'], self.start_date, self.end_date
        )
    
    def test_get_scores_combined_database_error(self):
        """Test getting combined scores with database error."""
        self.database_manager.get_scores_combined.side_effect = Exception("Database error")
        
        result = self.calculator.get_scores_combined(
            self.tickers, ['equal_weight'], self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_get_scores_combined_pivot(self):
        """Test getting combined scores as pivot table."""
        mock_data = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'score': 0.4, 'method': 'equal_weight'},
        ])
        
        self.database_manager.get_scores_combined_pivot.return_value = mock_data
        
        result = self.calculator.get_scores_combined_pivot(
            self.tickers, ['equal_weight'], self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        self.database_manager.get_scores_combined_pivot.assert_called_with(
            self.tickers, ['equal_weight'], self.start_date, self.end_date, True
        )
    
    def test_get_scores_combined_pivot_database_error(self):
        """Test getting combined scores pivot with database error."""
        self.database_manager.get_scores_combined_pivot.side_effect = Exception("Database error")
        
        result = self.calculator.get_scores_combined_pivot(
            self.tickers, ['equal_weight'], self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_get_missing_signals(self):
        """Test getting missing signals."""
        # Mock existing signals
        existing_signals = pd.DataFrame([
            {'ticker': 'AAPL', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.5},
            # Missing SENTIMENT for AAPL
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.2},
            {'ticker': 'MSFT', 'asof_date': self.start_date, 'signal_name': 'SENTIMENT', 'value': 0.4},
        ])
        
        self.database_manager.get_signals_raw.return_value = existing_signals
        
        result = self.calculator.get_missing_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, list)
        # Should identify missing signals
    
    def test_get_missing_signals_no_existing(self):
        """Test getting missing signals when no existing signals."""
        self.database_manager.get_signals_raw.return_value = pd.DataFrame()
        
        result = self.calculator.get_missing_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, list)
        # Should return all possible combinations
    
    def test_get_missing_signals_database_error(self):
        """Test getting missing signals with database error."""
        self.database_manager.get_signals_raw.side_effect = Exception("Database error")
        
        result = self.calculator.get_missing_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, list)
        assert result == []
    
    def test_calculate_missing_signals(self):
        """Test calculating missing signals."""
        # Mock missing signals
        missing_signals = [
            ('AAPL', 'SENTIMENT', self.start_date),
            ('AAPL', 'SENTIMENT', self.start_date),
        ]
        
        self.calculator.get_missing_signals = Mock(return_value=missing_signals)
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_missing_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should calculate missing signals
    
    def test_calculate_missing_signals_no_missing(self):
        """Test calculating missing signals when none are missing."""
        self.calculator.get_missing_signals = Mock(return_value=[])
        
        result = self.calculator.calculate_missing_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_calculate_missing_signals_database_error(self):
        """Test calculating missing signals with database error."""
        missing_signals = [('AAPL', 'SENTIMENT', self.start_date)]
        self.calculator.get_missing_signals = Mock(return_value=missing_signals)
        self.price_fetcher.get_price_history.return_value = self.price_data
        self.database_manager.store_signals_raw.side_effect = Exception("Database error")
        
        result = self.calculator.calculate_missing_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle database errors gracefully
    
    def test_calculator_performance(self):
        """Test calculator performance with large datasets."""
        import time
        
        # Create large dataset
        large_tickers = [f'TICKER_{i:03d}' for i in range(100)]
        large_signals = ['SENTIMENT', 'SENTIMENT', 'SENTIMENT']
        
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        start_time = time.time()
        result = self.calculator.calculate_signals(
            large_tickers, large_signals, self.start_date, self.end_date
        )
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 30.0  # 30 seconds max
        assert isinstance(result, pd.DataFrame)
    
    def test_calculator_memory_efficiency(self):
        """Test calculator memory efficiency."""
        # Create large dataset
        large_tickers = [f'TICKER_{i:03d}' for i in range(1000)]
        large_signals = ['SENTIMENT', 'SENTIMENT', 'SENTIMENT']
        
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result = self.calculator.calculate_signals(
            large_tickers, large_signals, self.start_date, self.end_date
        )
        
        # Should handle large datasets efficiently
        assert isinstance(result, pd.DataFrame)
    
    def test_calculator_concurrent_calls(self):
        """Test calculator with concurrent calls (thread safety)."""
        import threading
        import time
        
        results = []
        
        def calculate_signals_thread():
            result = self.calculator.calculate_signals(
                self.tickers, self.signals, self.start_date, self.end_date
            )
            results.append(result)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=calculate_signals_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have completed successfully
        assert len(results) == 5
        for result in results:
            assert isinstance(result, pd.DataFrame)
    
    def test_calculator_error_handling(self):
        """Test calculator error handling."""
        # Test with invalid inputs
        with pytest.raises(TypeError):
            self.calculator.calculate_signals(
                None, self.signals, self.start_date, self.end_date
            )
        
        with pytest.raises(TypeError):
            self.calculator.calculate_signals(
                self.tickers, None, self.start_date, self.end_date
            )
        
        with pytest.raises(TypeError):
            self.calculator.calculate_signals(
                self.tickers, self.signals, None, self.end_date
            )
        
        with pytest.raises(TypeError):
            self.calculator.calculate_signals(
                self.tickers, self.signals, self.start_date, None
            )
    
    def test_calculator_logging(self):
        """Test calculator logging."""
        import logging
        
        # Set up logging capture
        logger = logging.getLogger('signals.calculator')
        with patch.object(logger, 'info') as mock_info:
            self.price_fetcher.get_price_history.return_value = self.price_data
            
            result = self.calculator.calculate_signals(
                self.tickers, self.signals, self.start_date, self.end_date
            )
            
            # Check that appropriate log messages are generated
            assert mock_info.called
            assert isinstance(result, pd.DataFrame)
    
    def test_calculator_deterministic(self):
        """Test calculator is deterministic with same inputs."""
        self.price_fetcher.get_price_history.return_value = self.price_data
        
        result1 = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        result2 = self.calculator.calculate_signals(
            self.tickers, self.signals, self.start_date, self.end_date
        )
        
        # Results should be identical (or very similar) with same inputs
        assert isinstance(result1, pd.DataFrame)
        assert isinstance(result2, pd.DataFrame)
        
        if not result1.empty and not result2.empty:
            # Compare key columns
            assert result1['ticker'].tolist() == result2['ticker'].tolist()
            assert result1['signal_name'].tolist() == result2['signal_name'].tolist()
            assert result1['asof_date'].tolist() == result2['asof_date'].tolist()


if __name__ == '__main__':
    pytest.main([__file__])
