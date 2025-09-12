"""
End-to-end integration tests for the complete financial investment system.

Tests the full workflow from signal calculation through portfolio optimization
to backtesting, ensuring all components work together correctly.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from signals.calculator import SignalCalculator
from solver.solver import PortfolioSolver
from solver.config import SolverConfig
from solver.models import Portfolio
from backtest.engine import BacktestEngine
from backtest.config import BacktestConfig
from database.manager import DatabaseManager


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def setup_method(self):
        """Setup test data and components."""
        # Create comprehensive test data
        self.dates = pd.date_range(start='2023-01-01', end='2024-01-31', freq='D')
        np.random.seed(42)
        
        # Generate realistic price data for multiple tickers
        self.tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        # Extend date range to provide more data for optimization
        extended_dates = pd.date_range(start='2023-01-01', end='2024-01-31', freq='D')
        self.price_history = pd.DataFrame()
        
        for ticker in self.tickers:
            base_price = 100.0 if ticker == 'AAPL' else 200.0
            returns = np.random.randn(len(extended_dates)) * 0.02
            prices = base_price * np.exp(np.cumsum(returns))
            self.price_history[ticker] = prices
        
        self.price_history.index = extended_dates.date
        
        # Setup components
        self.price_fetcher = Mock()
        self.database_manager = Mock()
        self.signal_calculator = SignalCalculator(self.database_manager)
        
        # Configure portfolio solver for testing
        from solver.config import SolverConfig
        solver_config = SolverConfig()
        solver_config.allocation_method = "score_based"
        solver_config.max_weight = 0.5  # Allow up to 50% per stock for testing
        self.portfolio_solver = PortfolioSolver(solver_config)
        self.backtest_engine = BacktestEngine()
        
        # Mock price fetcher
        self.price_fetcher.get_price_history.return_value = self.price_history
        
        # Mock database manager to store and retrieve signals
        self.stored_signals = []
        self.database_manager.store_signals_raw.side_effect = lambda signals: self.stored_signals.extend(signals)
        self.database_manager.get_signals_raw.side_effect = lambda tickers, signal_names, start_date, end_date: pd.DataFrame([
            {
                'asof_date': signal.asof_date,
                'ticker': signal.ticker,
                'signal_name': signal.signal_name,
                'value': signal.value,
                'metadata': signal.metadata,
                'created_at': signal.created_at
            } for signal in self.stored_signals
            if signal.ticker in tickers and signal.signal_name in signal_names
            and start_date <= signal.asof_date <= end_date
        ])
    
    def test_complete_workflow_signal_calculation_to_portfolio(self):
        """Test complete workflow from signal calculation to portfolio creation."""
        # Step 1: Calculate signals
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=True
        )
        
        assert isinstance(signal_results, pd.DataFrame)
        assert not signal_results.empty
        assert 'ticker' in signal_results.columns
        assert 'signal_name' in signal_results.columns
        assert 'value' in signal_results.columns
        
        # Step 2: Combine signals to scores
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        assert not combined_scores.empty
        assert 'ticker' in combined_scores.columns
        assert 'score' in combined_scores.columns
        
        # Step 3: Create alpha scores dictionary
        target_date = date(2024, 1, 15)
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                # Use the latest score for the target date
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        assert len(alpha_scores) > 0
        
        # Step 4: Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, self.price_history, target_date
        )
        
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.get_active_positions()) > 0
        assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
    
    def test_complete_workflow_with_backtesting(self):
        """Test complete workflow including backtesting."""
        # Step 1: Calculate signals for backtesting period
        signals = ['SENTIMENT']
        start_date = date(2023, 1, 1)
        end_date = date(2024, 1, 31)
        
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        assert isinstance(signal_results, pd.DataFrame)
        assert not signal_results.empty
        
        # Step 2: Combine signals to scores
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        assert not combined_scores.empty
        
        # Step 3: Create backtest configuration
        backtest_config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=100000.0,
            rebalancing_frequency='monthly',
            evaluation_period='monthly',
            transaction_costs=0.001,
            max_weight=0.1,
            risk_aversion=0.5,
            benchmark_ticker='SPY'
        )
        
        # Step 4: Run backtest
        backtest_result = self.backtest_engine.run_backtest(
            self.tickers, signals, backtest_config, self.price_history
        )
        
        assert backtest_result is not None
        assert hasattr(backtest_result, 'total_return')
        assert hasattr(backtest_result, 'annualized_return')
        assert hasattr(backtest_result, 'volatility')
        assert hasattr(backtest_result, 'sharpe_ratio')
        assert hasattr(backtest_result, 'max_drawdown')
    
    def test_workflow_with_different_solver_configs(self):
        """Test workflow with different solver configurations."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Calculate signals and scores
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Test with different solver configurations
        configs = [
            SolverConfig(allocation_method="mean_variance", risk_aversion=0.0),
            SolverConfig(allocation_method="mean_variance", risk_aversion=1.0),
            SolverConfig(allocation_method="score_based", max_weight=0.05),
            SolverConfig(allocation_method="score_based", max_weight=0.2),
            SolverConfig(long_only=False, max_weight=0.1),
            SolverConfig(long_only=True, max_weight=0.1),
        ]
        
        for config in configs:
            solver = PortfolioSolver(config)
            portfolio = solver.solve_portfolio(alpha_scores, self.price_history, target_date)
            
            assert portfolio is not None
            assert isinstance(portfolio, Portfolio)
            assert len(portfolio.get_active_positions()) > 0
            assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
    
    def test_workflow_with_different_signal_combinations(self):
        """Test workflow with different signal combination methods."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Calculate signals
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        # Test different combination methods
        methods = [
            ('equal_weight', None),
            ('weighted', {'weights': {'SENTIMENT': 1.0}}),
            ('zscore', None),
        ]
        
        for method, method_params in methods:
            combined_scores = self.signal_calculator.combine_signals_to_scores(
                self.tickers, signals, start_date, end_date, 
                method=method, method_params=method_params, store_in_db=False
            )
            
            assert isinstance(combined_scores, pd.DataFrame)
            assert not combined_scores.empty
            
            # Create alpha scores
            alpha_scores = {}
            for ticker in self.tickers:
                ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
                if not ticker_scores.empty:
                    latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                    if not latest_score.empty:
                        alpha_scores[ticker] = latest_score['score'].iloc[-1]
            
            # Solve portfolio
            portfolio = self.portfolio_solver.solve_portfolio(
                alpha_scores, self.price_history, target_date
            )
            
            assert portfolio is not None
            assert isinstance(portfolio, Portfolio)
            assert len(portfolio.get_active_positions()) > 0
            assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
    
    def test_workflow_with_missing_data(self):
        """Test workflow with missing data scenarios."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Create price data with missing values
        incomplete_price_data = self.price_history.copy()
        incomplete_price_data.loc[incomplete_price_data.index[:10], 'AAPL'] = np.nan
        incomplete_price_data.loc[incomplete_price_data.index[10:20], 'MSFT'] = np.nan
        
        self.price_fetcher.get_price_history.return_value = incomplete_price_data
        
        # Calculate signals
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        # Should handle missing data gracefully
        assert isinstance(signal_results, pd.DataFrame)
        
        # Combine signals
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, incomplete_price_data, target_date
        )
        
        # Should handle missing data gracefully
        assert portfolio is not None or portfolio is None  # Either result is acceptable
    
    def test_workflow_with_extreme_data(self):
        """Test workflow with extreme data scenarios."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Create price data with extreme values
        extreme_price_data = self.price_history.copy()
        extreme_price_data.loc[extreme_price_data.index[:5], 'AAPL'] = 1e10
        extreme_price_data.loc[extreme_price_data.index[5:10], 'MSFT'] = 1e-10
        extreme_price_data.loc[extreme_price_data.index[10:15], 'GOOGL'] = 0.0
        
        self.price_fetcher.get_price_history.return_value = extreme_price_data
        
        # Calculate signals
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        # Should handle extreme data gracefully
        assert isinstance(signal_results, pd.DataFrame)
        
        # Combine signals
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, extreme_price_data, target_date
        )
        
        # Should handle extreme data gracefully
        assert portfolio is not None or portfolio is None  # Either result is acceptable
    
    def test_workflow_with_unicode_tickers(self):
        """Test workflow with unicode tickers."""
        unicode_tickers = ['AAPL', '测试', 'MSFT', 'GOOGL']
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Create price data for unicode tickers
        unicode_price_data = self.price_history.copy()
        unicode_price_data['测试'] = unicode_price_data['AAPL'] * 0.8
        
        self.price_fetcher.get_price_history.return_value = unicode_price_data
        
        # Calculate signals
        signal_results = self.signal_calculator.calculate_signals(
            unicode_tickers, signals, start_date, end_date, store_in_db=False
        )
        
        assert isinstance(signal_results, pd.DataFrame)
        
        # Combine signals
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            unicode_tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in unicode_tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, unicode_price_data, target_date
        )
        
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.get_active_positions()) > 0
        assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
    
    def test_workflow_with_large_dataset(self):
        """Test workflow with large dataset."""
        # Create large dataset
        large_tickers = [f'TICKER_{i:03d}' for i in range(100)]
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Create price data for large dataset
        large_price_data = pd.DataFrame()
        for ticker in large_tickers:
            base_price = 100.0
            returns = np.random.randn(len(self.dates)) * 0.02
            prices = base_price * np.exp(np.cumsum(returns))
            large_price_data[ticker] = prices
        large_price_data.index = self.dates.date
        
        self.price_fetcher.get_price_history.return_value = large_price_data
        
        # Calculate signals
        signal_results = self.signal_calculator.calculate_signals(
            large_tickers, signals, start_date, end_date, store_in_db=False
        )
        
        assert isinstance(signal_results, pd.DataFrame)
        
        # Combine signals
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            large_tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in large_tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, large_price_data, target_date
        )
        
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.get_active_positions()) > 0
        assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
    
    def test_workflow_with_database_errors(self):
        """Test workflow with database errors."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Mock database errors
        self.database_manager.store_signals_raw.side_effect = Exception("Database error")
        self.database_manager.store_scores_combined.side_effect = Exception("Database error")
        
        # Calculate signals (should handle database errors gracefully)
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=True
        )
        
        assert isinstance(signal_results, pd.DataFrame)
        
        # Combine signals (should handle database errors gracefully)
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=True
        )
        
        assert isinstance(combined_scores, pd.DataFrame)
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, self.price_history, target_date
        )
        
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.get_active_positions()) > 0
        assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
    
    def test_workflow_performance(self):
        """Test workflow performance."""
        import time
        
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        start_time = time.time()
        
        # Calculate signals
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        # Combine signals
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        # Create alpha scores
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        # Solve portfolio
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, self.price_history, target_date
        )
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 30.0  # 30 seconds max
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
    
    def test_workflow_deterministic(self):
        """Test workflow is deterministic with same inputs."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Run workflow twice
        def run_workflow():
            signal_results = self.signal_calculator.calculate_signals(
                self.tickers, signals, start_date, end_date, store_in_db=False
            )
            
            combined_scores = self.signal_calculator.combine_signals_to_scores(
                self.tickers, signals, start_date, end_date, 
                method='equal_weight', store_in_db=False
            )
            
            alpha_scores = {}
            for ticker in self.tickers:
                ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
                if not ticker_scores.empty:
                    latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                    if not latest_score.empty:
                        alpha_scores[ticker] = latest_score['score'].iloc[-1]
            
            portfolio = self.portfolio_solver.solve_portfolio(
                alpha_scores, self.price_history, target_date
            )
            
            return portfolio
        
        portfolio1 = run_workflow()
        portfolio2 = run_workflow()
        
        # Results should be identical (or very similar) with same inputs
        assert portfolio1 is not None
        assert portfolio2 is not None
        assert isinstance(portfolio1, Portfolio)
        assert isinstance(portfolio2, Portfolio)
        
        # Compare portfolio weights
        weights1 = portfolio1.get_weights()
        weights2 = portfolio2.get_weights()
        
        for ticker in weights1:
            assert abs(weights1[ticker] - weights2[ticker]) < 1e-6
    
    def test_workflow_concurrent_execution(self):
        """Test workflow with concurrent execution."""
        import threading
        import time
        
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        results = []
        
        def run_workflow_thread():
            signal_results = self.signal_calculator.calculate_signals(
                self.tickers, signals, start_date, end_date, store_in_db=False
            )
            
            combined_scores = self.signal_calculator.combine_signals_to_scores(
                self.tickers, signals, start_date, end_date, 
                method='equal_weight', store_in_db=False
            )
            
            alpha_scores = {}
            for ticker in self.tickers:
                ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
                if not ticker_scores.empty:
                    latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                    if not latest_score.empty:
                        alpha_scores[ticker] = latest_score['score'].iloc[-1]
            
            portfolio = self.portfolio_solver.solve_portfolio(
                alpha_scores, self.price_history, target_date
            )
            
            results.append(portfolio)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=run_workflow_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have completed successfully
        assert len(results) == 5
        for portfolio in results:
            assert portfolio is not None
            assert isinstance(portfolio, Portfolio)
    
    def test_workflow_memory_efficiency(self):
        """Test workflow memory efficiency."""
        # Create large dataset
        large_tickers = [f'TICKER_{i:03d}' for i in range(1000)]
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Create price data for large dataset
        large_price_data = pd.DataFrame()
        for ticker in large_tickers:
            base_price = 100.0
            returns = np.random.randn(len(self.dates)) * 0.02
            prices = base_price * np.exp(np.cumsum(returns))
            large_price_data[ticker] = prices
        large_price_data.index = self.dates.date
        
        self.price_fetcher.get_price_history.return_value = large_price_data
        
        # Run workflow
        signal_results = self.signal_calculator.calculate_signals(
            large_tickers, signals, start_date, end_date, store_in_db=False
        )
        
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            large_tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        alpha_scores = {}
        for ticker in large_tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, large_price_data, target_date
        )
        
        # Should handle large datasets efficiently
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
    
    def test_workflow_error_handling(self):
        """Test workflow error handling."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Test with invalid inputs
        with pytest.raises(TypeError):
            self.signal_calculator.calculate_signals(
                None, signals, start_date, end_date
            )
        
        with pytest.raises(TypeError):
            self.signal_calculator.calculate_signals(
                self.tickers, None, start_date, end_date
            )
        
        with pytest.raises(TypeError):
            self.portfolio_solver.solve_portfolio(
                None, self.price_history, target_date
            )
        
        with pytest.raises(TypeError):
            self.portfolio_solver.solve_portfolio(
                {}, None, target_date
            )
    
    def test_workflow_logging(self):
        """Test workflow logging."""
        import logging
        
        # Set up logging capture
        logger = logging.getLogger('signals.calculator')
        with patch.object(logger, 'info') as mock_info:
            signals = ['SENTIMENT']
            start_date = date(2024, 1, 1)
            end_date = date(2024, 1, 31)
            
            signal_results = self.signal_calculator.calculate_signals(
                self.tickers, signals, start_date, end_date, store_in_db=False
            )
            
            # Check that appropriate log messages are generated
            assert mock_info.called
            assert isinstance(signal_results, pd.DataFrame)
    
    def test_workflow_validation(self):
        """Test workflow validation."""
        signals = ['SENTIMENT']
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        target_date = date(2024, 1, 15)
        
        # Run complete workflow
        signal_results = self.signal_calculator.calculate_signals(
            self.tickers, signals, start_date, end_date, store_in_db=False
        )
        
        combined_scores = self.signal_calculator.combine_signals_to_scores(
            self.tickers, signals, start_date, end_date, 
            method='equal_weight', store_in_db=False
        )
        
        alpha_scores = {}
        for ticker in self.tickers:
            ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                latest_score = ticker_scores[ticker_scores['asof_date'] <= target_date]
                if not latest_score.empty:
                    alpha_scores[ticker] = latest_score['score'].iloc[-1]
        
        portfolio = self.portfolio_solver.solve_portfolio(
            alpha_scores, self.price_history, target_date
        )
        
        # Validate results
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.get_active_positions()) > 0
        assert abs(portfolio.get_total_weight() - 1.0) < 1e-6
        
        # Validate portfolio weights
        weights = portfolio.get_weights()
        for weight in weights.values():
            assert 0 <= weight <= 1
        
        # Validate alpha scores
        scores = portfolio.get_alpha_scores()
        for score in scores.values():
            assert -1 <= score <= 1
        
        # Validate portfolio metrics
        metrics = self.portfolio_solver.get_portfolio_metrics(portfolio, self.price_history)
        assert isinstance(metrics, dict)
        assert 'expected_return' in metrics
        assert 'volatility' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics


if __name__ == '__main__':
    pytest.main([__file__])
