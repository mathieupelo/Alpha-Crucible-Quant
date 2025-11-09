"""
Tests for signal combination with NULL value exclusion.

These tests verify that when combining signals:
- NULL values are excluded
- Remaining signals are averaged equally (no reweighting)
- Examples:
  - A:0.2, B:0.6, C:0.8 → (0.2+0.6+0.8)/3 = 0.533...
  - A:Null, B:0.6, C:0.8 → (0.6+0.8)/2 = 0.7
  - A:Null, B:Null, C:0.8 → 0.8/1 = 0.8
"""

import pytest
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta

# Add project root, backend and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))
sys.path.insert(0, str(project_root / 'src'))

from src.backtest.engine import BacktestEngine
from src.backtest.config import BacktestConfig
from services.database_service import DatabaseService

# Test signal names used in tests
TEST_SIGNAL_NAMES = ['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']


@pytest.fixture(autouse=True)
def cleanup_test_signals():
    """Clean up test signals from database before and after each test."""
    db_service = DatabaseService()
    if not db_service.ensure_connection():
        yield
        return
    
    db_manager = db_service.db_manager
    
    # Clean up before test (in case previous test failed)
    for signal_name in TEST_SIGNAL_NAMES:
        try:
            # Delete signal_raw records for this signal
            signal = db_manager.get_signal_by_name(signal_name)
            if signal:
                signal_id = signal.id
                # Delete from signal_raw table
                db_manager.execute_query(
                    "DELETE FROM signal_raw WHERE signal_id = %s",
                    (signal_id,)
                )
                # Delete the signal definition
                db_manager.execute_query(
                    "DELETE FROM signals WHERE id = %s",
                    (signal_id,)
                )
        except Exception as e:
            # Ignore errors during cleanup
            pass
    
    yield
    
    # Clean up after test
    if db_service.ensure_connection():
        for signal_name in TEST_SIGNAL_NAMES:
            try:
                # Delete signal_raw records for this signal
                signal = db_manager.get_signal_by_name(signal_name)
                if signal:
                    signal_id = signal.id
                    # Delete from signal_raw table
                    db_manager.execute_query(
                        "DELETE FROM signal_raw WHERE signal_id = %s",
                        (signal_id,)
                    )
                    # Delete the signal definition
                    db_manager.execute_query(
                        "DELETE FROM signals WHERE id = %s",
                        (signal_id,)
                    )
            except Exception as e:
                # Ignore errors during cleanup
                pass


def test_equal_weight_combination_all_signals_present():
    """Test equal weight combination when all signals are present."""
    engine = BacktestEngine()
    
    # Create test data: A:0.2, B:0.6, C:0.8
    test_date = date.today() - timedelta(days=1)
    raw_signals = pd.DataFrame({
        'asof_date': [test_date] * 3,
        'ticker': ['TEST'] * 3,
        'signal_name': ['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        'value': [0.2, 0.6, 0.8]
    })
    
    config = BacktestConfig(
        start_date=test_date,
        end_date=test_date + timedelta(days=1),
        universe_id=1,
        signal_combination_method='equal_weight',
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']
    )
    
    result = engine._combine_signals_to_scores(
        raw_signals=raw_signals,
        tickers=['TEST'],
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        config=config
    )
    
    assert not result.empty, "Should have combined score"
    assert len(result) == 1, "Should have one combined score"
    
    combined_score = result.iloc[0]['score']
    expected = (0.2 + 0.6 + 0.8) / 3  # 0.533...
    
    assert abs(combined_score - expected) < 0.001, \
        f"Expected {expected}, got {combined_score}"


def test_equal_weight_combination_one_null():
    """Test equal weight combination when one signal is NULL."""
    engine = BacktestEngine()
    
    # Create test data: A:Null, B:0.6, C:0.8
    test_date = date.today() - timedelta(days=1)
    raw_signals = pd.DataFrame({
        'asof_date': [test_date] * 3,
        'ticker': ['TEST'] * 3,
        'signal_name': ['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        'value': [np.nan, 0.6, 0.8]  # A is NULL
    })
    
    config = BacktestConfig(
        start_date=test_date,
        end_date=test_date + timedelta(days=1),
        universe_id=1,
        signal_combination_method='equal_weight',
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']
    )
    
    result = engine._combine_signals_to_scores(
        raw_signals=raw_signals,
        tickers=['TEST'],
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        config=config
    )
    
    assert not result.empty, "Should have combined score even with one NULL"
    assert len(result) == 1, "Should have one combined score"
    
    combined_score = result.iloc[0]['score']
    expected = (0.6 + 0.8) / 2  # 0.7
    
    assert abs(combined_score - expected) < 0.001, \
        f"Expected {expected}, got {combined_score}"


def test_equal_weight_combination_two_null():
    """Test equal weight combination when two signals are NULL."""
    engine = BacktestEngine()
    
    # Create test data: A:Null, B:Null, C:0.8
    test_date = date.today() - timedelta(days=1)
    raw_signals = pd.DataFrame({
        'asof_date': [test_date] * 3,
        'ticker': ['TEST'] * 3,
        'signal_name': ['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        'value': [np.nan, np.nan, 0.8]  # A and B are NULL
    })
    
    config = BacktestConfig(
        start_date=test_date,
        end_date=test_date + timedelta(days=1),
        universe_id=1,
        signal_combination_method='equal_weight',
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']
    )
    
    result = engine._combine_signals_to_scores(
        raw_signals=raw_signals,
        tickers=['TEST'],
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        config=config
    )
    
    assert not result.empty, "Should have combined score even with two NULL"
    assert len(result) == 1, "Should have one combined score"
    
    combined_score = result.iloc[0]['score']
    expected = 0.8  # Only C is available
    
    assert abs(combined_score - expected) < 0.001, \
        f"Expected {expected}, got {combined_score}"


def test_equal_weight_combination_all_null():
    """Test equal weight combination when all signals are NULL."""
    engine = BacktestEngine()
    
    # Create test data: A:Null, B:Null, C:Null
    test_date = date.today() - timedelta(days=1)
    raw_signals = pd.DataFrame({
        'asof_date': [test_date] * 3,
        'ticker': ['TEST'] * 3,
        'signal_name': ['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        'value': [np.nan, np.nan, np.nan]  # All NULL
    })
    
    config = BacktestConfig(
        start_date=test_date,
        end_date=test_date + timedelta(days=1),
        universe_id=1,
        signal_combination_method='equal_weight',
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']
    )
    
    result = engine._combine_signals_to_scores(
        raw_signals=raw_signals,
        tickers=['TEST'],
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        config=config
    )
    
    # Should return empty DataFrame when all signals are NULL
    assert result.empty, "Should return empty when all signals are NULL"


def test_equal_weight_combination_missing_signal_row():
    """Test equal weight combination when a signal row is completely missing (not just NULL value)."""
    engine = BacktestEngine()
    
    # Create test data: Only B and C present (A row is missing entirely)
    test_date = date.today() - timedelta(days=1)
    raw_signals = pd.DataFrame({
        'asof_date': [test_date] * 2,
        'ticker': ['TEST'] * 2,
        'signal_name': ['SIGNAL_B', 'SIGNAL_C'],
        'value': [0.6, 0.8]
    })
    
    config = BacktestConfig(
        start_date=test_date,
        end_date=test_date + timedelta(days=1),
        universe_id=1,
        signal_combination_method='equal_weight',
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']
    )
    
    result = engine._combine_signals_to_scores(
        raw_signals=raw_signals,
        tickers=['TEST'],
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        config=config
    )
    
    assert not result.empty, "Should have combined score even when signal row is missing"
    assert len(result) == 1, "Should have one combined score"
    
    combined_score = result.iloc[0]['score']
    expected = (0.6 + 0.8) / 2  # 0.7
    
    assert abs(combined_score - expected) < 0.001, \
        f"Expected {expected}, got {combined_score}"


def test_equal_weight_combination_multiple_tickers():
    """Test equal weight combination with multiple tickers, some with NULL signals."""
    engine = BacktestEngine()
    
    test_date = date.today() - timedelta(days=1)
    raw_signals = pd.DataFrame({
        'asof_date': [test_date] * 6,
        'ticker': ['TICKER1', 'TICKER1', 'TICKER1', 'TICKER2', 'TICKER2', 'TICKER2'],
        'signal_name': ['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'] * 2,
        'value': [0.2, 0.6, 0.8, np.nan, 0.6, 0.8]  # TICKER1: all present, TICKER2: A is NULL
    })
    
    config = BacktestConfig(
        start_date=test_date,
        end_date=test_date + timedelta(days=1),
        universe_id=1,
        signal_combination_method='equal_weight',
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C']
    )
    
    result = engine._combine_signals_to_scores(
        raw_signals=raw_signals,
        tickers=['TICKER1', 'TICKER2'],
        signals=['SIGNAL_A', 'SIGNAL_B', 'SIGNAL_C'],
        config=config
    )
    
    assert not result.empty, "Should have combined scores"
    assert len(result) == 2, "Should have two combined scores (one per ticker)"
    
    # Check TICKER1: all signals present
    ticker1_score = result[result['ticker'] == 'TICKER1'].iloc[0]['score']
    expected1 = (0.2 + 0.6 + 0.8) / 3
    assert abs(ticker1_score - expected1) < 0.001, \
        f"TICKER1: Expected {expected1}, got {ticker1_score}"
    
    # Check TICKER2: A is NULL
    ticker2_score = result[result['ticker'] == 'TICKER2'].iloc[0]['score']
    expected2 = (0.6 + 0.8) / 2
    assert abs(ticker2_score - expected2) < 0.001, \
        f"TICKER2: Expected {expected2}, got {ticker2_score}"

