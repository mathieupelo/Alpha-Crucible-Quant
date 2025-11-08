"""
Simulation engine for backtesting.

This module handles the main simulation loop that runs the backtest day-by-day.
"""

import logging
from datetime import date
from typing import List, Dict, Any, Tuple
import pandas as pd

from .config import BacktestConfig
from .metrics_calculation import BacktestMetricsCalculator

logger = logging.getLogger(__name__)


class BacktestSimulation:
    """Handles the main backtest simulation loop."""
    
    def __init__(self, price_fetcher, metrics_calculator: BacktestMetricsCalculator):
        """
        Initialize simulation engine.
        
        Args:
            price_fetcher: Price fetcher instance
            metrics_calculator: Metrics calculator instance
        """
        self.price_fetcher = price_fetcher
        self.metrics_calculator = metrics_calculator
    
    def run_simulation_with_portfolios(self, portfolios_created: List[Dict[str, Any]], 
                                      tickers: List[str], config: BacktestConfig,
                                      price_data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.DataFrame, date]:
        """
        Run simulation using pre-created portfolios.
        
        Args:
            portfolios_created: List of portfolio creation results
            tickers: List of stock ticker symbols
            config: Backtesting configuration
            price_data: Price data DataFrame
            
        Returns:
            Tuple of (portfolio_values, benchmark_values, weights_history, first_rebalance_date)
        """
        logger.info("Starting backtest simulation with pre-created portfolios...")
        
        if price_data is None or price_data.empty:
            logger.error("Failed to get price data")
            return pd.Series(), pd.Series(), pd.DataFrame(), None
        
        # Initialize tracking variables
        portfolio_value = config.initial_capital
        benchmark_value = config.initial_capital
        
        portfolio_values = pd.Series(index=price_data.index, dtype=float)
        benchmark_values = pd.Series(index=price_data.index, dtype=float)
        weights_history = pd.DataFrame(index=[p['inference_date'] for p in portfolios_created], columns=tickers, dtype=float)
        
        # Store returns for plotting
        strategy_returns = pd.Series(index=price_data.index, dtype=float)
        benchmark_returns = pd.Series(index=price_data.index, dtype=float)
        
        # Get benchmark data
        if config.use_equal_weight_benchmark:
            benchmark_data = price_data
        else:
            benchmark_data = self.price_fetcher.get_price_history(
                config.benchmark_ticker, config.start_date, config.end_date
            )
            if benchmark_data is not None and not benchmark_data.empty:
                benchmark_data = benchmark_data.reindex(price_data.index, method='ffill')
            else:
                benchmark_data = pd.DataFrame()
        
        # Find first rebalance date
        first_rebalance_date = None
        for portfolio in portfolios_created:
            if portfolio['inference_date'] >= config.start_date:
                first_rebalance_date = portfolio['inference_date']
                break
        
        if first_rebalance_date is None:
            logger.error("No valid rebalancing dates found")
            return pd.Series(), pd.Series(), pd.DataFrame(), None
        
        logger.info(f"Strategy and benchmark will start on: {first_rebalance_date}")
        
        # Reset values at first rebalance date
        portfolio_value = config.initial_capital
        benchmark_value = config.initial_capital
        
        # Create portfolio weights lookup
        portfolio_weights = {}
        for portfolio in portfolios_created:
            portfolio_weights[portfolio['inference_date']] = portfolio['weights']
        
        # Run simulation
        for i, current_date in enumerate(price_data.index):
            if current_date < first_rebalance_date:
                continue
            
            # Get current portfolio weights
            current_weights = None
            for rebal_date in sorted(portfolio_weights.keys()):
                if rebal_date <= current_date:
                    current_weights = portfolio_weights[rebal_date]
                else:
                    break
            
            # Update portfolio value
            if current_weights is not None:
                # Convert weights dict to Series for compatibility
                weights_series = pd.Series(current_weights)
                portfolio_return = self.metrics_calculator.calculate_portfolio_return(
                    weights_series, price_data, current_date, i
                )
                if portfolio_return is not None:
                    portfolio_value *= (1 + portfolio_return)
                    strategy_returns.loc[current_date] = portfolio_return
            
            # Update benchmark value
            if not benchmark_data.empty and current_date in benchmark_data.index:
                if config.use_equal_weight_benchmark:
                    benchmark_return = self.metrics_calculator.calculate_equal_weight_return(
                        tickers, benchmark_data, current_date, i
                    )
                else:
                    benchmark_return = self.metrics_calculator.calculate_benchmark_return(
                        benchmark_data, current_date, i
                    )
                
                if benchmark_return is not None:
                    benchmark_value *= (1 + benchmark_return)
                    benchmark_returns.loc[current_date] = benchmark_return
            
            # Store values
            portfolio_values.loc[current_date] = portfolio_value
            benchmark_values.loc[current_date] = benchmark_value
        
        # Store weights history
        for portfolio in portfolios_created:
            weights_history.loc[portfolio['inference_date']] = portfolio['weights']
        
        logger.info("Backtest simulation completed")
        
        # Filter to only include data from first rebalance date onwards
        portfolio_values = portfolio_values[portfolio_values.index >= first_rebalance_date].dropna()
        benchmark_values = benchmark_values[benchmark_values.index >= first_rebalance_date].dropna()
        
        return portfolio_values, benchmark_values, weights_history, first_rebalance_date, strategy_returns.dropna(), benchmark_returns.dropna()

