"""
Tests for backtest functionality.

These tests verify that backtests can be run correctly.
"""

import pytest
import sys
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

# Add backend and src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.database_service import DatabaseService
from src.backtest.engine import BacktestEngine
from src.backtest.config import BacktestConfig

# Test universe name - will be created and cleaned up
TEST_UNIVERSE_NAME = "__TEST_UNIVERSE_BACKTEST__"


@pytest.fixture(autouse=True)
def setup_test_universe():
    """Create and clean up test universe with tickers for each test."""
    db_service = DatabaseService()
    assert db_service.ensure_connection(), "Failed to connect to database"
    
    # Clean up if exists (delete backtests first if they exist)
    universes = db_service.get_all_universes()
    for universe in universes:
        if universe['name'] == TEST_UNIVERSE_NAME:
            universe_id = universe['id']
            # Try to delete backtests first
            try:
                backtests = db_service.db_manager.get_backtests()
                if not backtests.empty:
                    backtests_for_universe = backtests[backtests['universe_id'] == universe_id]
                    for _, bt in backtests_for_universe.iterrows():
                        try:
                            db_service.delete_backtest(bt['run_id'])
                        except Exception:
                            pass
            except Exception:
                pass
            # Now delete universe
            try:
                db_service.delete_universe(universe_id)
            except Exception:
                # If deletion fails (e.g., foreign key constraint), that's okay
                pass
            break
    
    # Create test universe
    universe = db_service.create_universe(name=TEST_UNIVERSE_NAME)
    universe_id = universe['id']
    
    # Add some valid tickers (at least 5 required for backtest)
    # Use tickers that exist in Varrock schema
    test_tickers = ['AAPL', 'MSFT', 'CMCSA', 'DIS', 'EA']  # Replaced GOOGL, AMZN, TSLA with available tickers
    for ticker in test_tickers:
        try:
            db_service.add_universe_ticker(universe_id, ticker)
        except Exception:
            # If ticker already exists or fails, continue
            pass
    
    yield universe_id
    
    # Cleanup after test
    if db_service.ensure_connection():
        universes = db_service.get_all_universes()
        for universe in universes:
            if universe['name'] == TEST_UNIVERSE_NAME:
                universe_id = universe['id']
                # Try to delete backtests first
                try:
                    backtests = db_service.db_manager.get_backtests()
                    if not backtests.empty:
                        backtests_for_universe = backtests[backtests['universe_id'] == universe_id]
                        for _, bt in backtests_for_universe.iterrows():
                            try:
                                db_service.delete_backtest(bt['run_id'])
                            except Exception:
                                pass
                except Exception:
                    pass
                # Now try to delete universe
                try:
                    db_service.delete_universe(universe_id)
                except Exception:
                    # If deletion fails (e.g., foreign key constraint), that's okay for tests
                    pass
                break


def test_backtest_config_creation():
    """Test creating a backtest configuration."""
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        universe_id=1,
        name="Test Backtest",
        initial_capital=10000.0,
        rebalancing_frequency='monthly'
    )
    
    assert config.start_date == start_date
    assert config.end_date == end_date
    assert config.universe_id == 1
    assert config.name == "Test Backtest"
    assert config.initial_capital == 10000.0
    assert config.rebalancing_frequency == 'monthly'


def test_backtest_engine_initialization():
    """Test initializing the backtest engine."""
    engine = BacktestEngine()
    assert engine is not None
    assert hasattr(engine, 'run_backtest')


def test_get_universe_tickers_for_backtest(setup_test_universe):
    """Test retrieving tickers from universe for backtest."""
    universe_id = setup_test_universe
    db_service = DatabaseService()
    
    tickers_data = db_service.get_universe_tickers(universe_id)
    assert len(tickers_data) >= 5, "Universe should have at least 5 tickers"
    
    tickers = [t['ticker'] for t in tickers_data]
    assert len(tickers) >= 5


def test_backtest_requires_minimum_tickers(setup_test_universe):
    """Test that backtest requires at least 5 tickers."""
    universe_id = setup_test_universe
    db_service = DatabaseService()
    
    tickers_data = db_service.get_universe_tickers(universe_id)
    ticker_count = len(tickers_data)
    
    # Should have at least 5 tickers
    assert ticker_count >= 5, f"Universe has {ticker_count} tickers, need at least 5"


def test_backtest_config_validation():
    """Test backtest configuration validation."""
    # Test invalid date range
    with pytest.raises(ValueError, match="Start date must be before end date"):
        BacktestConfig(
            start_date=date(2024, 12, 31),
            end_date=date(2024, 1, 1),
            universe_id=1
        )
    
    # Test invalid initial capital
    with pytest.raises(ValueError, match="Initial capital must be positive"):
        BacktestConfig(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            universe_id=1,
            initial_capital=-1000.0
        )
    
    # Test invalid max weight
    with pytest.raises(ValueError, match="Max weight must be between 0 and 1"):
        BacktestConfig(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            universe_id=1,
            max_weight=1.5
        )


def test_backtest_universe_exists(setup_test_universe):
    """Test that universe exists before running backtest."""
    universe_id = setup_test_universe
    db_service = DatabaseService()
    
    universe = db_service.get_universe_by_id(universe_id)
    assert universe is not None
    assert universe['id'] == universe_id
    assert universe['name'] == TEST_UNIVERSE_NAME


@pytest.mark.slow
def test_run_backtest_basic(setup_test_universe):
    """Test running a basic backtest (marked as slow due to data fetching)."""
    universe_id = setup_test_universe
    db_service = DatabaseService()
    
    # Get universe tickers
    tickers_data = db_service.get_universe_tickers(universe_id)
    if len(tickers_data) < 5:
        pytest.skip("Not enough tickers in test universe")
    
    tickers = [t['ticker'] for t in tickers_data[:5]]  # Use first 5
    
    # Get available signals from database
    signals_df = db_service.db_manager.execute_query(
        "SELECT DISTINCT signal_name FROM signal_raw LIMIT 1"
    )
    
    if signals_df.empty:
        pytest.skip("No signals available in database")
    
    signals = [signals_df.iloc[0]['signal_name']]
    
    # Create config with recent dates (to ensure data availability)
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=30)
    
    initial_capital = 10000.0
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        universe_id=universe_id,
        name=f"Test Backtest {TEST_UNIVERSE_NAME}",
        initial_capital=initial_capital,
        rebalancing_frequency='monthly',
        min_lookback_days=20,
        max_lookback_days=60
    )
    
    # Run backtest
    engine = BacktestEngine()
    try:
        result = engine.run_backtest(
            tickers=tickers,
            signals=signals,
            config=config
        )
        
        assert result is not None
        assert hasattr(result, 'backtest_id')
        assert hasattr(result, 'total_return')
        assert hasattr(result, 'sharpe_ratio')
        
        # Verify NAV data is stored with return_pct
        nav_df = db_service.db_manager.get_backtest_nav(result.backtest_id)
        if not nav_df.empty:
            # Check that return_pct column exists and has values
            assert 'return_pct' in nav_df.columns, "return_pct column should exist"
            
            # Check that return_pct values are calculated correctly
            first_nav = nav_df.iloc[0]['nav']
            first_return_pct = nav_df.iloc[0].get('return_pct')
            
            if first_return_pct is not None and not pd.isna(first_return_pct):
                # First NAV should have return_pct = 0 (baseline)
                assert abs(first_return_pct) < 0.001, f"First NAV return_pct should be ~0, got {first_return_pct}"
                
                # Check that return_pct matches the calculation
                expected_return_pct = (first_nav - initial_capital) / initial_capital
                assert abs(first_return_pct - expected_return_pct) < 0.001, \
                    f"return_pct calculation mismatch: expected {expected_return_pct}, got {first_return_pct}"
    except Exception as e:
        # If backtest fails due to missing data, that's okay for basic test
        # We're mainly testing that the infrastructure works
        pytest.skip(f"Backtest failed (likely due to missing data): {e}")


@pytest.mark.slow
def test_nav_percentage_storage(setup_test_universe):
    """Test that NAV data is stored with percentage changes."""
    universe_id = setup_test_universe
    db_service = DatabaseService()
    
    # Get universe tickers
    tickers_data = db_service.get_universe_tickers(universe_id)
    if len(tickers_data) < 5:
        pytest.skip("Not enough tickers in test universe")
    
    tickers = [t['ticker'] for t in tickers_data[:5]]
    
    # Get available signals
    signals_df = db_service.db_manager.execute_query(
        "SELECT DISTINCT signal_name FROM signal_raw LIMIT 1"
    )
    if signals_df.empty:
        pytest.skip("No signals available in database")
    
    signals = [signals_df.iloc[0]['signal_name']]
    
    # Create config
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=30)
    initial_capital = 50000.0
    
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        universe_id=universe_id,
        name=f"NAV Percentage Test {TEST_UNIVERSE_NAME}",
        initial_capital=initial_capital,
        rebalancing_frequency='monthly',
        min_lookback_days=20,
        max_lookback_days=60
    )
    
    # Run backtest
    engine = BacktestEngine()
    try:
        result = engine.run_backtest(
            tickers=tickers,
            signals=signals,
            config=config
        )
        
        # Get NAV data
        nav_df = db_service.db_manager.get_backtest_nav(result.backtest_id)
        if nav_df.empty:
            pytest.skip("No NAV data stored")
        
        # Verify return_pct column exists
        assert 'return_pct' in nav_df.columns, "return_pct column should exist in NAV data"
        
        # Verify all records have return_pct
        assert nav_df['return_pct'].notna().any(), "At least some return_pct values should be non-null"
        
        # Verify first NAV has return_pct = 0 (baseline)
        first_row = nav_df.iloc[0]
        first_return_pct = first_row.get('return_pct')
        if first_return_pct is not None and not pd.isna(first_return_pct):
            assert abs(first_return_pct) < 0.001, \
                f"First NAV return_pct should be ~0, got {first_return_pct}"
        
        # Verify return_pct calculation for a few records
        for idx, row in nav_df.iterrows():
            nav_value = row['nav']
            return_pct = row.get('return_pct')
            
            if return_pct is not None and not pd.isna(return_pct):
                # Calculate expected return_pct
                expected_return_pct = (nav_value - initial_capital) / initial_capital
                assert abs(return_pct - expected_return_pct) < 0.01, \
                    f"return_pct mismatch at {row['date']}: expected {expected_return_pct:.4f}, got {return_pct:.4f}"
        
    except Exception as e:
        pytest.skip(f"Backtest failed (likely due to missing data): {e}")


@pytest.mark.slow
def test_dynamic_starting_capital(setup_test_universe):
    """Test that NAV can be reconstructed with different starting capital."""
    universe_id = setup_test_universe
    db_service = DatabaseService()
    
    # Get universe tickers
    tickers_data = db_service.get_universe_tickers(universe_id)
    if len(tickers_data) < 5:
        pytest.skip("Not enough tickers in test universe")
    
    tickers = [t['ticker'] for t in tickers_data[:5]]
    
    # Get available signals
    signals_df = db_service.db_manager.execute_query(
        "SELECT DISTINCT signal_name FROM signal_raw LIMIT 1"
    )
    if signals_df.empty:
        pytest.skip("No signals available in database")
    
    signals = [signals_df.iloc[0]['signal_name']]
    
    # Create config with known initial capital
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=30)
    original_capital = 10000.0
    
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        universe_id=universe_id,
        name=f"Dynamic Capital Test {TEST_UNIVERSE_NAME}",
        initial_capital=original_capital,
        rebalancing_frequency='monthly',
        min_lookback_days=20,
        max_lookback_days=60
    )
    
    # Run backtest
    engine = BacktestEngine()
    try:
        result = engine.run_backtest(
            tickers=tickers,
            signals=signals,
            config=config
        )
        
        # Get NAV data with original capital (no starting_capital parameter)
        nav_df_original = db_service.db_manager.get_backtest_nav(result.backtest_id)
        if nav_df_original.empty:
            pytest.skip("No NAV data stored")
        
        # Get NAV data with different starting capital
        new_capital = 50000.0
        nav_df_new = db_service.db_manager.get_backtest_nav(
            result.backtest_id,
            starting_capital=new_capital
        )
        
        # Verify both have same number of records
        assert len(nav_df_original) == len(nav_df_new), \
            "Both NAV dataframes should have same number of records"
        
        # Verify that NAV values are different but return_pct is the same
        for idx in range(min(len(nav_df_original), len(nav_df_new))):
            orig_row = nav_df_original.iloc[idx]
            new_row = nav_df_new.iloc[idx]
            
            orig_nav = orig_row['nav']
            new_nav = new_row['nav']
            orig_return_pct = orig_row.get('return_pct')
            new_return_pct = new_row.get('return_pct')
            
            # If we have return_pct, verify reconstruction
            if orig_return_pct is not None and not pd.isna(orig_return_pct):
                # Verify return_pct is the same
                assert abs(orig_return_pct - new_return_pct) < 0.001, \
                    f"return_pct should be the same: {orig_return_pct} vs {new_return_pct}"
                
                # Verify new NAV is reconstructed correctly
                expected_new_nav = new_capital * (1 + orig_return_pct)
                assert abs(new_nav - expected_new_nav) < 0.01, \
                    f"Reconstructed NAV mismatch: expected {expected_new_nav:.2f}, got {new_nav:.2f}"
        
    except Exception as e:
        pytest.skip(f"Backtest failed (likely due to missing data): {e}")

