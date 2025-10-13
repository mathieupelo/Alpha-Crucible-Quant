"""
Database Service

Service layer for database operations and data processing.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import pandas as pd
import logging

from src.database import DatabaseManager
from src.database.models import Backtest, BacktestNav, Portfolio, PortfolioPosition, SignalRaw, ScoreCombined, Universe, UniverseTicker

# Import response models
from models import PositionResponse

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self):
        """Initialize database service."""
        self.db_manager = DatabaseManager()
        self._connected = False
        # Don't fail at initialization - connect lazily
        try:
            self._connected = self.db_manager.connect()
        except Exception as e:
            logger.warning(f"Database connection failed at initialization: {e}")
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        if not self._connected:
            return False
        # Actually test the connection by calling the database manager's is_connected method
        return self.db_manager.is_connected()
    
    def ensure_connection(self) -> bool:
        """Ensure database connection is established."""
        # Check if we have a valid connection
        if not self.is_connected():
            try:
                self._connected = self.db_manager.connect()
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                self._connected = False
                return False
        return self._connected
    
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
            
            # Parse JSON fields and add universe information for each backtest
            for backtest in backtests:
                backtest['universe'] = self._parse_json_field(backtest.get('universe'))
                backtest['params'] = self._parse_json_field(backtest.get('params'))
                
                # Get universe information
                universe = self.db_manager.get_universe_by_id(backtest.get('universe_id'))
                backtest['universe_name'] = universe.name if universe else "Unknown Universe"
            
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
            
            # Get universe information
            universe = self.db_manager.get_universe_by_id(backtest.universe_id)
            universe_name = universe.name if universe else "Unknown Universe"
            
            return {
                "id": backtest.id,
                "run_id": backtest.run_id,
                "name": backtest.name,
                "start_date": backtest.start_date,
                "end_date": backtest.end_date,
                "frequency": backtest.frequency,
                "universe_id": backtest.universe_id,
                "universe_name": universe_name,
                "universe": self._parse_json_field(backtest.universe),
                "benchmark": backtest.benchmark,
                "params": self._parse_json_field(backtest.params),
                "created_at": backtest.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting backtest {run_id}: {e}")
            raise
    
    def check_backtest_name_exists(self, name: str) -> bool:
        """Check if a backtest name already exists."""
        try:
            return self.db_manager.check_backtest_name_exists(name)
        except Exception as e:
            logger.error(f"Error checking backtest name {name}: {e}")
            raise
    
    def get_backtest_nav(self, run_id: str, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get NAV data for a backtest."""
        try:
            nav_df = self.db_manager.get_backtest_nav(run_id, start_date, end_date)
            
            if nav_df.empty:
                return []
            
            # Transform field names to match Pydantic model
            nav_records = nav_df.to_dict('records')
            for record in nav_records:
                # Rename fields to match NavResponse model
                if 'nav' in record:
                    record['portfolio_nav'] = record.pop('nav')
                if 'date' in record:
                    record['nav_date'] = record.pop('date')
                # Handle benchmark_nav field
                if 'benchmark_nav' not in record and 'benchmark' in record:
                    record['benchmark_nav'] = record.pop('benchmark')
            
            return nav_records
            
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
            
            # Parse JSON fields and add position count and universe information for each portfolio
            for portfolio in portfolios:
                portfolio['params'] = self._parse_json_field(portfolio.get('params'))
                positions_df = self.db_manager.get_portfolio_positions(portfolio['id'])
                portfolio['position_count'] = len(positions_df)
                # total_value is already in the database, no need to override it
                
                # Get universe information
                universe = self.db_manager.get_universe_by_id(portfolio.get('universe_id'))
                portfolio['universe_name'] = universe.name if universe else "Unknown Universe"
            
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
            positions = []
            if not positions_df.empty:
                for _, row in positions_df.iterrows():
                    position = PositionResponse(
                        id=int(row['id']),
                        portfolio_id=int(row['portfolio_id']),
                        ticker=str(row['ticker']),
                        weight=float(row['weight']),
                        price_used=float(row['price_used']),
                        created_at=row['created_at']
                    )
                    positions.append(position)
            
            # Get universe information
            universe = self.db_manager.get_universe_by_id(portfolio.universe_id)
            universe_name = universe.name if universe else "Unknown Universe"
            
            return {
                "id": portfolio.id,
                "run_id": portfolio.run_id,
                "universe_id": portfolio.universe_id,
                "universe_name": universe_name,
                "asof_date": portfolio.asof_date,
                "method": portfolio.method,
                "params": self._parse_json_field(portfolio.params),
                "cash": portfolio.cash,
                "total_value": portfolio.total_value,
                "notes": portfolio.notes,
                "created_at": portfolio.created_at,
                "positions": positions
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio {portfolio_id}: {e}")
            raise
    
    def get_portfolio_signals(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Get signal scores for a specific portfolio."""
        try:
            # Get portfolio details to get the date and universe
            portfolio = self.db_manager.get_portfolio_by_id(portfolio_id)
            if portfolio is None:
                return []
            
            # Get all universe tickers instead of just portfolio positions
            universe_tickers_df = self.db_manager.get_universe_tickers(portfolio.universe_id)
            if universe_tickers_df.empty:
                return []
            
            # Get the tickers from universe
            tickers = universe_tickers_df['ticker'].tolist()
            
            # Get signal scores for the portfolio date and all universe tickers
            signals_df = self.db_manager.get_signals_raw(
                tickers=tickers,
                start_date=portfolio.asof_date,
                end_date=portfolio.asof_date
            )
            
            signals = []
            if not signals_df.empty:
                # Get all unique signal names from the data
                available_signals = signals_df['signal_name'].unique().tolist()
            else:
                available_signals = []
            
            # Create signal data for ALL universe tickers, not just those with data
            for ticker in tickers:
                signal_data = {
                    'ticker': str(ticker),
                    'available_signals': [str(signal) for signal in available_signals]
                }
                
                # Add signal values if they exist for this ticker
                if not signals_df.empty:
                    ticker_signals = signals_df[signals_df['ticker'] == ticker]
                    for _, row in ticker_signals.iterrows():
                        signal_name = str(row['signal_name'])
                        signal_data[signal_name] = float(row['value']) if pd.notna(row['value']) else None
                
                signals.append(signal_data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting signals for portfolio {portfolio_id}: {e}")
            raise
    
    def get_portfolio_scores(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Get combined scores for a specific portfolio."""
        try:
            # Get portfolio details to get the date and universe
            portfolio = self.db_manager.get_portfolio_by_id(portfolio_id)
            if portfolio is None:
                return []
            
            # Get all universe tickers instead of just portfolio positions
            universe_tickers_df = self.db_manager.get_universe_tickers(portfolio.universe_id)
            if universe_tickers_df.empty:
                return []
            
            # Get the tickers from universe
            tickers = universe_tickers_df['ticker'].tolist()
            
            # Get combined scores for the portfolio date and all universe tickers
            scores_df = self.db_manager.get_scores_combined(
                tickers=tickers,
                start_date=portfolio.asof_date,
                end_date=portfolio.asof_date
            )
            
            scores = []
            
            # Create score data for ALL universe tickers, not just those with data
            for ticker in tickers:
                score_data = {
                    'ticker': str(ticker),
                    'combined_score': None,
                    'method': None
                }
                
                # Add score data if it exists for this ticker
                if not scores_df.empty:
                    ticker_scores = scores_df[scores_df['ticker'] == ticker]
                    if not ticker_scores.empty:
                        row = ticker_scores.iloc[0]
                        score_data['combined_score'] = float(row['score']) if pd.notna(row['score']) else None
                        score_data['method'] = str(row['method'])
                
                scores.append(score_data)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error getting scores for portfolio {portfolio_id}: {e}")
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
            nav_df['nav_date'] = pd.to_datetime(nav_df['nav_date'])
            nav_df = nav_df.set_index('nav_date').sort_index()
            
            if len(nav_df) < 2:
                return None
            
            # Calculate returns
            nav_series = nav_df['portfolio_nav']
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
    
    def get_all_universes(self) -> List[Dict[str, Any]]:
        """Get all universes with ticker counts."""
        try:
            universes_df = self.db_manager.get_universes()
            
            if universes_df.empty:
                return []
            
            universes = []
            for _, row in universes_df.iterrows():
                # Get ticker count for each universe
                tickers_df = self.db_manager.get_universe_tickers(int(row['id']))
                ticker_count = len(tickers_df)
                
                universe_data = {
                    "id": int(row['id']),
                    "name": str(row['name']),
                    "description": str(row.get('description')) if pd.notna(row.get('description')) else None,
                    "created_at": row['created_at'].isoformat() if pd.notna(row['created_at']) else None,
                    "updated_at": row['updated_at'].isoformat() if pd.notna(row['updated_at']) else None,
                    "ticker_count": ticker_count
                }
                universes.append(universe_data)
            
            return universes
            
        except Exception as e:
            logger.error(f"Error getting universes: {e}")
            raise
    
    def get_universe_by_id(self, universe_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific universe by ID."""
        try:
            universe = self.db_manager.get_universe_by_id(universe_id)
            if universe is None:
                return None
            
            # Get ticker count
            tickers_df = self.db_manager.get_universe_tickers(universe_id)
            ticker_count = len(tickers_df)
            
            return {
                "id": universe.id,
                "name": universe.name,
                "description": universe.description,
                "created_at": universe.created_at,
                "updated_at": universe.updated_at,
                "ticker_count": ticker_count
            }
            
        except Exception as e:
            logger.error(f"Error getting universe {universe_id}: {e}")
            raise
    
    def create_universe(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new universe."""
        try:
            # Check if universe already exists
            existing = self.db_manager.get_universe_by_name(name)
            if existing:
                raise ValueError(f"Universe '{name}' already exists")
            
            universe = Universe(
                name=name,
                description=description,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            universe_id = self.db_manager.store_universe(universe)
            
            return {
                "id": universe_id,
                "name": name,
                "description": description,
                "created_at": universe.created_at,
                "updated_at": universe.updated_at,
                "ticker_count": 0
            }
            
        except Exception as e:
            logger.error(f"Error creating universe: {e}")
            raise
    
    def update_universe(self, universe_id: int, name: Optional[str] = None, 
                       description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update an existing universe."""
        try:
            universe = self.db_manager.get_universe_by_id(universe_id)
            if universe is None:
                return None
            
            # Check if new name conflicts with existing universe
            if name and name != universe.name:
                existing = self.db_manager.get_universe_by_name(name)
                if existing:
                    raise ValueError(f"Universe '{name}' already exists")
            
            # Update fields
            if name:
                universe.name = name
            if description is not None:
                universe.description = description
            
            universe.updated_at = datetime.now()
            
            # Store updated universe
            self.db_manager.store_universe(universe)
            
            # Get ticker count
            tickers_df = self.db_manager.get_universe_tickers(universe_id)
            ticker_count = len(tickers_df)
            
            return {
                "id": universe.id,
                "name": universe.name,
                "description": universe.description,
                "created_at": universe.created_at,
                "updated_at": universe.updated_at,
                "ticker_count": ticker_count
            }
            
        except Exception as e:
            logger.error(f"Error updating universe {universe_id}: {e}")
            raise
    
    def delete_universe(self, universe_id: int) -> bool:
        """Delete a universe and all its tickers."""
        try:
            return self.db_manager.delete_universe(universe_id)
        except Exception as e:
            logger.error(f"Error deleting universe {universe_id}: {e}")
            raise
    
    def get_universe_tickers(self, universe_id: int) -> List[Dict[str, Any]]:
        """Get all tickers for a universe."""
        try:
            tickers_df = self.db_manager.get_universe_tickers(universe_id)
            
            if tickers_df.empty:
                return []
            
            tickers = []
            for _, row in tickers_df.iterrows():
                ticker_data = {
                    "id": int(row['id']),
                    "universe_id": int(row['universe_id']),
                    "ticker": str(row['ticker']),
                    "added_at": row['added_at'].isoformat() if pd.notna(row['added_at']) else None
                }
                tickers.append(ticker_data)
            
            return tickers
            
        except Exception as e:
            logger.error(f"Error getting tickers for universe {universe_id}: {e}")
            raise
    
    def update_universe_tickers(self, universe_id: int, tickers: List[str]) -> List[Dict[str, Any]]:
        """Update all tickers for a universe."""
        try:
            # Check if universe exists
            universe = self.db_manager.get_universe_by_id(universe_id)
            if universe is None:
                raise ValueError(f"Universe {universe_id} not found")
            
            # Remove all existing tickers
            self.db_manager.delete_all_universe_tickers(universe_id)
            
            # Add new tickers
            if tickers:
                universe_tickers = []
                for ticker in tickers:
                    universe_ticker = UniverseTicker(
                        universe_id=universe_id,
                        ticker=ticker.strip().upper(),
                        added_at=datetime.now()
                    )
                    universe_tickers.append(universe_ticker)
                
                self.db_manager.store_universe_tickers(universe_tickers)
            
            # Return updated ticker list
            return self.get_universe_tickers(universe_id)
            
        except Exception as e:
            logger.error(f"Error updating tickers for universe {universe_id}: {e}")
            raise
    
    def add_universe_ticker(self, universe_id: int, ticker: str) -> Dict[str, Any]:
        """Add a single ticker to a universe."""
        try:
            # Check if universe exists
            universe = self.db_manager.get_universe_by_id(universe_id)
            if universe is None:
                raise ValueError(f"Universe {universe_id} not found")
            
            universe_ticker = UniverseTicker(
                universe_id=universe_id,
                ticker=ticker.strip().upper(),
                added_at=datetime.now()
            )
            
            ticker_id = self.db_manager.store_universe_ticker(universe_ticker)
            
            return {
                "id": ticker_id,
                "universe_id": universe_id,
                "ticker": ticker.strip().upper(),
                "added_at": universe_ticker.added_at
            }
            
        except Exception as e:
            logger.error(f"Error adding ticker {ticker} to universe {universe_id}: {e}")
            raise
    
    def remove_universe_ticker(self, universe_id: int, ticker: str) -> bool:
        """Remove a ticker from a universe."""
        try:
            return self.db_manager.delete_universe_ticker(universe_id, ticker.strip().upper())
        except Exception as e:
            logger.error(f"Error removing ticker {ticker} from universe {universe_id}: {e}")
            raise
    
    def get_signals_raw(self, tickers: Optional[List[str]] = None, 
                       signal_names: Optional[List[str]] = None,
                       start_date: Optional[date] = None, 
                       end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get raw signals with optional filtering."""
        try:
            signals_df = self.db_manager.get_signals_raw(
                tickers=tickers,
                signal_names=signal_names,
                start_date=start_date,
                end_date=end_date
            )
            
            if signals_df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            signals = []
            for _, row in signals_df.iterrows():
                signal_data = {
                    "id": int(row.get('id')) if pd.notna(row.get('id')) else None,
                    "asof_date": row['asof_date'].isoformat() if pd.notna(row['asof_date']) else None,
                    "ticker": str(row['ticker']),
                    "signal_name": str(row['signal_name']),
                    "value": float(row['value']) if pd.notna(row['value']) else None,
                    "metadata": self._parse_json_field(row.get('metadata')),
                    "created_at": row['created_at'].isoformat() if pd.notna(row.get('created_at')) else None
                }
                signals.append(signal_data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting raw signals: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.db_manager:
            self.db_manager.disconnect()

