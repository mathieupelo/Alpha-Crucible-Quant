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
import numpy as np
import logging

from src.database import DatabaseManager
from src.database.models import Signal, Backtest, BacktestNav, Portfolio, PortfolioPosition, SignalRaw, ScoreCombined, Universe, UniverseTicker

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
                        end_date: Optional[date] = None,
                        starting_capital: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get NAV data for a backtest.
        
        Args:
            run_id: Backtest run ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            starting_capital: Optional starting capital to reconstruct NAV values dynamically.
                           If provided, NAV will be calculated using the new starting capital.
                           If None, uses original initial_capital from backtests.params
        
        Returns:
            List of NAV records with reconstructed values if starting_capital is provided
        """
        try:
            nav_df = self.db_manager.get_backtest_nav(run_id, start_date, end_date, starting_capital)
            
            if nav_df.empty:
                logger.warning(f"No NAV data found in database for backtest {run_id}")
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
        """Get all portfolios for a backtest (optimized with batch fetching)."""
        try:
            portfolios_df = self.db_manager.get_portfolios(run_id=run_id)
            
            if portfolios_df.empty:
                return []
            
            portfolios = portfolios_df.to_dict('records')
            
            # Batch fetch all positions for all portfolios
            portfolio_ids = [int(p['id']) for p in portfolios]
            all_positions_df = self.db_manager.get_portfolio_positions(portfolio_ids=portfolio_ids)
            
            # Group positions by portfolio_id for quick lookup (more efficient than filtering in loop)
            positions_by_portfolio = {}
            if not all_positions_df.empty:
                grouped = all_positions_df.groupby('portfolio_id')
                for portfolio_id in portfolio_ids:
                    if portfolio_id in grouped.groups:
                        positions_by_portfolio[portfolio_id] = grouped.get_group(portfolio_id)
                    else:
                        positions_by_portfolio[portfolio_id] = pd.DataFrame()
            
            # Batch fetch all universes
            universe_ids = list(set(int(p.get('universe_id', 0)) for p in portfolios if p.get('universe_id')))
            universes_df = self.db_manager.get_universes_by_ids(universe_ids) if universe_ids else pd.DataFrame()
            
            # Create universe lookup dictionary
            universe_lookup = {}
            if not universes_df.empty:
                for _, row in universes_df.iterrows():
                    universe_lookup[int(row['id'])] = str(row['name'])
            
            # Process portfolios with pre-fetched data
            for portfolio in portfolios:
                portfolio['params'] = self._parse_json_field(portfolio.get('params'))
                
                # Get position count from pre-fetched data
                portfolio_id = int(portfolio['id'])
                positions_df = positions_by_portfolio.get(portfolio_id, pd.DataFrame())
                portfolio['position_count'] = len(positions_df)
                
                # Get universe name from pre-fetched data
                universe_id = portfolio.get('universe_id')
                if universe_id:
                    portfolio['universe_name'] = universe_lookup.get(int(universe_id), "Unknown Universe")
                else:
                    portfolio['universe_name'] = "Unknown Universe"
            
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
            
            # Get portfolio positions with company info
            positions_df = self.db_manager.get_portfolio_positions(portfolio_id)
            positions = []
            if not positions_df.empty:
                for _, row in positions_df.iterrows():
                    # Convert pandas Timestamp to Python datetime if needed
                    created_at = row['created_at']
                    if pd.notna(created_at) and hasattr(created_at, 'to_pydatetime'):
                        created_at = created_at.to_pydatetime()
                    
                    # Convert to dictionary directly for JSON serialization
                    position_dict = {
                        "id": int(row['id']),
                        "portfolio_id": int(row['portfolio_id']),
                        "ticker": str(row.get('main_ticker') or row['ticker']),  # Use main_ticker if available
                        "weight": float(row['weight']),
                        "price_used": float(row['price_used']),
                        "company_uid": str(row.get('company_uid')) if pd.notna(row.get('company_uid')) else None,
                        "company_name": str(row.get('company_name')) if pd.notna(row.get('company_name')) else None,
                        "main_ticker": str(row.get('main_ticker')) if pd.notna(row.get('main_ticker')) else None,
                        "created_at": created_at
                    }
                    positions.append(position_dict)
            
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
            
            # Get all universe companies instead of just portfolio positions
            companies_df = self.db_manager.get_universe_companies(portfolio.universe_id)
            if companies_df.empty:
                return []
            
            # Get company_uids from universe
            company_uids = companies_df['company_uid'].dropna().tolist()
            if not company_uids:
                return []
            
            # Get signal scores for the portfolio date and all universe companies
            signals_df = self.db_manager.get_signals_raw(
                company_uids=company_uids,
                start_date=portfolio.asof_date,
                end_date=portfolio.asof_date
            )
            
            signals = []
            available_signals = []
            
            # Prepare signals DataFrame for efficient lookup
            signals_df_copy = None
            if not signals_df.empty and 'company_uid' in signals_df.columns:
                # Create a copy and convert company_uid to string for comparison (once, not per iteration)
                signals_df_copy = signals_df.copy()
                signals_df_copy['company_uid'] = signals_df_copy['company_uid'].astype(str)
                
                # Get all unique signal names from the data
                if 'signal_name_display' in signals_df_copy.columns:
                    available_signals = signals_df_copy['signal_name_display'].dropna().unique().tolist()
                if not available_signals and 'signal_name' in signals_df_copy.columns:
                    available_signals = signals_df_copy['signal_name'].dropna().unique().tolist()
                # Convert to strings and ensure they're valid
                available_signals = [str(s) for s in available_signals if s]
            
            # Create signal data for ALL universe companies, not just those with data
            for _, company_row in companies_df.iterrows():
                company_uid = str(company_row['company_uid']) if pd.notna(company_row.get('company_uid')) else None
                if not company_uid:
                    continue
                    
                main_ticker = str(company_row['main_ticker']) if pd.notna(company_row.get('main_ticker')) else None
                company_name = str(company_row['company_name']) if pd.notna(company_row.get('company_name')) else None
                
                signal_data = {
                    'company_uid': company_uid,
                    'company_name': company_name,
                    'main_ticker': main_ticker,
                    'ticker': main_ticker,  # Keep for backward compatibility
                    'available_signals': available_signals
                }
                
                # Add signal values if they exist for this company
                if signals_df_copy is not None:
                    company_signals = signals_df_copy[signals_df_copy['company_uid'] == company_uid]
                    
                    for _, row in company_signals.iterrows():
                        # Get signal name safely
                        signal_name = None
                        if 'signal_name_display' in row.index and pd.notna(row.get('signal_name_display')):
                            signal_name = str(row['signal_name_display'])
                        elif 'signal_name' in row.index and pd.notna(row.get('signal_name')):
                            signal_name = str(row['signal_name'])
                        
                        if signal_name:
                            # Sanitize signal name for use as dictionary key (replace invalid chars)
                            signal_name_key = signal_name.replace(' ', '_').replace('-', '_').replace('.', '_')
                            # Get value safely
                            value = None
                            if 'value' in row.index and pd.notna(row.get('value')):
                                try:
                                    value = float(row['value'])
                                except (ValueError, TypeError):
                                    value = None
                            signal_data[signal_name_key] = value
                
                signals.append(signal_data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting signals for portfolio {portfolio_id}: {e}", exc_info=True)
            raise
    
    def get_portfolio_scores(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Get combined scores for a specific portfolio."""
        try:
            # Get portfolio details to get the date and universe
            portfolio = self.db_manager.get_portfolio_by_id(portfolio_id)
            if portfolio is None:
                return []
            
            # Get all universe companies instead of just portfolio positions
            companies_df = self.db_manager.get_universe_companies(portfolio.universe_id)
            if companies_df.empty:
                return []
            
            # Get company_uids from universe
            company_uids = companies_df['company_uid'].dropna().tolist()
            if not company_uids:
                return []
            
            # Get combined scores for the portfolio date and all universe companies
            scores_df = self.db_manager.get_scores_combined(
                company_uids=company_uids,
                start_date=portfolio.asof_date,
                end_date=portfolio.asof_date
            )
            
            scores = []
            
            # Prepare scores DataFrame for efficient lookup
            scores_df_copy = None
            if not scores_df.empty and 'company_uid' in scores_df.columns:
                # Create a copy and convert company_uid to string for comparison (once, not per iteration)
                scores_df_copy = scores_df.copy()
                scores_df_copy['company_uid'] = scores_df_copy['company_uid'].astype(str)
            
            # Create score data for ALL universe companies, not just those with data
            for _, company_row in companies_df.iterrows():
                company_uid = str(company_row['company_uid']) if pd.notna(company_row.get('company_uid')) else None
                if not company_uid:
                    continue
                    
                main_ticker = str(company_row['main_ticker']) if pd.notna(company_row.get('main_ticker')) else None
                company_name = str(company_row['company_name']) if pd.notna(company_row.get('company_name')) else None
                
                score_data = {
                    'company_uid': company_uid,
                    'company_name': company_name,
                    'main_ticker': main_ticker,
                    'ticker': main_ticker,  # Keep for backward compatibility
                    'combined_score': None,
                    'method': None
                }
                
                # Add score data if it exists for this company
                if scores_df_copy is not None:
                    company_scores = scores_df_copy[scores_df_copy['company_uid'] == company_uid]
                    if not company_scores.empty:
                        row = company_scores.iloc[0]
                        if 'score' in row.index and pd.notna(row.get('score')):
                            try:
                                score_data['combined_score'] = float(row['score'])
                            except (ValueError, TypeError):
                                score_data['combined_score'] = None
                        if 'method' in row.index and pd.notna(row.get('method')):
                            score_data['method'] = str(row['method'])
                
                scores.append(score_data)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error getting scores for portfolio {portfolio_id}: {e}", exc_info=True)
            raise
    
    def get_backtest_signals(self, run_id: str, start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get raw signals for a backtest period, filtered to only signals used in this backtest."""
        try:
            # Check if backtest exists
            backtest = self.db_manager.get_backtest_by_run_id(run_id)
            if backtest is None:
                return []
            
            # Get the signals that were actually used for this backtest from backtest_signals table
            backtest_signals_df = self.db_manager.get_backtest_signals(run_id)
            
            if backtest_signals_df.empty:
                logger.warning(f"No signals found in backtest_signals table for run_id: {run_id}")
                return []
            
            # Extract signal IDs directly (more reliable than name lookup)
            signal_ids = []
            if 'signal_id' in backtest_signals_df.columns:
                # Convert numpy types to native Python ints to avoid database adapter issues
                signal_ids = [int(sid) for sid in backtest_signals_df['signal_id'].unique().tolist()]
            
            # Also extract signal names for logging
            signal_names = []
            if 'signal_name' in backtest_signals_df.columns:
                signal_names = backtest_signals_df['signal_name'].unique().tolist()
            
            if not signal_ids:
                logger.warning(f"Could not extract signal IDs from backtest_signals for run_id: {run_id}. Columns: {list(backtest_signals_df.columns)}")
                return []
            
            logger.info(f"Found {len(signal_ids)} unique signal(s) for backtest {run_id}: signal_ids={signal_ids}, names={signal_names}")
            
            # Get date range if not provided
            if start_date is None:
                start_date = backtest.start_date
            if end_date is None:
                end_date = backtest.end_date
            
            # Get universe companies for this backtest
            companies_df = self.db_manager.get_universe_companies(backtest.universe_id)
            company_uids = companies_df['company_uid'].dropna().tolist() if not companies_df.empty else []
            
            # Get signal raw data filtered by signal IDs (more reliable than names)
            signals_df = self.db_manager.get_signals_raw(
                company_uids=company_uids if company_uids else None,
                signal_ids=signal_ids,  # Use signal_ids instead of signal_names for more reliable filtering
                start_date=start_date,
                end_date=end_date
            )
            
            logger.info(f"Retrieved {len(signals_df)} signal records after filtering by signal_ids={signal_ids}")
            
            if signals_df.empty:
                return []

            # Normalize signal name field to avoid mixed naming in frontend
            signal_records = signals_df.to_dict('records')
            for rec in signal_records:
                # Prefer joined signal name over raw table column
                if 'signal_name_display' in rec and rec['signal_name_display']:
                    rec['signal_name'] = rec['signal_name_display']
            return signal_records
            
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

    def get_backtest_used_signals(self, run_id: str) -> List[Dict[str, Any]]:
        """Return the list of signals explicitly associated with a backtest (by run_id).
        
        Fetches all signals from backtest_signals table and joins with signals table
        to return the name and description of each signal.
        """
        try:
            # Get backtest signals with join to signals table
            # get_backtest_signals already performs: SELECT bs.*, s.name as signal_name, s.description as signal_description
            # FROM backtest_signals bs LEFT JOIN signals s ON bs.signal_id = s.id WHERE bs.run_id = %s
            df = self.db_manager.get_backtest_signals(run_id)
            if df.empty:
                logger.info(f"No backtest_signals records found for run_id: {run_id}")
                return []
            
            # Get unique signal_ids and their corresponding name/description
            result = []
            seen_signal_ids = set()
            
            for _, row in df.iterrows():
                signal_id = int(row['signal_id']) if pd.notna(row['signal_id']) else None
                if signal_id is None or signal_id in seen_signal_ids:
                    continue
                
                seen_signal_ids.add(signal_id)
                
                # Extract name from joined signals table (signal_name column)
                name = None
                if 'signal_name' in row and pd.notna(row['signal_name']):
                    name = str(row['signal_name']).strip()
                
                # Extract description from joined signals table (signal_description column)
                description = None
                if 'signal_description' in row and pd.notna(row['signal_description']):
                    description = str(row['signal_description']).strip()
                
                result.append({
                    'signal_id': signal_id,
                    'name': name if name else f"SIGNAL_{signal_id}",
                    'description': description
                })
            
            logger.info(f"Successfully retrieved {len(result)} unique signal(s) for backtest {run_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting used signals for {run_id}: {e}", exc_info=True)
            raise
    
    def get_backtest_metrics(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Calculate backtest performance metrics."""
        try:
            # Get NAV data
            nav_data = self.get_backtest_nav(run_id)
            if not nav_data:
                logger.warning(f"No NAV data found for backtest {run_id}")
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
            
            # Alpha, Beta, Information Ratio - Calculate from benchmark NAV if available
            alpha = 0.0
            beta = 1.0
            information_ratio = 0.0
            tracking_error = 0.0
            
            # Check if we have benchmark NAV data
            if 'benchmark_nav' in nav_df.columns:
                benchmark_nav = nav_df['benchmark_nav'].dropna()
                
                # Only calculate if we have sufficient benchmark data
                if len(benchmark_nav) >= 2 and len(nav_series) >= 2:
                    # Align portfolio and benchmark data
                    aligned_data = pd.DataFrame({
                        'portfolio': nav_series,
                        'benchmark': benchmark_nav
                    }).dropna()
                    
                    if len(aligned_data) >= 2:
                        # Calculate returns for both portfolio and benchmark
                        portfolio_returns = aligned_data['portfolio'].pct_change().dropna()
                        benchmark_returns = aligned_data['benchmark'].pct_change().dropna()
                        
                        # Align returns
                        aligned_returns = pd.DataFrame({
                            'portfolio': portfolio_returns,
                            'benchmark': benchmark_returns
                        }).dropna()
                        
                        if len(aligned_returns) >= 2:
                            port_ret = aligned_returns['portfolio']
                            bench_ret = aligned_returns['benchmark']
                            
                            # Calculate excess returns
                            excess_returns = port_ret - bench_ret
                            
                            # Calculate alpha (annualized excess return)
                            alpha = excess_returns.mean() * 252 * 100  # Convert to percentage
                            
                            # Calculate beta (covariance / variance)
                            if bench_ret.var() > 0:
                                beta = np.cov(port_ret, bench_ret)[0, 1] / bench_ret.var()
                            else:
                                beta = 1.0
                            
                            # Calculate information ratio (annualized)
                            if excess_returns.std() > 0:
                                information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
                            else:
                                information_ratio = 0.0
                            
                            # Calculate tracking error (annualized standard deviation of excess returns)
                            tracking_error = excess_returns.std() * np.sqrt(252) * 100  # Convert to percentage
            
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
                # Get company count for each universe (using universe_companies)
                companies_df = self.db_manager.get_universe_companies(int(row['id']))
                company_count = len(companies_df)
                
                universe_data = {
                    "id": int(row['id']),
                    "name": str(row['name']),
                    "description": str(row.get('description')) if pd.notna(row.get('description')) else None,
                    "created_at": row['created_at'].isoformat() if pd.notna(row['created_at']) else None,
                    "updated_at": row['updated_at'].isoformat() if pd.notna(row['updated_at']) else None,
                    "ticker_count": company_count  # Keep for backward compatibility, but it's actually company count
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
            
            # Get company count (using universe_companies)
            companies_df = self.db_manager.get_universe_companies(universe_id)
            company_count = len(companies_df)
            
            return {
                "id": universe.id,
                "name": universe.name,
                "description": universe.description,
                "created_at": universe.created_at,
                "updated_at": universe.updated_at,
                "ticker_count": company_count  # Keep for backward compatibility, but it's actually company count
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
                "ticker_count": 0  # Keep for backward compatibility, but it's actually company count
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
            
            # Use the new name or keep the existing one
            updated_name = name if name else universe.name
            updated_description = description if description is not None else universe.description
            
            # Update the universe in the database
            success = self.db_manager.update_universe(
                universe_id=universe_id,
                name=updated_name,
                description=updated_description,
                updated_at=datetime.now()
            )
            
            if not success:
                raise ValueError(f"Failed to update universe {universe_id}")
            
            # Get the updated universe
            updated_universe = self.db_manager.get_universe_by_id(universe_id)
            if updated_universe is None:
                raise ValueError(f"Failed to retrieve updated universe {universe_id}")
            
            # Get company count (using universe_companies)
            companies_df = self.db_manager.get_universe_companies(universe_id)
            company_count = len(companies_df)
            
            return {
                "id": updated_universe.id,
                "name": updated_universe.name,
                "description": updated_universe.description,
                "created_at": updated_universe.created_at,
                "updated_at": updated_universe.updated_at,
                "ticker_count": company_count  # Keep for backward compatibility, but it's actually company count
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
    
    def get_universe_companies(self, universe_id: int) -> List[Dict[str, Any]]:
        """Get all companies for a universe with company info and tickers."""
        try:
            companies_df = self.db_manager.get_universe_companies(universe_id)
            
            if companies_df.empty:
                return []
            
            companies = []
            for _, row in companies_df.iterrows():
                # Handle all_tickers array (PostgreSQL array)
                all_tickers = row.get('all_tickers', [])
                if isinstance(all_tickers, str):
                    # If it's a string representation of array, parse it
                    import re
                    all_tickers = re.findall(r'"([^"]+)"', all_tickers) if all_tickers else []
                elif pd.isna(all_tickers):
                    all_tickers = []
                
                company_data = {
                    "id": int(row['id']),
                    "universe_id": int(row['universe_id']),
                    "company_uid": str(row['company_uid']),
                    "company_name": str(row['company_name']) if pd.notna(row.get('company_name')) else None,
                    "main_ticker": str(row['main_ticker']) if pd.notna(row.get('main_ticker')) else None,
                    "all_tickers": all_tickers if isinstance(all_tickers, list) else list(all_tickers) if all_tickers else [],
                    "added_at": row['added_at'].isoformat() if pd.notna(row['added_at']) else None
                }
                companies.append(company_data)
            
            return companies
            
        except Exception as e:
            logger.error(f"Error getting companies for universe {universe_id}: {e}")
            raise
    
    def get_universe_tickers(self, universe_id: int) -> List[Dict[str, Any]]:
        """Get all tickers for a universe (DEPRECATED - use get_universe_companies instead)."""
        try:
            # Use universe_companies and extract main tickers
            companies_df = self.db_manager.get_universe_companies(universe_id)
            
            if companies_df.empty:
                return []
            
            tickers = []
            for _, row in companies_df.iterrows():
                main_ticker = row.get('main_ticker')
                if pd.notna(main_ticker):
                    ticker_data = {
                        "id": int(row['id']),
                        "universe_id": int(row['universe_id']),
                        "ticker": str(main_ticker),
                        "added_at": row['added_at'].isoformat() if pd.notna(row['added_at']) else None
                    }
                    tickers.append(ticker_data)
            
            return tickers
            
        except Exception as e:
            logger.error(f"Error getting tickers for universe {universe_id}: {e}")
            raise
    
    def update_universe_companies(self, universe_id: int, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Update all companies for a universe (accepts tickers, auto-resolves to companies).
        
        Args:
            universe_id: Universe ID
            tickers: List of ticker symbols (will be resolved to company_uid)
            
        Returns:
            List of company dictionaries with company info
        """
        try:
            from src.database.models import UniverseCompany
            
            # Check if universe exists
            universe = self.db_manager.get_universe_by_id(universe_id)
            if universe is None:
                raise ValueError(f"Universe {universe_id} not found")
            
            # Remove all existing companies
            self.db_manager.delete_all_universe_companies(universe_id)
            
            # Resolve tickers to company_uids and add companies
            if tickers:
                universe_companies = []
                for ticker in tickers:
                    try:
                        # Resolve ticker to company_uid
                        company_uid = self.db_manager.resolve_ticker_to_company_uid(ticker.strip().upper())
                        
                        universe_company = UniverseCompany(
                            universe_id=universe_id,
                            company_uid=company_uid,
                            added_at=datetime.now()
                        )
                        universe_companies.append(universe_company)
                    except ValueError as e:
                        logger.warning(f"Ticker {ticker} not found in Varrock, skipping: {e}")
                        continue
                
                if universe_companies:
                    self.db_manager.store_universe_companies(universe_companies)
            
            # Return updated company list
            return self.get_universe_companies(universe_id)
            
        except Exception as e:
            logger.error(f"Error updating companies for universe {universe_id}: {e}")
            raise
    
    def update_universe_tickers(self, universe_id: int, tickers: List[str]) -> List[Dict[str, Any]]:
        """Update all tickers for a universe (DEPRECATED - use update_universe_companies instead)."""
        return self.update_universe_companies(universe_id, tickers)
    
    def add_universe_company(self, universe_id: int, ticker: str) -> Dict[str, Any]:
        """
        Add a single company to a universe (accepts ticker, auto-resolves to company).
        
        Args:
            universe_id: Universe ID
            ticker: Ticker symbol (will be resolved to company_uid)
            
        Returns:
            Company dictionary with company info
        """
        try:
            from src.database.models import UniverseCompany
            
            # Check if universe exists
            universe = self.db_manager.get_universe_by_id(universe_id)
            if universe is None:
                raise ValueError(f"Universe {universe_id} not found")
            
            # Resolve ticker to company_uid
            company_uid = self.db_manager.resolve_ticker_to_company_uid(ticker.strip().upper())
            
            universe_company = UniverseCompany(
                universe_id=universe_id,
                company_uid=company_uid,
                added_at=datetime.now()
            )
            
            company_id = self.db_manager.store_universe_company(universe_company)
            
            # Get full company info
            companies = self.get_universe_companies(universe_id)
            for company in companies:
                if company['company_uid'] == company_uid:
                    return company
            
            # Fallback if not found
            return {
                "id": company_id,
                "universe_id": universe_id,
                "company_uid": company_uid,
                "company_name": None,
                "main_ticker": ticker.strip().upper(),
                "all_tickers": [ticker.strip().upper()],
                "added_at": universe_company.added_at.isoformat() if universe_company.added_at else None
            }
            
        except Exception as e:
            logger.error(f"Error adding company (ticker {ticker}) to universe {universe_id}: {e}")
            raise
    
    def add_universe_ticker(self, universe_id: int, ticker: str) -> Dict[str, Any]:
        """Add a single ticker to a universe (DEPRECATED - use add_universe_company instead)."""
        return self.add_universe_company(universe_id, ticker)
    
    def remove_universe_company(self, universe_id: int, company_uid: str) -> bool:
        """Remove a company from a universe."""
        try:
            return self.db_manager.delete_universe_company(universe_id, company_uid)
        except Exception as e:
            logger.error(f"Error removing company {company_uid} from universe {universe_id}: {e}")
            raise
    
    def remove_universe_ticker(self, universe_id: int, ticker: str) -> bool:
        """Remove a ticker from a universe (DEPRECATED - use remove_universe_company instead)."""
        try:
            # Resolve ticker to company_uid first
            company_uid = self.db_manager.resolve_ticker_to_company_uid(ticker.strip().upper())
            return self.remove_universe_company(universe_id, company_uid)
        except Exception as e:
            logger.error(f"Error removing ticker {ticker} from universe {universe_id}: {e}")
            raise
    
    def get_all_signals(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get all signal definitions."""
        try:
            signals_df = self.db_manager.get_all_signals(enabled_only=enabled_only)
            
            if signals_df.empty:
                return []
            
            signals = []
            for _, row in signals_df.iterrows():
                signal_data = {
                    "id": int(row['id']),
                    "name": str(row['name']),
                    "description": str(row.get('description')) if pd.notna(row.get('description')) else None,
                    "enabled": bool(row.get('enabled', True)),
                    "parameters": self._parse_json_field(row.get('parameters')),
                    "created_at": row['created_at'].isoformat() if pd.notna(row.get('created_at')) else None,
                    "updated_at": row['updated_at'].isoformat() if pd.notna(row.get('updated_at')) else None
                }
                signals.append(signal_data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            raise
    
    def get_signal_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a signal definition by name."""
        try:
            signal = self.db_manager.get_signal_by_name(name)
            if signal is None:
                return None
            
            return {
                "id": signal.id,
                "name": signal.name,
                "description": signal.description,
                "enabled": signal.enabled,
                "parameters": signal.parameters,
                "created_at": signal.created_at.isoformat() if signal.created_at else None,
                "updated_at": signal.updated_at.isoformat() if signal.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting signal {name}: {e}")
            raise
    
    def get_signals_raw(self, tickers: Optional[List[str]] = None, 
                       signal_names: Optional[List[str]] = None,
                       signal_ids: Optional[List[int]] = None,
                       company_uids: Optional[List[str]] = None,
                       start_date: Optional[date] = None, 
                       end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get raw signals with optional filtering and company information."""
        try:
            signals_df = self.db_manager.get_signals_raw(
                tickers=tickers,
                signal_names=signal_names,
                signal_ids=signal_ids,
                company_uids=company_uids,
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
                    "ticker": str(row.get('main_ticker') or row['ticker']),  # Use main_ticker if available
                    "signal_id": int(row['signal_id']) if pd.notna(row.get('signal_id')) else None,
                    "signal_name": str(row.get('signal_name_display') or row.get('signal_name', '')) if pd.notna(row.get('signal_name_display') or row.get('signal_name')) else None,
                    "value": float(row['value']) if pd.notna(row['value']) else None,
                    "metadata": self._parse_json_field(row.get('metadata')),
                    "company_uid": str(row.get('company_uid')) if pd.notna(row.get('company_uid')) else None,
                    "company_name": str(row.get('company_name')) if pd.notna(row.get('company_name')) else None,
                    "main_ticker": str(row.get('main_ticker')) if pd.notna(row.get('main_ticker')) else None,
                    "created_at": row['created_at'].isoformat() if pd.notna(row.get('created_at')) else None
                }
                signals.append(signal_data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting raw signals: {e}")
            raise
    
    def delete_backtest(self, run_id: str) -> bool:
        """Delete a backtest and all associated data."""
        try:
            # Check if backtest exists
            backtest = self.get_backtest_by_run_id(run_id)
            if backtest is None:
                logger.warning(f"Backtest {run_id} not found for deletion")
                return False
            
            # Delete in order to respect foreign key constraints:
            # 1. Portfolio positions (references portfolios)
            # 2. Portfolios (references backtests via run_id)
            # 3. Backtest NAV data (references backtests via run_id)
            # 4. Backtest itself
            
            # Delete portfolio positions for all portfolios of this backtest
            portfolios = self.get_backtest_portfolios(run_id)
            for portfolio in portfolios:
                portfolio_id = portfolio.get('id')
                if portfolio_id:
                    self.db_manager.execute_query(
                        "DELETE FROM portfolio_positions WHERE portfolio_id = %s",
                        (portfolio_id,)
                    )
            
            # Delete portfolios for this backtest
            self.db_manager.execute_query(
                "DELETE FROM portfolios WHERE run_id = %s",
                (run_id,)
            )
            
            # Delete NAV data for this backtest
            self.db_manager.execute_query(
                "DELETE FROM backtest_nav WHERE run_id = %s",
                (run_id,)
            )
            
            # Delete the backtest itself
            self.db_manager.execute_query(
                "DELETE FROM backtests WHERE run_id = %s",
                (run_id,)
            )
            
            logger.info(f"Successfully deleted backtest {run_id} and all associated data")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting backtest {run_id}: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.db_manager:
            self.db_manager.disconnect()

