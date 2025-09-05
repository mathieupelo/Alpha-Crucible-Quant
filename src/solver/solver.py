"""
Portfolio optimization solver using CVXOPT.

Implements mean-variance optimization with signal-based expected returns.
"""

import logging
import numpy as np
import pandas as pd
from datetime import date
from typing import Dict, List, Optional, Tuple
from cvxopt import matrix, solvers
import warnings

from .config import SolverConfig
from .models import Portfolio, StockPosition

logger = logging.getLogger(__name__)

# Suppress CVXOPT warnings
warnings.filterwarnings('ignore', category=UserWarning)


class PortfolioSolver:
    """Portfolio optimization solver using CVXOPT."""
    
    def __init__(self, config: Optional[SolverConfig] = None):
        """
        Initialize portfolio solver.
        
        Args:
            config: Solver configuration (optional)
        """
        self.config = config or SolverConfig()
        self._setup_solver_options()
    
    def _setup_solver_options(self):
        """Setup CVXOPT solver options."""
        solvers.options.update(self.config.solver_options)
    
    def solve_portfolio(self, alpha_scores: Dict[str, float], 
                       price_history: pd.DataFrame,
                       target_date: date) -> Optional[Portfolio]:
        """
        Solve for optimal portfolio weights.
        
        Args:
            alpha_scores: Dictionary mapping ticker to alpha score
            price_history: DataFrame with price history (indexed by date)
            target_date: Date for portfolio creation
            
        Returns:
            Optimized portfolio or None if optimization fails
        """
        try:
            # Validate inputs
            if not alpha_scores:
                logger.warning("No alpha scores provided")
                return None
            
            if price_history.empty:
                logger.warning("No price history provided")
                return None
            
            # Filter price history to target date
            price_data = price_history[price_history.index <= target_date]
            if price_data.empty:
                logger.warning(f"No price data available up to {target_date}")
                return None
            
            # Get common tickers
            common_tickers = list(set(alpha_scores.keys()) & set(price_data.columns))
            if not common_tickers:
                logger.warning("No common tickers between alpha scores and price history")
                return None
            
            logger.info(f"Solving portfolio for {len(common_tickers)} tickers on {target_date}")
            
            # Choose allocation method based on config
            if self.config.allocation_method == "score_based":
                weights = self._solve_score_based_allocation(alpha_scores, common_tickers)
            else:
                # Use mean-variance optimization
                returns_data = self._prepare_returns_data(price_data, common_tickers)
                if returns_data is None:
                    return None
                
                expected_returns = self._calculate_expected_returns(alpha_scores, common_tickers)
                covariance_matrix = self._calculate_covariance_matrix(returns_data, common_tickers)
                
                if expected_returns is None or covariance_matrix is None:
                    return None
                
                weights = self._solve_optimization(expected_returns, covariance_matrix, common_tickers)
            
            if weights is None:
                return None
            
            # Create portfolio
            portfolio = Portfolio(
                creation_date=target_date,
                config=self.config
            )
            
            # Add positions
            for i, ticker in enumerate(common_tickers):
                if weights[i] > 1e-6:  # Only add positions with meaningful weights
                    portfolio.add_position(
                        ticker=ticker,
                        weight=weights[i],
                        alpha_score=alpha_scores[ticker]
                    )
            
            # Validate portfolio
            if not self._validate_portfolio(portfolio):
                logger.warning("Portfolio validation failed")
                return None
            
            logger.info(f"Successfully created portfolio with {len(portfolio.get_active_positions())} positions")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error solving portfolio: {e}")
            return None
    
    def _solve_score_based_allocation(self, alpha_scores: Dict[str, float], 
                                    tickers: List[str]) -> Optional[np.ndarray]:
        """
        Solve for portfolio weights based purely on alpha scores.
        
        This method allocates weights based on score ranking, with higher scores
        getting maximum allocation up to the max_weight constraint, and remaining
        weight distributed proportionally among lower-ranked stocks.
        
        Args:
            alpha_scores: Dictionary mapping ticker to alpha score
            tickers: List of tickers to include
            
        Returns:
            Array of weights or None if allocation fails
        """
        try:
            # Get scores for common tickers
            scores = np.array([alpha_scores.get(ticker, 0.0) for ticker in tickers])
            
            # Sort by score (descending)
            sorted_indices = np.argsort(scores)[::-1]
            sorted_scores = scores[sorted_indices]
            sorted_tickers = [tickers[i] for i in sorted_indices]
            
            # Initialize weights
            weights = np.zeros(len(tickers))
            n_assets = len(tickers)
            
            if n_assets == 0:
                return weights
            
            # Step 1: Allocate maximum weight to highest ranking stocks
            remaining_weight = 1.0
            allocated_count = 0
            
            # Give maximum allocation to top stocks until we run out of weight or stocks
            for i in range(n_assets):
                if remaining_weight <= 0:
                    break
                
                # Calculate how much weight to allocate to this stock
                weight_to_allocate = min(self.config.max_weight, remaining_weight)
                
                # Only allocate if we have enough remaining weight
                if weight_to_allocate >= self.config.min_weight:
                    weights[sorted_indices[i]] = weight_to_allocate
                    remaining_weight -= weight_to_allocate
                    allocated_count += 1
                else:
                    break
            
            # Step 2: Distribute remaining weight proportionally among remaining stocks
            if remaining_weight > 0 and allocated_count < n_assets:
                # Get remaining stocks (those not yet allocated)
                remaining_stocks = sorted_indices[allocated_count:]
                
                if len(remaining_stocks) > 0:
                    # Calculate proportional weights based on scores
                    remaining_scores = scores[remaining_stocks]
                    
                    # Handle case where all remaining scores are the same or zero
                    if np.all(remaining_scores == remaining_scores[0]):
                        # Equal distribution among remaining stocks
                        equal_weight = remaining_weight / len(remaining_stocks)
                        for idx in remaining_stocks:
                            if equal_weight >= self.config.min_weight:
                                weights[idx] = equal_weight
                    else:
                        # Proportional distribution based on scores
                        # Normalize scores to positive values for proportional allocation
                        min_score = np.min(remaining_scores)
                        if min_score < 0:
                            normalized_scores = remaining_scores - min_score + 1e-8
                        else:
                            normalized_scores = remaining_scores + 1e-8
                        
                        # Calculate proportional weights
                        total_normalized_score = np.sum(normalized_scores)
                        if total_normalized_score > 0:
                            proportional_weights = (normalized_scores / total_normalized_score) * remaining_weight
                            
                            # Apply proportional weights
                            for i, idx in enumerate(remaining_stocks):
                                if proportional_weights[i] >= self.config.min_weight:
                                    weights[idx] = proportional_weights[i]
            
            # Step 3: Apply minimum weight threshold and clean up
            weights[weights < self.config.min_weight] = 0.0
            
            # Step 4: Renormalize to ensure weights sum to 1
            total_weight = np.sum(weights)
            if total_weight > 0:
                weights = weights / total_weight
            else:
                # If all weights are zero (shouldn't happen), distribute equally
                weights = np.ones(len(tickers)) / len(tickers)
            
            logger.info(f"Score-based allocation completed. Weights: {dict(zip(tickers, weights))}")
            logger.info(f"Allocation strategy: {allocated_count} stocks at max weight ({self.config.max_weight:.1%}), remainder distributed proportionally")
            return weights
            
        except Exception as e:
            logger.error(f"Error in score-based allocation: {e}")
            return None
    
    def _prepare_returns_data(self, price_data: pd.DataFrame, tickers: List[str]) -> Optional[pd.DataFrame]:
        """
        Prepare returns data for optimization.
        
        Args:
            price_data: DataFrame with price data
            tickers: List of tickers to include
            
        Returns:
            DataFrame with returns data or None if preparation fails
        """
        try:
            # Calculate returns
            returns_data = price_data[tickers].pct_change().dropna()
            
            if returns_data.empty:
                logger.warning("No returns data available after calculation")
                return None
            
            # Remove any infinite or NaN values
            returns_data = returns_data.replace([np.inf, -np.inf], np.nan).dropna()
            
            if returns_data.empty:
                logger.warning("No valid returns data after cleaning")
                return None
            
            # Ensure we have enough data points
            min_observations = max(30, len(tickers) * 2)  # At least 30 observations or 2x number of assets
            if len(returns_data) < min_observations:
                logger.warning(f"Insufficient data: {len(returns_data)} observations, need at least {min_observations}")
                return None
            
            return returns_data
            
        except Exception as e:
            logger.error(f"Error preparing returns data: {e}")
            return None
    
    def _calculate_expected_returns(self, alpha_scores: Dict[str, float], 
                                  tickers: List[str]) -> Optional[np.ndarray]:
        """
        Calculate expected returns from alpha scores.
        
        Args:
            alpha_scores: Dictionary mapping ticker to alpha score
            tickers: List of tickers
            
        Returns:
            Array of expected returns or None if calculation fails
        """
        try:
            expected_returns = np.array([alpha_scores.get(ticker, 0.0) for ticker in tickers])
            
            # For signal-based allocation, we want to preserve the relative ranking
            # Higher scores should get higher allocations, lower scores should get lower allocations
            # We'll use the raw scores as expected returns, but scale them appropriately
            # to work with the mean-variance optimization
            
            # Scale scores to a reasonable range for expected returns (e.g., -0.1 to 0.1)
            min_score = np.min(expected_returns)
            max_score = np.max(expected_returns)
            
            if max_score > min_score:
                # Scale to [-0.1, 0.1] range
                expected_returns = 0.2 * (expected_returns - min_score) / (max_score - min_score) - 0.1
            else:
                # All scores are the same, set to zero
                expected_returns = np.zeros_like(expected_returns)
            
            return expected_returns
            
        except Exception as e:
            logger.error(f"Error calculating expected returns: {e}")
            return None
    
    def _calculate_covariance_matrix(self, returns_data: pd.DataFrame, 
                                   tickers: List[str]) -> Optional[np.ndarray]:
        """
        Calculate covariance matrix from returns data.
        
        Args:
            returns_data: DataFrame with returns data
            tickers: List of tickers
            
        Returns:
            Covariance matrix or None if calculation fails
        """
        try:
            # Calculate covariance matrix
            cov_matrix = returns_data[tickers].cov().values
            
            # Ensure matrix is positive semi-definite
            cov_matrix = self._make_positive_semi_definite(cov_matrix)
            
            return cov_matrix
            
        except Exception as e:
            logger.error(f"Error calculating covariance matrix: {e}")
            return None
    
    def _make_positive_semi_definite(self, matrix: np.ndarray) -> np.ndarray:
        """
        Make matrix positive semi-definite using eigenvalue decomposition.
        
        Args:
            matrix: Input matrix
            
        Returns:
            Positive semi-definite matrix
        """
        try:
            # Eigenvalue decomposition
            eigenvals, eigenvecs = np.linalg.eigh(matrix)
            
            # Set negative eigenvalues to zero
            eigenvals = np.maximum(eigenvals, 0)
            
            # Reconstruct matrix
            positive_semi_definite = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
            
            return positive_semi_definite
            
        except Exception as e:
            logger.error(f"Error making matrix positive semi-definite: {e}")
            return matrix
    
    def _solve_optimization(self, expected_returns: np.ndarray, 
                          covariance_matrix: np.ndarray, 
                          tickers: List[str]) -> Optional[np.ndarray]:
        """
        Solve the portfolio optimization problem.
        
        Args:
            expected_returns: Array of expected returns
            covariance_matrix: Covariance matrix
            tickers: List of tickers
            
        Returns:
            Array of optimal weights or None if optimization fails
        """
        try:
            n_assets = len(tickers)
            
            # Convert to CVXOPT matrices
            P = matrix(covariance_matrix)
            q = matrix(-expected_returns * (1 - self.config.risk_aversion))
            
            # Constraints: sum of weights = 1
            A = matrix(np.ones((1, n_assets)))
            b = matrix(1.0)
            
            # Constraints: weight bounds
            if self.config.long_only:
                # Long-only: 0 <= w <= max_weight
                G = np.vstack([-np.eye(n_assets), np.eye(n_assets)])
                h = np.hstack([np.zeros(n_assets), np.full(n_assets, self.config.max_weight)])
            else:
                # Allow short selling: -max_weight <= w <= max_weight
                G = np.vstack([-np.eye(n_assets), np.eye(n_assets)])
                h = np.hstack([np.full(n_assets, self.config.max_weight), 
                              np.full(n_assets, self.config.max_weight)])
            
            G = matrix(G)
            h = matrix(h)
            
            # Solve optimization problem
            solution = solvers.qp(P, q, G, h, A, b)
            
            if solution['status'] != 'optimal':
                logger.warning(f"Optimization failed with status: {solution['status']}")
                return None
            
            weights = np.array(solution['x']).flatten()
            
            # Ensure weights sum to 1
            weights = weights / np.sum(weights)
            
            # Apply minimum weight threshold
            weights[weights < 1e-6] = 0.0
            weights = weights / np.sum(weights) if np.sum(weights) > 0 else weights
            
            return weights
            
        except Exception as e:
            logger.error(f"Error solving optimization: {e}")
            return None
    
    def _validate_portfolio(self, portfolio: Portfolio) -> bool:
        """
        Validate the optimized portfolio.
        
        Args:
            portfolio: Portfolio to validate
            
        Returns:
            True if portfolio is valid, False otherwise
        """
        try:
            # Check total weight
            total_weight = portfolio.get_total_weight()
            if abs(total_weight - 1.0) > 1e-6:
                logger.warning(f"Portfolio weights don't sum to 1: {total_weight}")
                return False
            
            # Check individual weight bounds
            for ticker, position in portfolio.positions.items():
                if position.weight < 0:
                    logger.warning(f"Negative weight for {ticker}: {position.weight}")
                    return False
                
                if position.weight > self.config.max_weight + 1e-6:
                    logger.warning(f"Weight exceeds maximum for {ticker}: {position.weight}")
                    return False
            
            # Check minimum number of positions
            active_positions = len(portfolio.get_active_positions())
            if active_positions == 0:
                logger.warning("Portfolio has no active positions")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating portfolio: {e}")
            return False
    
    def solve_portfolio_batch(self, alpha_scores_list: List[Dict[str, float]], 
                            price_history: pd.DataFrame,
                            target_dates: List[date]) -> List[Optional[Portfolio]]:
        """
        Solve multiple portfolios in batch.
        
        Args:
            alpha_scores_list: List of alpha score dictionaries
            price_history: DataFrame with price history
            target_dates: List of target dates
            
        Returns:
            List of optimized portfolios (or None for failed optimizations)
        """
        if len(alpha_scores_list) != len(target_dates):
            raise ValueError("Number of alpha score dictionaries must match number of target dates")
        
        portfolios = []
        for alpha_scores, target_date in zip(alpha_scores_list, target_dates):
            portfolio = self.solve_portfolio(alpha_scores, price_history, target_date)
            portfolios.append(portfolio)
        
        return portfolios
    
    def get_portfolio_metrics(self, portfolio: Portfolio, 
                            price_history: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics.
        
        Args:
            portfolio: Portfolio to analyze
            price_history: DataFrame with price history
            
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            weights = portfolio.get_weights()
            active_tickers = [ticker for ticker, weight in weights.items() if weight > 0]
            
            if not active_tickers:
                return {}
            
            # Get returns data
            returns_data = price_history[active_tickers].pct_change().dropna()
            
            if returns_data.empty:
                return {}
            
            # Calculate portfolio returns
            portfolio_returns = (returns_data * list(weights.values())).sum(axis=1)
            
            # Calculate metrics
            metrics = {
                'expected_return': portfolio_returns.mean() * 252,  # Annualized
                'volatility': portfolio_returns.std() * np.sqrt(252),  # Annualized
                'sharpe_ratio': portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252) if portfolio_returns.std() > 0 else 0,
                'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
                'skewness': portfolio_returns.skew(),
                'kurtosis': portfolio_returns.kurtosis()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {}
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calculate maximum drawdown from returns series.
        
        Args:
            returns: Series of returns
            
        Returns:
            Maximum drawdown
        """
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
