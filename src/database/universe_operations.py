"""
Universe and UniverseTicker database operations.

This module contains all database operations related to universes and tickers.
"""

import logging
from datetime import datetime
from typing import List, Optional
import pandas as pd
from psycopg2 import Error as PgError

from .models import Universe, UniverseTicker

logger = logging.getLogger(__name__)


class UniverseOperationsMixin:
    """Mixin class providing universe-related database operations."""
    
    def store_universe(self, universe: Universe) -> int:
        """Store a universe in the database."""
        query = """
        INSERT INTO universes (name, description, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            description = EXCLUDED.description,
            updated_at = EXCLUDED.updated_at
        """
        
        params = (
            universe.name,
            universe.description,
            universe.created_at or datetime.now(),
            universe.updated_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an UPDATE query and return the number of affected rows."""
        try:
            self.ensure_connection()
            if not self._connection:
                logger.error("Database connection is None after ensure_connection")
                return 0
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            return cursor.rowcount
        except PgError as e:
            logger.error(f"Error executing update: {e}")
            if self._connection:
                self._connection.rollback()
            raise
        except Exception as e:
            logger.error(f"Database error in execute_update: {e}")
            if self._connection:
                self._connection.rollback()
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def update_universe(self, universe_id: int, name: str, description: Optional[str] = None, 
                       updated_at: Optional[datetime] = None) -> bool:
        """Update an existing universe in the database."""
        query = """
        UPDATE universes 
        SET name = %s, description = %s, updated_at = %s
        WHERE id = %s
        """
        
        params = (
            name,
            description,
            updated_at or datetime.now(),
            universe_id
        )
        
        try:
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating universe {universe_id}: {e}")
            raise
    
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
    
    def get_universes_by_ids(self, universe_ids: List[int]) -> pd.DataFrame:
        """Get multiple universes by their IDs (for batch fetching)."""
        if not universe_ids:
            return pd.DataFrame()
        
        placeholders = ','.join(['%s'] * len(universe_ids))
        query = f"SELECT * FROM universes WHERE id IN ({placeholders})"
        return self.execute_query(query, tuple(universe_ids))
    
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
        except PgError as e:
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
        ON CONFLICT (universe_id, ticker) DO UPDATE SET
            added_at = EXCLUDED.added_at
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
        ON CONFLICT (universe_id, ticker) DO UPDATE SET
            added_at = EXCLUDED.added_at
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
        except PgError as e:
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
        except PgError as e:
            logger.error(f"Error deleting all tickers from universe {universe_id}: {e}")
            raise
        finally:
            cursor.close()

