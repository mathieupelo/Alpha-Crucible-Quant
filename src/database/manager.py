"""
Database manager for the Quant Project system.

Provides a simplified interface to PostgreSQL database operations using pandas DataFrames.
"""

import os
import logging
from datetime import date, datetime
from typing import List, Dict, Optional, Any
import pandas as pd
import psycopg2
from psycopg2 import Error as PgError
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from src.utils.error_handling import handle_database_errors, retry_on_failure

# Import operation mixins
from .signal_operations import SignalOperationsMixin
from .score_operations import ScoreOperationsMixin
from .portfolio_operations import PortfolioOperationsMixin
from .backtest_operations import BacktestOperationsMixin
from .universe_operations import UniverseOperationsMixin

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager(
    SignalOperationsMixin,
    ScoreOperationsMixin,
    PortfolioOperationsMixin,
    BacktestOperationsMixin,
    UniverseOperationsMixin
):
    """
    Manages database connections and operations for the Quant Project system.
    
    This class provides a unified interface to all database operations through
    multiple inheritance of operation mixins. The core connection and query
    methods are defined here, while domain-specific operations are provided
    by the mixin classes.
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, 
                 user: Optional[str] = None, password: Optional[str] = None, 
                 database: Optional[str] = None, database_url: Optional[str] = None):
        """Initialize database manager with connection parameters."""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        # Ensure sslmode=require exactly once when using DATABASE_URL (Supabase requires SSL)
        if self.database_url:
            url_lower = self.database_url.lower()
            has_query = '?' in self.database_url
            has_ssl = 'sslmode=' in url_lower
            if not has_ssl:
                separator = '&' if has_query else '?'
                self.database_url = f"{self.database_url}{separator}sslmode=require"
        self.host = host or os.getenv('DB_HOST', '127.0.0.1')
        self.port = port or int(os.getenv('DB_PORT', '5432'))
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.database = database or os.getenv('DB_NAME', 'postgres')
        self._connection = None
    
    def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            # Connection hardening for Supabase (and remote Postgres)
            common_kwargs = {
                "connect_timeout": 10,
                # Enable TCP keepalives so idle connections don't die silently
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 3,
            }
            if self.database_url:
                # Use DATABASE_URL if available (for Supabase)
                self._connection = psycopg2.connect(self.database_url, **common_kwargs)
            else:
                # Use individual connection parameters
                self._connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    sslmode="require",
                    **common_kwargs
                )
            
            if self._connection:
                self._connection.autocommit = True
                logger.info(f"Connected to PostgreSQL database: {self.database}")
                return True
        except PgError as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False
        return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("PostgreSQL connection closed")
    
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self._connection and not self._connection.closed
    
    def ensure_connection(self) -> None:
        """Ensure database connection is active, reconnect if necessary."""
        if not self.is_connected():
            if not self.connect():
                raise Exception("Failed to establish database connection")
    
    @handle_database_errors
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute a SELECT query and return results as DataFrame."""
        try:
            self.ensure_connection()
            if not self._connection:
                logger.error("Database connection is None after ensure_connection")
                return pd.DataFrame()
                
            cursor = self._connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                return pd.DataFrame()
            
            return pd.DataFrame(results)
        except Exception as e:
            # Handle intermittent SSL EOF / network blips by one-time reconnect and retry
            err_msg = str(e)
            logger.error(f"Database error in execute_query: {err_msg}")
            if "SSL SYSCALL error: EOF detected" in err_msg or "server closed the connection unexpectedly" in err_msg:
                try:
                    logger.info("Attempting to reconnect and retry query after connection drop")
                    self.disconnect()
                    if self.connect():
                        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
                        cursor.execute(query, params)
                        results = cursor.fetchall()
                        cursor.close()
                        return pd.DataFrame(results) if results else pd.DataFrame()
                except Exception as e2:
                    logger.error(f"Retry after reconnect failed: {e2}")
            return pd.DataFrame()
    
    def execute_insert(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT query and return the last insert ID."""
        try:
            self.ensure_connection()
            if not self._connection:
                logger.error("Database connection is None after ensure_connection")
                return 0
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            
            # Check if query has RETURNING clause
            if cursor.description:
                result = cursor.fetchone()
                return result[0] if result else 0
            else:
                # Fallback to lastrowid if no RETURNING clause
                return cursor.lastrowid if hasattr(cursor, 'lastrowid') else 0
        except PgError as e:
            logger.error(f"Error executing insert: {e}")
            raise
        except Exception as e:
            logger.error(f"Database error in execute_insert: {e}")
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute a query with multiple parameter sets."""
        self.ensure_connection()
        cursor = self._connection.cursor()
        try:
            cursor.executemany(query, params_list)
            return cursor.rowcount
        except PgError as e:
            logger.error(f"Error executing batch insert: {e}")
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
        except PgError as e:
            logger.error(f"Error clearing table {table_name}: {e}")
            raise
        finally:
            cursor.close()
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """Get information about a table structure."""
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def __enter__(self) -> 'DatabaseManager':
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]) -> None:
        """Context manager exit."""
        self.disconnect()
