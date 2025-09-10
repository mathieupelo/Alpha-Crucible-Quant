"""
Portfolio service for creating and managing portfolios.

This module provides the PortfolioService class that handles portfolio creation
at inference time, including signal validation, score combination, and portfolio solving.
"""

import logging
from datetime import date
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
import numpy as np

from signals import SignalCalculator
from solver import PortfolioSolver
from database import DatabaseManager, Portfolio, PortfolioPosition
from utils import TradingCalendar, validate_ticker_list, validate_signal_list
from utils.error_handling import handle_calculation_errors, handle_database_errors

logger = logging.getLogger(__name__)


class PortfolioService:
    """
    Service for creating and managing portfolios at inference time.
    
    This service handles the complete portfolio creation process:
    1. Validates that the inference date is a trading day
    2. Fetches all required signal scores
    3. Validates signal completeness
    4. Combines scores and stores them
    5. Solves the portfolio optimization
    6. Stores the portfolio in the database
    
    Attributes:
        signal_calculator: Instance for signal operations
        portfolio_solver: Instance for portfolio optimization
        database_manager: Instance for database operations
        trading_calendar: Instance for trading date validation
    """
    
    def __init__(self, signal_calculator: Optional[SignalCalculator] = None,
                 portfolio_solver: Optional[PortfolioSolver] = None,
                 database_manager: Optional[DatabaseManager] = None,
                 trading_calendar: Optional[TradingCalendar] = None):
        """
        Initialize portfolio service.
        
        Args:
            signal_calculator: Signal calculator instance (optional)
            portfolio_solver: Portfolio solver instance (optional)
            database_manager: Database manager instance (optional)
            trading_calendar: Trading calendar instance (optional)
        """
        self.signal_calculator = signal_calculator or SignalCalculator()
        self.portfolio_solver = portfolio_solver or PortfolioSolver()
        self.database_manager = database_manager or DatabaseManager()
        self.trading_calendar = trading_calendar or TradingCalendar()
    
    @handle_calculation_errors
    def create_portfolio_from_scores(self, combined_scores: pd.DataFrame, 
                                   tickers: List[str], inference_date: date,
                                   run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a single portfolio for inference on a specific date using pre-combined scores.
        
        Args:
            combined_scores: DataFrame with combined signal scores
            tickers: List of stock ticker symbols
            inference_date: Date to create portfolio for
            run_id: Optional run ID to associate with the portfolio
            
        Returns:
            Dictionary containing portfolio information and status
            
        Raises:
            ValueError: If required data is missing
            RuntimeError: If portfolio optimization fails
        """
        logger.info(f"Creating portfolio for {len(tickers)} tickers on {inference_date}")
        
        # Step 0: Validate that the inference date is a trading day
        if not self.trading_calendar.validate_trading_date(inference_date):
            error_msg = f"Date {inference_date} is not a valid NYSE trading day"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Step 1: Validate inputs
        if not tickers:
            raise ValueError("Tickers list cannot be empty")
        
        if combined_scores.empty:
            error_msg = f"No combined scores provided for {inference_date}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Step 2: Filter scores for the inference date
        date_scores = combined_scores[combined_scores['asof_date'] == inference_date]
        if date_scores.empty:
            error_msg = f"No scores available for {inference_date}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Step 3: Solve the portfolio
        logger.info("Solving portfolio optimization")
        portfolio_weights = self._solve_portfolio(date_scores, tickers, inference_date)
        
        if portfolio_weights is None:
            error_msg = f"Portfolio optimization failed for {inference_date}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Step 4: Insert the solved portfolio in the database
        portfolio_id = self._store_portfolio(tickers, portfolio_weights, inference_date, 'combined_scores', None, run_id)
        
        logger.info(f"Portfolio created successfully with ID: {portfolio_id}")
        
        return {
            'portfolio_id': portfolio_id,
            'inference_date': inference_date,
            'tickers': tickers,
            'method': 'combined_scores',
            'method_params': None,
            'weights': dict(zip(tickers, portfolio_weights)),
            'status': 'success'
        }
    
    def _solve_portfolio(self, combined_scores_df: pd.DataFrame, tickers: List[str], inference_date: date) -> Optional[np.ndarray]:
        """
        Solve portfolio optimization using combined scores.
        
        Args:
            combined_scores_df: DataFrame with combined scores
            tickers: List of ticker symbols
            inference_date: Date for portfolio creation
            
        Returns:
            Array of portfolio weights or None if optimization fails
        """
        try:
            # Convert scores to dictionary format expected by solver
            scores_dict = {}
            for _, row in combined_scores_df.iterrows():
                scores_dict[row['ticker']] = row['score']
            
            # Solve using the portfolio solver
            # Create a proper price history for the solver
            # We need at least 30 days of data for mean-variance optimization
            # or we can use score-based allocation which doesn't need price history
            from solver.config import SolverConfig
            
            # Configure solver for score-based allocation
            solver_config = SolverConfig(
                allocation_method="score_based",
                max_weight=0.2,  # Allow up to 20% per stock
                min_weight=0.0   # No minimum weight
            )
            self.portfolio_solver.config = solver_config
            
            # Create a minimal price history (score-based allocation doesn't need much)
            dummy_price_history = pd.DataFrame(
                index=pd.date_range(start='2023-01-01', periods=30, freq='D').date, 
                columns=tickers, 
                data=100.0  # Use 100 as base price
            )
            
            portfolio = self.portfolio_solver.solve_portfolio(
                scores_dict, dummy_price_history, inference_date
            )
            
            if portfolio is None:
                logger.error("Portfolio solver returned None")
                return None
            
            # Extract weights from portfolio
            weights_dict = portfolio.get_weights()
            weights = np.array([weights_dict.get(ticker, 0.0) for ticker in tickers])
            
            # Validate weights
            if not self._validate_weights(weights, tickers):
                logger.error("Portfolio weights validation failed")
                return None
            
            return weights
            
        except Exception as e:
            logger.error(f"Error solving portfolio: {e}")
            return None
    
    def _validate_weights(self, weights: np.ndarray, tickers: List[str]) -> bool:
        """
        Validate portfolio weights.
        
        Args:
            weights: Array of portfolio weights
            tickers: List of ticker symbols
            
        Returns:
            True if weights are valid, False otherwise
        """
        if len(weights) != len(tickers):
            logger.error(f"Weights length ({len(weights)}) doesn't match tickers length ({len(tickers)})")
            return False
        
        if np.any(weights < 0):
            logger.error("Negative weights found")
            return False
        
        if abs(np.sum(weights) - 1.0) > 1e-6:
            logger.error(f"Weights don't sum to 1.0: {np.sum(weights)}")
            return False
        
        return True
    
    @handle_database_errors
    def _store_portfolio(self, tickers: List[str], weights: np.ndarray, 
                        inference_date: date, method: str, 
                        method_params: Optional[Dict[str, Any]],
                        run_id: Optional[str] = None) -> str:
        """
        Store portfolio in the database.
        
        Args:
            tickers: List of ticker symbols
            weights: Portfolio weights
            inference_date: Date of portfolio creation
            method: Method used for signal combination
            method_params: Parameters used for combination
            run_id: Optional run ID to associate with the portfolio
            
        Returns:
            Portfolio ID
        """
        try:
            # Create portfolio object
            portfolio_run_id = run_id or f"portfolio_{inference_date}_{method}"
            portfolio = Portfolio(
                run_id=portfolio_run_id,
                asof_date=inference_date,
                method=method,
                params=method_params or {},
                notes=f"Portfolio for {inference_date} with {len(tickers)} tickers",
                created_at=pd.Timestamp.now()
            )
            
            # Store in database
            portfolio_id = self.database_manager.store_portfolio(portfolio)
            
            # Store portfolio positions
            positions = []
            for ticker, weight in zip(tickers, weights):
                if weight > 0:  # Only store positions with non-zero weights
                    position = PortfolioPosition(
                        portfolio_id=portfolio_id,
                        ticker=ticker,
                        weight=float(weight),
                        price_used=100.0,  # Dummy price for now
                        created_at=pd.Timestamp.now()
                    )
                    positions.append(position)
            
            if positions:
                self.database_manager.store_portfolio_positions(positions)
                logger.info(f"Stored {len(positions)} portfolio positions")
            
            logger.info(f"Portfolio stored with ID: {portfolio_id}")
            return portfolio_id
            
        except Exception as e:
            logger.error(f"Error storing portfolio: {e}")
            raise
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """
        Get portfolio information by ID.
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            Portfolio information dictionary or None if not found
        """
        try:
            portfolio = self.database_manager.get_portfolio(portfolio_id)
            if portfolio is None:
                return None
            
            return {
                'portfolio_id': portfolio_id,
                'asof_date': portfolio.asof_date,
                'tickers': portfolio.tickers,
                'weights': portfolio.weights,
                'method': portfolio.method,
                'method_params': portfolio.method_params,
                'created_at': portfolio.created_at
            }
            
        except Exception as e:
            logger.error(f"Error retrieving portfolio {portfolio_id}: {e}")
            return None
    
    def get_portfolios_by_date_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Get all portfolios within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of portfolio information dictionaries
        """
        try:
            portfolios = self.database_manager.get_portfolios_by_date_range(start_date, end_date)
            
            return [{
                'portfolio_id': p.portfolio_id,
                'asof_date': p.asof_date,
                'tickers': p.tickers,
                'weights': p.weights,
                'method': p.method,
                'method_params': p.method_params,
                'created_at': p.created_at
            } for p in portfolios]
            
        except Exception as e:
            logger.error(f"Error retrieving portfolios for date range {start_date} to {end_date}: {e}")
            return []
    
    def validate_portfolio_creation_prerequisites(self, tickers: List[str], signals: List[str], 
                                                inference_date: date) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for portfolio creation without actually creating it.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal names
            inference_date: Date to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate tickers
        if not validate_ticker_list(tickers):
            errors.append("Invalid ticker list")
        
        # Validate signals
        if not validate_signal_list(signals):
            errors.append("Invalid signal list")
        
        # Validate trading date
        if not self.trading_calendar.validate_trading_date(inference_date):
            errors.append(f"Date {inference_date} is not a valid NYSE trading day")
        
        # Check signal completeness
        is_complete, missing_signals = self.signal_calculator.validate_signals_complete(
            tickers, signals, inference_date
        )
        
        if not is_complete:
            errors.append(f"Missing signals: {missing_signals}")
        
        return len(errors) == 0, errors
