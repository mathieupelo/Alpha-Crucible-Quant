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

from .models import SignalScore, Portfolio, BacktestResult, SignalDefinition, DataFrameConverter

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
        self.database = database or os.getenv('DB_NAME', 'quant_project')
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
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute a SELECT query and return results as DataFrame."""
        self.ensure_connection()
        try:
            df = pd.read_sql(query, self._connection, params=params)
            return df
        except Error as e:
            logger.error(f"Error executing query: {e}")
            raise
    
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
    
    # Signal Score Operations
    
    def store_signal_scores(self, scores: List[SignalScore]) -> int:
        """Store signal scores in the database."""
        if not scores:
            return 0
        
        query = """
        INSERT INTO signal_scores (ticker, signal_id, date, score, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            score = VALUES(score),
            created_at = VALUES(created_at)
        """
        
        params_list = []
        for score in scores:
            params_list.append((
                score.ticker,
                score.signal_id,
                score.date,
                score.score,
                score.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_signal_scores(self, tickers: Optional[List[str]] = None,
                         signals: Optional[List[str]] = None,
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve signal scores from the database."""
        query = "SELECT * FROM signal_scores WHERE 1=1"
        params = []
        
        if tickers:
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND ticker IN ({placeholders})"
            params.extend(tickers)
        
        if signals:
            placeholders = ','.join(['%s'] * len(signals))
            query += f" AND signal_id IN ({placeholders})"
            params.extend(signals)
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " ORDER BY date, ticker, signal_id"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_signal_scores_dataframe(self, tickers: List[str], signals: List[str],
                                   start_date: date, end_date: date) -> pd.DataFrame:
        """Get signal scores as a pivot table (date x ticker x signal)."""
        df = self.get_signal_scores(tickers, signals, start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Create pivot table with date as index, ticker-signal as columns
        pivot_df = df.pivot_table(
            index='date',
            columns=['ticker', 'signal_id'],
            values='score',
            aggfunc='first'
        )
        
        return pivot_df
    
    # Portfolio Operations
    
    def store_portfolio(self, portfolio: Portfolio) -> int:
        """Store a portfolio in the database."""
        query = """
        INSERT INTO portfolios (portfolio_id, creation_date, weights, signal_weights, 
                              risk_aversion, max_weight, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            weights = VALUES(weights),
            signal_weights = VALUES(signal_weights),
            risk_aversion = VALUES(risk_aversion),
            max_weight = VALUES(max_weight),
            created_at = VALUES(created_at)
        """
        
        params = (
            portfolio.portfolio_id,
            portfolio.creation_date,
            str(portfolio.weights),  # Store as JSON string
            str(portfolio.signal_weights),  # Store as JSON string
            portfolio.risk_aversion,
            portfolio.max_weight,
            portfolio.created_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_portfolios(self, start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve portfolios from the database."""
        query = "SELECT * FROM portfolios WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND creation_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND creation_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY creation_date"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    # Backtest Results Operations
    
    def store_backtest_result(self, result: BacktestResult) -> int:
        """Store backtest results in the database."""
        query = """
        INSERT INTO backtest_results (backtest_id, start_date, end_date, tickers, signals,
                                    total_return, annualized_return, sharpe_ratio, max_drawdown,
                                    volatility, alpha, information_ratio, execution_time_seconds, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_return = VALUES(total_return),
            annualized_return = VALUES(annualized_return),
            sharpe_ratio = VALUES(sharpe_ratio),
            max_drawdown = VALUES(max_drawdown),
            volatility = VALUES(volatility),
            alpha = VALUES(alpha),
            information_ratio = VALUES(information_ratio),
            execution_time_seconds = VALUES(execution_time_seconds),
            created_at = VALUES(created_at)
        """
        
        params = (
            result.backtest_id,
            result.start_date,
            result.end_date,
            ','.join(result.tickers),
            ','.join(result.signals),
            result.total_return,
            result.annualized_return,
            result.sharpe_ratio,
            result.max_drawdown,
            result.volatility,
            result.alpha,
            result.information_ratio,
            result.execution_time_seconds,
            result.created_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_backtest_results(self, start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve backtest results from the database."""
        query = "SELECT * FROM backtest_results WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND start_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND end_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    # Signal Definition Operations
    
    def store_signal_definition(self, signal_def: SignalDefinition) -> int:
        """Store a signal definition in the database."""
        query = """
        INSERT INTO signal_definitions (signal_id, name, parameters, enabled, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            parameters = VALUES(parameters),
            enabled = VALUES(enabled),
            created_at = VALUES(created_at)
        """
        
        params = (
            signal_def.signal_id,
            signal_def.name,
            str(signal_def.parameters),  # Store as JSON string
            signal_def.enabled,
            signal_def.created_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_signal_definitions(self, enabled_only: bool = True) -> pd.DataFrame:
        """Retrieve signal definitions from the database."""
        query = "SELECT * FROM signal_definitions"
        params = []
        
        if enabled_only:
            query += " WHERE enabled = %s"
            params.append(True)
        
        query += " ORDER BY signal_id"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_enabled_signals(self) -> List[str]:
        """Get list of enabled signal IDs."""
        df = self.get_signal_definitions(enabled_only=True)
        return df['signal_id'].tolist() if not df.empty else []
    
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
