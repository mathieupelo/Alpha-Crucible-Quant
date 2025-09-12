"""
Database manager for the Quant Project system.

Provides a simplified interface to MySQL database operations using pandas DataFrames.
"""

import os
import logging
from datetime import date, datetime
from typing import List, Dict, Optional, Any
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from .models import SignalRaw, ScoreCombined, Portfolio, PortfolioPosition, Backtest, BacktestNav, Universe, UniverseTicker, DataFrameConverter
from utils.error_handling import handle_database_errors, retry_on_failure

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations for the Quant Project system."""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, 
                 user: Optional[str] = None, password: Optional[str] = None, 
                 database: Optional[str] = None):
        """Initialize database manager with connection parameters."""
        self.host = host or os.getenv('DB_HOST', '127.0.0.1')
        self.port = port or int(os.getenv('DB_PORT', '3306'))
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.database = database or os.getenv('DB_NAME', 'signal_forge')
        self._connection = None
    
    def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            if self._connection.is_connected():
                logger.info(f"Connected to MySQL database: {self.database}")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
        return False
    
    def disconnect(self):
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.info("MySQL connection closed")
    
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self._connection and self._connection.is_connected()
    
    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary."""
        if not self.is_connected():
            self.connect()
    
    @handle_database_errors
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute a SELECT query and return results as DataFrame."""
        self.ensure_connection()
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                return pd.DataFrame()
            
            return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"Database error in execute_query: {e}")
            return pd.DataFrame()
    
    def execute_insert(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT query and return the last insert ID."""
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params)
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error executing insert: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute a query with multiple parameter sets."""
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.executemany(query, params_list)
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error executing batch insert: {e}")
            raise
        finally:
            cursor.close()
    
    # Signal Raw Operations
    
    def store_signals_raw(self, signals: List[SignalRaw]) -> int:
        """Store raw signals in the database."""
        if not signals:
            return 0
        
        query = """
        INSERT INTO signals_raw (asof_date, ticker, signal_name, value, metadata, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            value = VALUES(value),
            metadata = VALUES(metadata),
            created_at = VALUES(created_at)
        """
        
        params_list = []
        for signal in signals:
            metadata_json = None
            if signal.metadata:
                import json
                metadata_json = json.dumps(signal.metadata)
            
            params_list.append((
                signal.asof_date,
                signal.ticker,
                signal.signal_name,
                signal.value,
                metadata_json,
                signal.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_signals_raw(self, tickers: Optional[List[str]] = None,
                       signal_names: Optional[List[str]] = None,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve raw signals from the database."""
        query = "SELECT * FROM signals_raw WHERE 1=1"
        params = []
        
        if tickers:
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND ticker IN ({placeholders})"
            params.extend(tickers)
        
        if signal_names:
            placeholders = ','.join(['%s'] * len(signal_names))
            query += f" AND signal_name IN ({placeholders})"
            params.extend(signal_names)
        
        if start_date:
            query += " AND asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY asof_date, ticker, signal_name"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    # Score Combined Operations
    
    def store_scores_combined(self, scores: List[ScoreCombined]) -> int:
        """Store combined scores in the database."""
        if not scores:
            return 0
        
        query = """
        INSERT INTO scores_combined (asof_date, ticker, score, method, params, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            score = VALUES(score),
            method = VALUES(method),
            params = VALUES(params),
            created_at = VALUES(created_at)
        """
        
        params_list = []
        for score in scores:
            params_json = None
            if score.params:
                import json
                params_json = json.dumps(score.params)
            
            params_list.append((
                score.asof_date,
                score.ticker,
                score.score,
                score.method,
                params_json,
                score.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_scores_combined(self, tickers: Optional[List[str]] = None,
                           methods: Optional[List[str]] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve combined scores from the database."""
        query = "SELECT * FROM scores_combined WHERE 1=1"
        params = []
        
        if tickers:
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND ticker IN ({placeholders})"
            params.extend(tickers)
        
        if methods:
            placeholders = ','.join(['%s'] * len(methods))
            query += f" AND method IN ({placeholders})"
            params.extend(methods)
        
        if start_date:
            query += " AND asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY asof_date, ticker, method"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_scores_combined_pivot(self, tickers: List[str], methods: List[str],
                                 start_date: date, end_date: date, 
                                 forward_fill: bool = True) -> pd.DataFrame:
        """Get combined scores as a pivot table (date x ticker x method)."""
        df = self.get_scores_combined(tickers, methods, start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Create pivot table with date as index, ticker-method as columns
        pivot_df = df.pivot_table(
            index='asof_date',
            columns=['ticker', 'method'],
            values='score',
            aggfunc='first'
        )
        
        # Forward fill missing values if requested
        if forward_fill and not pivot_df.empty:
            pivot_df = pivot_df.ffill()
        
        return pivot_df
    
    # Portfolio Operations
    
    def store_portfolio(self, portfolio: Portfolio) -> int:
        """Store a portfolio in the database."""
        query = """
        INSERT INTO portfolios (run_id, universe_id, asof_date, method, params, cash, notes, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            universe_id = VALUES(universe_id),
            method = VALUES(method),
            params = VALUES(params),
            cash = VALUES(cash),
            notes = VALUES(notes),
            created_at = VALUES(created_at)
        """
        
        params_json = None
        if portfolio.params:
            import json
            params_json = json.dumps(portfolio.params)
        
        params = (
            portfolio.run_id,
            portfolio.universe_id,
            portfolio.asof_date,
            portfolio.method,
            params_json,
            portfolio.cash,
            portfolio.notes,
            portfolio.created_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_portfolios(self, run_id: Optional[str] = None,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve portfolios from the database."""
        query = "SELECT * FROM portfolios WHERE 1=1"
        params = []
        
        if run_id:
            query += " AND run_id = %s"
            params.append(run_id)
        
        if start_date:
            query += " AND asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY asof_date"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_portfolio_by_id(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio by ID."""
        query = "SELECT * FROM portfolios WHERE id = %s"
        df = self.execute_query(query, (portfolio_id,))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        params = None
        if row.get('params'):
            import json
            try:
                params = json.loads(row['params'])
            except (json.JSONDecodeError, TypeError):
                params = None
        
        return Portfolio(
            id=int(row['id']),
            run_id=str(row['run_id']),
            universe_id=int(row['universe_id']),
            asof_date=row['asof_date'],
            method=str(row['method']),
            params=params,
            cash=float(row.get('cash', 0.0)),
            notes=str(row.get('notes')) if pd.notna(row.get('notes')) else None,
            created_at=row.get('created_at')
        )
    
    # Portfolio Position Operations
    
    def store_portfolio_positions(self, positions: List[PortfolioPosition]) -> int:
        """Store portfolio positions in the database."""
        if not positions:
            return 0
        
        query = """
        INSERT INTO portfolio_positions (portfolio_id, ticker, weight, price_used, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            weight = VALUES(weight),
            price_used = VALUES(price_used),
            created_at = VALUES(created_at)
        """
        
        params_list = []
        for position in positions:
            params_list.append((
                position.portfolio_id,
                position.ticker,
                position.weight,
                position.price_used,
                position.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_portfolio_positions(self, portfolio_id: Optional[int] = None,
                               tickers: Optional[List[str]] = None) -> pd.DataFrame:
        """Retrieve portfolio positions from the database."""
        query = "SELECT * FROM portfolio_positions WHERE 1=1"
        params = []
        
        if portfolio_id:
            query += " AND portfolio_id = %s"
            params.append(portfolio_id)
        
        if tickers:
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND ticker IN ({placeholders})"
            params.extend(tickers)
        
        query += " ORDER BY portfolio_id, ticker"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    # Backtest Operations
    
    def store_backtest(self, backtest: Backtest) -> int:
        """Store a backtest configuration in the database."""
        query = """
        INSERT INTO backtests (run_id, name, start_date, end_date, frequency, universe_id, universe, benchmark, params, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            start_date = VALUES(start_date),
            end_date = VALUES(end_date),
            frequency = VALUES(frequency),
            universe_id = VALUES(universe_id),
            universe = VALUES(universe),
            benchmark = VALUES(benchmark),
            params = VALUES(params),
            created_at = VALUES(created_at)
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
        
        return self.execute_insert(query, params)
    
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
    
    def get_backtest_by_run_id(self, run_id: str) -> Optional[Backtest]:
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
        
        return Backtest(
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
    
    # Backtest NAV Operations
    
    def store_backtest_nav(self, nav_data: List[BacktestNav]) -> int:
        """Store backtest NAV data in the database."""
        if not nav_data:
            return 0
        
        query = """
        INSERT INTO backtest_nav (run_id, date, nav, benchmark_nav, pnl)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            nav = VALUES(nav),
            benchmark_nav = VALUES(benchmark_nav),
            pnl = VALUES(pnl)
        """
        
        params_list = []
        for nav in nav_data:
            params_list.append((
                nav.run_id,
                nav.date,
                nav.nav,
                nav.benchmark_nav,
                nav.pnl
            ))
        
        return self.execute_many(query, params_list)
    
    def get_backtest_nav(self, run_id: Optional[str] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve backtest NAV data from the database."""
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
        
        query += " ORDER BY run_id, date"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    # Universe Operations
    
    def store_universe(self, universe: Universe) -> int:
        """Store a universe in the database."""
        query = """
        INSERT INTO universes (name, description, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            description = VALUES(description),
            updated_at = VALUES(updated_at)
        """
        
        params = (
            universe.name,
            universe.description,
            universe.created_at or datetime.now(),
            universe.updated_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_universes(self) -> pd.DataFrame:
        """Retrieve all universes from the database."""
        query = "SELECT * FROM universes ORDER BY created_at DESC"
        return self.execute_query(query)
    
    def get_universe_by_id(self, universe_id: int) -> Optional[Universe]:
        """Get a specific universe by ID."""
        query = "SELECT * FROM universes WHERE id = %s"
        df = self.execute_query(query, (int(universe_id),))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        return Universe(
            id=row['id'],
            name=row['name'],
            description=row.get('description'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def get_universe_by_name(self, name: str) -> Optional[Universe]:
        """Get a specific universe by name."""
        query = "SELECT * FROM universes WHERE name = %s"
        df = self.execute_query(query, (name,))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        return Universe(
            id=row['id'],
            name=row['name'],
            description=row.get('description'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def delete_universe(self, universe_id: int) -> bool:
        """Delete a universe and all its tickers."""
        query = "DELETE FROM universes WHERE id = %s"
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, (universe_id,))
            return cursor.rowcount > 0
        except Error as e:
            logger.error(f"Error deleting universe {universe_id}: {e}")
            raise
        finally:
            cursor.close()
    
    # Universe Ticker Operations
    
    def store_universe_ticker(self, ticker: UniverseTicker) -> int:
        """Store a ticker in a universe."""
        query = """
        INSERT INTO universe_tickers (universe_id, ticker, added_at)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            added_at = VALUES(added_at)
        """
        
        params = (
            ticker.universe_id,
            ticker.ticker,
            ticker.added_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def store_universe_tickers(self, tickers: List[UniverseTicker]) -> int:
        """Store multiple tickers in a universe."""
        if not tickers:
            return 0
        
        query = """
        INSERT INTO universe_tickers (universe_id, ticker, added_at)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            added_at = VALUES(added_at)
        """
        
        params_list = []
        for ticker in tickers:
            params_list.append((
                ticker.universe_id,
                ticker.ticker,
                ticker.added_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_universe_tickers(self, universe_id: int) -> pd.DataFrame:
        """Get all tickers for a universe."""
        query = "SELECT * FROM universe_tickers WHERE universe_id = %s ORDER BY ticker"
        return self.execute_query(query, (universe_id,))
    
    def delete_universe_ticker(self, universe_id: int, ticker: str) -> bool:
        """Delete a ticker from a universe."""
        query = "DELETE FROM universe_tickers WHERE universe_id = %s AND ticker = %s"
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, (universe_id, ticker))
            return cursor.rowcount > 0
        except Error as e:
            logger.error(f"Error deleting ticker {ticker} from universe {universe_id}: {e}")
            raise
        finally:
            cursor.close()
    
    def delete_all_universe_tickers(self, universe_id: int) -> int:
        """Delete all tickers from a universe."""
        query = "DELETE FROM universe_tickers WHERE universe_id = %s"
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, (universe_id,))
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error deleting all tickers from universe {universe_id}: {e}")
            raise
        finally:
            cursor.close()
    
    # Utility Methods
    
    def clear_table(self, table_name: str) -> int:
        """Clear all data from a table."""
        query = f"DELETE FROM {table_name}"
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query)
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error clearing table {table_name}: {e}")
            raise
        finally:
            cursor.close()
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """Get information about a table structure."""
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
