"""
Portfolio rebalancing for backtesting.

This module handles creating portfolios for rebalancing dates.
"""

import logging
from datetime import date
from typing import List, Dict, Any, Optional
import pandas as pd

from .config import BacktestConfig
from .models import BacktestResult

logger = logging.getLogger(__name__)


class BacktestPortfolioRebalancing:
    """Handles portfolio creation and rebalancing for backtesting."""
    
    def __init__(self, portfolio_service):
        """
        Initialize portfolio rebalancing.
        
        Args:
            portfolio_service: Portfolio service instance
        """
        self.portfolio_service = portfolio_service
    
    def create_portfolios_for_dates(self, signal_scores: pd.DataFrame, 
                                   rebalancing_dates: List[date], tickers: List[str], 
                                   config: BacktestConfig, run_id: str, 
                                   result: BacktestResult) -> Optional[List]:
        """
        Create portfolios for all rebalancing dates.
        
        Args:
            signal_scores: DataFrame with signal scores for all dates
            rebalancing_dates: List of rebalancing dates
            tickers: List of stock ticker symbols
            config: Backtesting configuration
            run_id: Unique backtest run identifier
            result: BacktestResult object to update on error
            
        Returns:
            List of created portfolios or None if error occurred
        """
        portfolios_created = []
        for rebal_date in rebalancing_dates:
            try:
                # Get combined scores for this date
                date_scores = signal_scores[signal_scores.index == rebal_date]
                if date_scores.empty:
                    logger.warning(f"No signal scores available for {rebal_date}")
                    continue
                
                # Convert to the format expected by portfolio service
                combined_scores_df = pd.DataFrame({
                    'asof_date': rebal_date,
                    'ticker': date_scores.columns,
                    'score': date_scores.iloc[0].values
                })
                
                portfolio_result = self.portfolio_service.create_portfolio_from_scores(
                    combined_scores_df, tickers, rebal_date, config.universe_id, run_id=run_id,
                    max_weight=config.max_weight
                )
                portfolios_created.append(portfolio_result)
                logger.info(f"Created portfolio for {rebal_date}")
            except Exception as e:
                error_msg = f"Failed to create portfolio for {rebal_date}: {e}"
                logger.error(error_msg)
                result.error_message = error_msg
                return None
        
        return portfolios_created

