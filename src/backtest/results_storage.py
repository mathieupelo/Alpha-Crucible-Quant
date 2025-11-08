"""
Results storage for backtesting.

This module handles storing backtest results in the database:
- NAV data
- Portfolio data
- Position data
"""

import logging
from datetime import date, datetime
from typing import List
import pandas as pd

from .models import BacktestResult
from src.database.models import BacktestNav, Portfolio, PortfolioPosition
from .config import BacktestConfig

logger = logging.getLogger(__name__)


class BacktestResultsStorage:
    """Handles storage of backtest results in the database."""
    
    def __init__(self, database_manager, price_fetcher):
        """
        Initialize results storage.
        
        Args:
            database_manager: Database manager instance
            price_fetcher: Price fetcher instance
        """
        self.database_manager = database_manager
        self.price_fetcher = price_fetcher
    
    def store_portfolio_data(self, result: BacktestResult, portfolio_values: pd.Series, 
                            benchmark_values: pd.Series, weights_history: pd.DataFrame, 
                            first_rebalance_date: date, config: BacktestConfig):
        """Store portfolio data in the database."""
        try:
            # Store backtest NAV data
            nav_objects = []
            for date, portfolio_value in portfolio_values.items():
                if pd.isna(portfolio_value):
                    continue
                    
                benchmark_value = benchmark_values.get(date, 0.0)
                if pd.isna(benchmark_value):
                    benchmark_value = 0.0
                
                # Calculate PnL
                pnl = 0.0
                if len(portfolio_values) > 1:
                    prev_date = portfolio_values.index[portfolio_values.index < date]
                    if len(prev_date) > 0:
                        prev_date = prev_date[-1]
                        prev_portfolio_value = portfolio_values.get(prev_date, portfolio_value)
                        if prev_portfolio_value > 0:
                            pnl = portfolio_value - prev_portfolio_value
                
                nav_obj = BacktestNav(
                    run_id=result.backtest_id,
                    date=date,
                    nav=float(portfolio_value),
                    benchmark_nav=float(benchmark_value) if benchmark_value > 0 else None,
                    pnl=float(pnl)
                )
                nav_objects.append(nav_obj)
            
            if nav_objects:
                try:
                    stored_count = self.database_manager.store_backtest_nav(nav_objects)
                    logger.info(f"Stored {stored_count} NAV records for backtest {result.backtest_id}")
                except Exception as e:
                    logger.error(f"Failed to store NAV data for backtest {result.backtest_id}: {e}")
                    raise
            else:
                logger.warning(f"No NAV data to store for backtest {result.backtest_id}")
            
            # Store portfolios and positions
            for date, weights_row in weights_history.iterrows():
                if weights_row.isna().all():
                    continue
                
                # Calculate portfolio value based on current NAV
                current_nav = portfolio_values.get(date, config.initial_capital)
                
                # Create portfolio
                portfolio = Portfolio(
                    run_id=result.backtest_id,
                    universe_id=config.universe_id,
                    asof_date=date,
                    method='optimization',
                    params={'risk_aversion': result.signal_weights},
                    cash=0.0,  # Always 0 since weights are normalized to sum to 1.0
                    total_value=current_nav,  # Total portfolio value available for investment
                    notes=f'Portfolio for {date}',
                    created_at=datetime.now()
                )
                
                # Store portfolio and get ID
                portfolio_id = self.database_manager.store_portfolio(portfolio)
                
                # Store portfolio positions
                positions = []
                for ticker, weight in weights_row.items():
                    if pd.isna(weight) or weight == 0:
                        continue
                    
                    # Get price used (simplified - using last available price)
                    try:
                        price_data = self.price_fetcher.get_price_history(ticker, date, date)
                        price_used = price_data.iloc[-1]['Close'] if not price_data.empty else 0.0
                    except:
                        price_used = 0.0
                    
                    position = PortfolioPosition(
                        portfolio_id=portfolio_id,
                        ticker=ticker,
                        weight=float(weight),
                        price_used=float(price_used),
                        created_at=datetime.now()
                    )
                    positions.append(position)
                
                if positions:
                    self.database_manager.store_portfolio_positions(positions)
                    logger.info(f"Stored {len(positions)} positions for portfolio {portfolio_id}")
                
        except Exception as e:
            logger.error(f"Error storing portfolio data: {e}")
            raise

