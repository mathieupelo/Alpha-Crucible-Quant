"""
Database Service

Service layer for database operations and data processing.
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import pandas as pd
import logging

# Add src to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from database import DatabaseManager
from database.models import Backtest, BacktestNav, Portfolio, PortfolioPosition, SignalRaw, ScoreCombined

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self):
        """Initialize database service."""
        self.db_manager = DatabaseManager()
        if not self.db_manager.connect():
            raise Exception("Failed to connect to database")
    
    def _parse_json_field(self, value: Any) -> Any:
        """Parse JSON string fields to dictionaries."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value
    
    def get_all_backtests(self, page: int = 1, size: int = 50) -> Dict[str, Any]:
        """Get all backtests with pagination."""
        try:
            backtests_df = self.db_manager.get_backtests()
            
            if backtests_df.empty:
                return {
                    "backtests": [],
                    "total": 0,
                    "page": page,
                    "size": size
                }
            
            # Convert to list of dictionaries
            backtests = backtests_df.to_dict('records')
            
            # Parse JSON fields for each backtest
            for backtest in backtests:
                backtest['universe'] = self._parse_json_field(backtest.get('universe'))
                backtest['params'] = self._parse_json_field(backtest.get('params'))
            
            # Apply pagination
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            paginated_backtests = backtests[start_idx:end_idx]
            
            return {
                "backtests": paginated_backtests,
                "total": len(backtests),
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"Error getting backtests: {e}")
            raise
    
    def get_backtest_by_run_id(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get specific backtest by run ID."""
        try:
            backtest = self.db_manager.get_backtest_by_run_id(run_id)
            if backtest is None:
                return None
            
            return {
                "id": backtest.id,
                "run_id": backtest.run_id,
                "start_date": backtest.start_date,
                "end_date": backtest.end_date,
                "frequency": backtest.frequency,
                "universe": self._parse_json_field(backtest.universe),
                "benchmark": backtest.benchmark,
                "params": self._parse_json_field(backtest.params),
                "created_at": backtest.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting backtest {run_id}: {e}")
            raise
    
    def get_backtest_nav(self, run_id: str, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get NAV data for a backtest."""
        try:
            nav_df = self.db_manager.get_backtest_nav(run_id, start_date, end_date)
            
            if nav_df.empty:
                return []
            
            return nav_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting NAV data for {run_id}: {e}")
            raise
    
    def get_backtest_portfolios(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all portfolios for a backtest."""
        try:
            portfolios_df = self.db_manager.get_portfolios(run_id=run_id)
            
            if portfolios_df.empty:
                return []
            
            portfolios = portfolios_df.to_dict('records')
            
            # Parse JSON fields and add position count for each portfolio
            for portfolio in portfolios:
                portfolio['params'] = self._parse_json_field(portfolio.get('params'))
                positions_df = self.db_manager.get_portfolio_positions(portfolio['id'])
                portfolio['position_count'] = len(positions_df)
                portfolio['total_value'] = 0.0  # Will be calculated from NAV data
            
            return portfolios
            
        except Exception as e:
            logger.error(f"Error getting portfolios for {run_id}: {e}")
            raise
    
    def get_portfolio_details(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed portfolio information."""
        try:
            portfolio = self.db_manager.get_portfolio_by_id(portfolio_id)
            if portfolio is None:
                return None
            
            # Get portfolio positions
            positions_df = self.db_manager.get_portfolio_positions(portfolio_id)
            positions = positions_df.to_dict('records') if not positions_df.empty else []
            
            return {
                "id": portfolio.id,
                "run_id": portfolio.run_id,
                "asof_date": portfolio.asof_date,
                "method": portfolio.method,
                "params": self._parse_json_field(portfolio.params),
                "cash": portfolio.cash,
                "notes": portfolio.notes,
                "created_at": portfolio.created_at,
                "positions": positions
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio {portfolio_id}: {e}")
            raise
    
    def get_backtest_signals(self, run_id: str, start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get raw signals for a backtest period."""
        try:
            # Get backtest to determine date range
            backtest = self.db_manager.get_backtest_by_run_id(run_id)
            if backtest is None:
                return []
            
            if start_date is None:
                start_date = backtest.start_date
            if end_date is None:
                end_date = backtest.end_date
            
            signals_df = self.db_manager.get_signals_raw(
                start_date=start_date,
                end_date=end_date
            )
            
            if signals_df.empty:
                return []
            
            return signals_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting signals for {run_id}: {e}")
            raise
    
    def get_backtest_scores(self, run_id: str, start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get combined scores for a backtest period."""
        try:
            # Get backtest to determine date range
            backtest = self.db_manager.get_backtest_by_run_id(run_id)
            if backtest is None:
                return []
            
            if start_date is None:
                start_date = backtest.start_date
            if end_date is None:
                end_date = backtest.end_date
            
            scores_df = self.db_manager.get_scores_combined(
                start_date=start_date,
                end_date=end_date
            )
            
            if scores_df.empty:
                return []
            
            return scores_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting scores for {run_id}: {e}")
            raise
    
    def get_backtest_metrics(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Calculate backtest performance metrics."""
        try:
            # Get NAV data
            nav_data = self.get_backtest_nav(run_id)
            if not nav_data:
                return None
            
            # Convert to DataFrame for calculations
            nav_df = pd.DataFrame(nav_data)
            nav_df['date'] = pd.to_datetime(nav_df['date'])
            nav_df = nav_df.set_index('date').sort_index()
            
            if len(nav_df) < 2:
                return None
            
            # Calculate returns
            nav_series = nav_df['nav']
            returns = nav_series.pct_change().dropna()
            
            # Calculate metrics
            total_return = (nav_series.iloc[-1] / nav_series.iloc[0] - 1) * 100
            
            # Annualized return
            days = (nav_series.index[-1] - nav_series.index[0]).days
            annualized_return = ((nav_series.iloc[-1] / nav_series.iloc[0]) ** (365 / days) - 1) * 100
            
            # Volatility (annualized)
            volatility = returns.std() * (252 ** 0.5) * 100
            
            # Sharpe ratio (assuming 0% risk-free rate)
            sharpe_ratio = (returns.mean() * 252) / (returns.std() * (252 ** 0.5)) if returns.std() > 0 else 0
            
            # Max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Win rate
            win_rate = (returns > 0).mean() * 100
            
            # Alpha, Beta, Information Ratio (simplified)
            alpha = 0.0  # Would need benchmark data for proper calculation
            beta = 1.0   # Would need benchmark data for proper calculation
            information_ratio = 0.0  # Would need benchmark data for proper calculation
            tracking_error = 0.0     # Would need benchmark data for proper calculation
            
            # Portfolio metrics
            portfolios = self.get_backtest_portfolios(run_id)
            num_rebalances = len(portfolios)
            
            return {
                "run_id": run_id,
                "total_return": round(total_return, 2),
                "annualized_return": round(annualized_return, 2),
                "volatility": round(volatility, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown": round(max_drawdown, 2),
                "win_rate": round(win_rate, 2),
                "alpha": round(alpha, 2),
                "beta": round(beta, 2),
                "information_ratio": round(information_ratio, 2),
                "tracking_error": round(tracking_error, 2),
                "num_rebalances": num_rebalances,
                "avg_turnover": 0.0,  # Would need historical data
                "avg_num_positions": 0.0,  # Would need historical data
                "max_concentration": 0.0,  # Would need historical data
                "execution_time_seconds": 0.0  # Would need backtest metadata
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics for {run_id}: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.db_manager:
            self.db_manager.disconnect()

