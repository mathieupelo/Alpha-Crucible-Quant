"""
Backtest, BacktestNav, and BacktestSignal database operations.

This module contains all database operations related to backtests.
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Optional
import pandas as pd
from psycopg2 import Error as PgError

from .models import Backtest, BacktestNav, BacktestSignal

logger = logging.getLogger(__name__)


class BacktestOperationsMixin:
    """Mixin class providing backtest-related database operations."""
    
    # Backtest Signal Operations
    
    def store_backtest_signals(self, backtest_signals: List[BacktestSignal]) -> int:
        """Store backtest-signal relationships."""
        if not backtest_signals:
            return 0
        
        query = """
        INSERT INTO backtest_signals (run_id, signal_id, weight, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (run_id, signal_id) DO UPDATE SET 
            weight = EXCLUDED.weight,
            created_at = EXCLUDED.created_at
        """
        
        params_list = []
        for bs in backtest_signals:
            params_list.append((
                bs.run_id,
                bs.signal_id,
                bs.weight,
                bs.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_backtest_signals(self, run_id: str) -> pd.DataFrame:
        """Get all signals associated with a backtest."""
        query = """
        SELECT bs.*, s.name as signal_name, s.description as signal_description, s.enabled
        FROM backtest_signals bs
        LEFT JOIN signals s ON bs.signal_id = s.id
        WHERE bs.run_id = %s
        ORDER BY COALESCE(s.name, bs.signal_id::text)
        """
        try:
            result = self.execute_query(query, (run_id,))
            if result.empty:
                logger.warning(f"No signals found for backtest {run_id} in backtest_signals table")
            else:
                # Check for orphaned records (signals without matching signal_id in signals table)
                orphaned = result[result['signal_name'].isna()]
                if not orphaned.empty:
                    logger.warning(f"Found {len(orphaned)} orphaned signal record(s) for backtest {run_id}: signal_ids={orphaned['signal_id'].tolist()}")
            return result
        except Exception as e:
            logger.error(f"Error executing get_backtest_signals query for {run_id}: {e}", exc_info=True)
            # Return empty DataFrame on error rather than raising
            return pd.DataFrame()
    
    def delete_backtest_signals(self, run_id: str) -> int:
        """Delete all signal relationships for a backtest."""
        query = "DELETE FROM backtest_signals WHERE run_id = %s"
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, (run_id,))
            self._connection.commit()
            return cursor.rowcount
        except PgError as e:
            logger.error(f"Error deleting backtest signals for {run_id}: {e}")
            self._connection.rollback()
            raise
        finally:
            cursor.close()
    
    # Backtest Operations
    
    def store_backtest(self, backtest: Backtest, signal_ids: Optional[List[int]] = None, signal_weights: Optional[Dict[int, float]] = None) -> int:
        """Store a backtest configuration in the database."""
        query = """
        INSERT INTO backtests (run_id, name, start_date, end_date, frequency, universe_id, universe, benchmark, params, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (run_id) DO UPDATE SET
            name = EXCLUDED.name,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            frequency = EXCLUDED.frequency,
            universe_id = EXCLUDED.universe_id,
            universe = EXCLUDED.universe,
            benchmark = EXCLUDED.benchmark,
            params = EXCLUDED.params,
            created_at = EXCLUDED.created_at
        RETURNING id
        """
        
        universe_json = None
        if backtest.universe:
            import json
            universe_json = json.dumps(backtest.universe)
        
        params_json = None
        if backtest.params:
            import json
            params_json = json.dumps(backtest.params)
        
        params = (
            backtest.run_id,
            backtest.name,
            backtest.start_date,
            backtest.end_date,
            backtest.frequency,
            backtest.universe_id,
            universe_json,
            backtest.benchmark,
            params_json,
            backtest.created_at or datetime.now()
        )
        
        backtest_id = self.execute_insert(query, params)
        
        # Store backtest-signal relationships if provided
        if signal_ids:
            backtest_signals = []
            for signal_id in signal_ids:
                weight = signal_weights.get(signal_id, 1.0) if signal_weights else 1.0
                backtest_signals.append(BacktestSignal(
                    run_id=backtest.run_id,
                    signal_id=signal_id,
                    weight=weight,
                    created_at=datetime.now()
                ))
            
            if backtest_signals:
                self.store_backtest_signals(backtest_signals)
        
        return backtest_id
    
    def get_backtests(self, run_id: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve backtests from the database."""
        query = "SELECT * FROM backtests WHERE 1=1"
        params = []
        
        if run_id:
            query += " AND run_id = %s"
            params.append(run_id)
        
        if start_date:
            query += " AND start_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND end_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def check_backtest_name_exists(self, name: str) -> bool:
        """Check if a backtest name already exists."""
        query = "SELECT COUNT(*) as count FROM backtests WHERE name = %s"
        result = self.execute_query(query, (name,))
        if result.empty:
            return False
        # Convert numpy int64 to Python int, then to bool
        count = int(result.iloc[0]['count'])
        return count > 0
    
    def get_backtest_by_run_id(self, run_id: str, include_signals: bool = True) -> Optional[Backtest]:
        """Get a specific backtest by run_id."""
        query = "SELECT * FROM backtests WHERE run_id = %s"
        df = self.execute_query(query, (run_id,))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        universe = None
        if row.get('universe'):
            import json
            try:
                universe = json.loads(row['universe'])
            except (json.JSONDecodeError, TypeError):
                universe = None
        
        params = None
        if row.get('params'):
            import json
            try:
                params = json.loads(row['params'])
            except (json.JSONDecodeError, TypeError):
                params = None
        
        backtest = Backtest(
            id=row['id'],
            run_id=row['run_id'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            frequency=row['frequency'],
            universe_id=row['universe_id'],
            name=row.get('name'),
            universe=universe,
            benchmark=row.get('benchmark'),
            params=params,
            created_at=row.get('created_at')
        )
        
        # Optionally include signal information in params
        if include_signals:
            signals_df = self.get_backtest_signals(run_id)
            if not signals_df.empty:
                if params is None:
                    params = {}
                params['signal_ids'] = signals_df['signal_id'].tolist()
                params['signal_weights'] = dict(zip(signals_df['signal_id'], signals_df['weight']))
                params['signal_names'] = signals_df['signal_name'].tolist()
                backtest.params = params
        
        return backtest
    
    # Backtest NAV Operations
    
    def store_backtest_nav(self, nav_data: List[BacktestNav]) -> int:
        """Store backtest NAV data in the database."""
        if not nav_data:
            return 0
        
        query = """
        INSERT INTO backtest_nav (run_id, date, nav, benchmark_nav, pnl, return_pct, benchmark_return_pct)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (run_id, date) DO UPDATE SET 
            nav = EXCLUDED.nav,
            benchmark_nav = EXCLUDED.benchmark_nav,
            pnl = EXCLUDED.pnl,
            return_pct = EXCLUDED.return_pct,
            benchmark_return_pct = EXCLUDED.benchmark_return_pct
        """
        
        params_list = []
        for nav in nav_data:
            params_list.append((
                nav.run_id,
                nav.date,
                nav.nav,
                nav.benchmark_nav,
                nav.pnl,
                nav.return_pct,
                nav.benchmark_return_pct
            ))
        
        return self.execute_many(query, params_list)
    
    def get_backtest_nav(self, run_id: Optional[str] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        starting_capital: Optional[float] = None) -> pd.DataFrame:
        """
        Retrieve backtest NAV data from the database.
        
        Args:
            run_id: Backtest run ID to filter by
            start_date: Start date filter
            end_date: End date filter
            starting_capital: Optional starting capital to reconstruct NAV values.
                             If provided, NAV will be calculated as: starting_capital * (1 + return_pct)
                             If None, uses original initial_capital from backtests.params
        
        Returns:
            DataFrame with NAV data. If starting_capital is provided, nav and benchmark_nav
            columns will be reconstructed using the new starting capital.
        """
        query = "SELECT * FROM backtest_nav WHERE 1=1"
        params = []
        
        if run_id:
            query += " AND run_id = %s"
            params.append(run_id)
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        # Optimize ORDER BY: if filtering by run_id, only need to order by date
        # The unique index on (run_id, date) will be used efficiently
        if run_id:
            query += " ORDER BY date"
        else:
            query += " ORDER BY run_id, date"
        
        nav_df = self.execute_query(query, tuple(params) if params else None)
        
        # If starting_capital is provided and we have return_pct, reconstruct NAV values
        if starting_capital is not None and not nav_df.empty and 'return_pct' in nav_df.columns:
            # Get original initial_capital from backtests.params if run_id is provided
            original_capital = None
            if run_id:
                backtest = self.get_backtest_by_run_id(run_id, include_signals=False)
                if backtest and backtest.params and 'initial_capital' in backtest.params:
                    original_capital = backtest.params['initial_capital']
            
            # If we don't have original_capital, use the first nav value as baseline
            if original_capital is None and not nav_df.empty:
                # Get first nav value (sorted by date)
                first_nav = nav_df.sort_values('date').iloc[0]['nav']
                if first_nav and first_nav > 0:
                    original_capital = first_nav
            
            # Default to 10000 if we still don't have a baseline
            if original_capital is None:
                original_capital = 10000.0
            
            # Reconstruct NAV: nav = starting_capital * (1 + return_pct)
            # But we need to adjust for the original baseline
            # If original baseline was 10000 and return_pct=0.15, then nav=11500
            # If new starting_capital=50000, new nav should be 50000 * (1 + 0.15) = 57500
            nav_df['nav'] = starting_capital * (1 + nav_df['return_pct'].fillna(0))
            
            # Reconstruct benchmark_nav if benchmark_return_pct exists
            if 'benchmark_return_pct' in nav_df.columns:
                nav_df['benchmark_nav'] = starting_capital * (1 + nav_df['benchmark_return_pct'].fillna(0))
        
        return nav_df

