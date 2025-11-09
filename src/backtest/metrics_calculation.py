"""
Performance metrics calculation for backtesting.

This module handles calculation of all performance metrics including:
- Returns, volatility, Sharpe ratio
- Drawdown, win rate
- Alpha, beta, information ratio
- Turnover, concentration metrics
"""

import logging
from datetime import date
from typing import List, Optional
import pandas as pd
import numpy as np

from .models import BacktestResult
from .config import BacktestConfig

logger = logging.getLogger(__name__)


class BacktestMetricsCalculator:
    """Handles calculation of backtest performance metrics."""
    
    def calculate_performance_metrics(self, result: BacktestResult, 
                                     portfolio_values: pd.Series, 
                                     benchmark_values: pd.Series,
                                     config: BacktestConfig):
        """Calculate performance metrics."""
        try:
            # Calculate returns
            portfolio_returns = portfolio_values.pct_change().dropna()
            benchmark_returns = benchmark_values.pct_change().dropna()
            
            # Align returns
            aligned_returns = pd.DataFrame({
                'portfolio': portfolio_returns,
                'benchmark': benchmark_returns
            }).dropna()
            
            if aligned_returns.empty:
                logger.warning("No aligned returns data for metrics calculation")
                return
            
            portfolio_returns = aligned_returns['portfolio']
            benchmark_returns = aligned_returns['benchmark']
            
            # Calculate metrics
            result.total_return = (portfolio_values.iloc[-1] / config.initial_capital) - 1
            result.annualized_return = (1 + result.total_return) ** (252 / len(portfolio_returns)) - 1
            result.volatility = portfolio_returns.std() * np.sqrt(252)
            result.sharpe_ratio = result.annualized_return / result.volatility if result.volatility > 0 else 0
            
            # Calculate max drawdown
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            result.max_drawdown = drawdown.min()
            
            # Calculate win rate
            result.win_rate = (portfolio_returns > 0).mean()
            
            # Calculate alpha and beta
            excess_returns = portfolio_returns - benchmark_returns
            result.alpha = excess_returns.mean() * 252  # Annualized
            result.beta = np.cov(portfolio_returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
            result.information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
            result.tracking_error = excess_returns.std() * np.sqrt(252)
            
            # Store returns series
            result.returns = portfolio_returns
            result.benchmark_returns = benchmark_returns
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
    
    def calculate_avg_turnover(self, weights_history: pd.DataFrame) -> float:
        """Calculate average turnover."""
        if weights_history.empty or len(weights_history) < 2:
            return 0.0
        
        turnovers = []
        for i in range(1, len(weights_history)):
            prev_weights = weights_history.iloc[i-1]
            curr_weights = weights_history.iloc[i]
            turnover = abs(curr_weights - prev_weights).sum()
            turnovers.append(turnover)
        
        return np.mean(turnovers) if turnovers else 0.0
    
    def calculate_avg_num_positions(self, weights_history: pd.DataFrame) -> float:
        """Calculate average number of positions."""
        if weights_history.empty:
            return 0.0
        
        num_positions = []
        for _, weights in weights_history.iterrows():
            num_positions.append((weights > 0).sum())
        
        return np.mean(num_positions) if num_positions else 0.0
    
    def calculate_max_concentration(self, weights_history: pd.DataFrame) -> float:
        """Calculate maximum concentration."""
        if weights_history.empty:
            return 0.0
        
        max_weights = []
        for _, weights in weights_history.iterrows():
            # Skip NaN values when calculating max
            valid_weights = weights.dropna()
            if not valid_weights.empty:
                max_weights.append(valid_weights.max())
        
        return np.max(max_weights) if max_weights else 0.0
    
    def calculate_portfolio_return(self, weights: pd.Series, price_data: pd.DataFrame,
                                  current_date: date, current_index: int) -> Optional[float]:
        """Calculate portfolio return for a given date."""
        try:
            if current_index == 0:
                return 0.0  # No return on first day
            
            prev_date = price_data.index[current_index - 1]
            
            # Get current and previous prices
            current_prices = price_data.loc[current_date]
            prev_prices = price_data.loc[prev_date]
            
            # Calculate returns
            returns = (current_prices - prev_prices) / prev_prices
            
            # Calculate portfolio return
            portfolio_return = (weights * returns).sum()
            
            return portfolio_return if not pd.isna(portfolio_return) else None
            
        except Exception as e:
            logger.error(f"Error calculating portfolio return for {current_date}: {e}")
            return None
    
    def calculate_equal_weight_return(self, tickers: List[str], price_data: pd.DataFrame,
                                     current_date: date, current_index: int) -> Optional[float]:
        """Calculate equal-weight portfolio return for a given date."""
        try:
            if current_index == 0:
                return 0.0  # No return on first day
            
            prev_date = price_data.index[current_index - 1]
            
            # Get current and previous prices for all tickers
            current_prices = price_data.loc[current_date]
            prev_prices = price_data.loc[prev_date]
            
            # Calculate individual stock returns
            returns = []
            for ticker in tickers:
                if ticker in current_prices.index and ticker in prev_prices.index:
                    current_price = current_prices[ticker]
                    prev_price = prev_prices[ticker]
                    
                    if not pd.isna(current_price) and not pd.isna(prev_price) and prev_price > 0:
                        stock_return = (current_price - prev_price) / prev_price
                        returns.append(stock_return)
            
            if not returns:
                return None
            
            # Equal-weight portfolio return is the average of individual returns
            equal_weight_return = np.mean(returns)
            
            return equal_weight_return if not pd.isna(equal_weight_return) else None
            
        except Exception as e:
            logger.error(f"Error calculating equal-weight return for {current_date}: {e}")
            return None
    
    def calculate_benchmark_return(self, benchmark_data: pd.DataFrame,
                                  current_date: date, current_index: int) -> Optional[float]:
        """Calculate benchmark return for a given date."""
        try:
            if current_index == 0:
                return 0.0  # No return on first day
            
            prev_date = benchmark_data.index[current_index - 1]
            
            # Get current and previous prices
            current_price = benchmark_data.loc[current_date, 'Close']
            prev_price = benchmark_data.loc[prev_date, 'Close']
            
            # Calculate return
            if pd.isna(current_price) or pd.isna(prev_price) or prev_price == 0:
                return None
            
            benchmark_return = (current_price - prev_price) / prev_price
            
            return benchmark_return if not pd.isna(benchmark_return) else None
            
        except Exception as e:
            logger.error(f"Error calculating benchmark return for {current_date}: {e}")
            return None

