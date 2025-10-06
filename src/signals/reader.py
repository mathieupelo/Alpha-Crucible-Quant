"""
Signal reader for alpha-crucible.

This module provides read-only access to signal_forge.signal_raw table.
It replaces the signal generation logic with a simple database reader.
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Optional, Any, Tuple
import pandas as pd
import numpy as np

from src.database import DatabaseManager

logger = logging.getLogger(__name__)


class SignalReader:
    """
    Reads signal data from signal_forge.signal_raw table.
    
    This class provides read-only access to computed signals stored in the
    signal_forge database. It replaces the signal generation logic with
    a simple database reader interface.
    """
    
    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        """
        Initialize signal reader.
        
        Args:
            database_manager: Database manager instance (optional)
        """
        self.database_manager = database_manager or DatabaseManager()
    
    def get_signals(self, tickers: Optional[List[str]] = None,
                   signal_names: Optional[List[str]] = None,
                   start_date: Optional[date] = None,
                   end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get signals from signal_forge.signal_raw table.
        
        Args:
            tickers: List of ticker symbols to filter by (optional)
            signal_names: List of signal names to filter by (optional)
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            DataFrame with signal data
        """
        try:
            if not self.database_manager.is_connected():
                if not self.database_manager.connect():
                    logger.error("Failed to connect to database")
                    return pd.DataFrame()
            
            return self.database_manager.get_signals_raw(
                tickers=tickers,
                signal_names=signal_names,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            logger.error(f"Error reading signals from database: {e}")
            return pd.DataFrame()
    
    def get_signal_pivot(self, tickers: Optional[List[str]] = None,
                        signal_names: Optional[List[str]] = None,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get signals as a pivoted DataFrame with tickers as columns and dates as index.
        
        Args:
            tickers: List of ticker symbols to filter by (optional)
            signal_names: List of signal names to filter by (optional)
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            Pivoted DataFrame with (date, signal_name) as index and tickers as columns
        """
        df = self.get_signals(tickers, signal_names, start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Pivot the data
        try:
            pivot_df = df.pivot_table(
                index=['asof_date', 'signal_name'],
                columns='ticker',
                values='value',
                aggfunc='first'  # Take first value if duplicates
            )
            
            # Flatten column names if multi-level
            if isinstance(pivot_df.columns, pd.MultiIndex):
                pivot_df.columns = pivot_df.columns.get_level_values(0)
            
            return pivot_df
            
        except Exception as e:
            logger.error(f"Error pivoting signal data: {e}")
            return pd.DataFrame()
    
    def get_signal_for_ticker(self, ticker: str, signal_name: str,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> pd.Series:
        """
        Get a specific signal for a specific ticker as a time series.
        
        Args:
            ticker: Ticker symbol
            signal_name: Signal name
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            Series with dates as index and signal values
        """
        df = self.get_signals(
            tickers=[ticker],
            signal_names=[signal_name],
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            return pd.Series(dtype=float)
        
        # Convert to time series
        df = df.set_index('asof_date')
        return df['value'].sort_index()
    
    def get_available_signals(self) -> List[str]:
        """
        Get list of available signal names in the database.
        
        Returns:
            List of signal names
        """
        try:
            if not self.database_manager.is_connected():
                if not self.database_manager.connect():
                    logger.error("Failed to connect to database")
                    return []
            
            query = "SELECT DISTINCT signal_name FROM signal_raw ORDER BY signal_name"
            df = self.database_manager.execute_query(query)
            
            if df.empty:
                return []
            
            return df['signal_name'].tolist()
            
        except Exception as e:
            logger.error(f"Error getting available signals: {e}")
            return []
    
    def get_available_tickers(self) -> List[str]:
        """
        Get list of available tickers in the database.
        
        Returns:
            List of ticker symbols
        """
        try:
            if not self.database_manager.is_connected():
                if not self.database_manager.connect():
                    logger.error("Failed to connect to database")
                    return []
            
            query = "SELECT DISTINCT ticker FROM signal_raw ORDER BY ticker"
            df = self.database_manager.execute_query(query)
            
            if df.empty:
                return []
            
            return df['ticker'].tolist()
            
        except Exception as e:
            logger.error(f"Error getting available tickers: {e}")
            return []
    
    def get_signal_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for all signals in the database.
        
        Returns:
            DataFrame with signal summary statistics
        """
        try:
            if not self.database_manager.is_connected():
                if not self.database_manager.connect():
                    logger.error("Failed to connect to database")
                    return pd.DataFrame()
            
            query = """
            SELECT 
                signal_name,
                ticker,
                COUNT(*) as count,
                MIN(asof_date) as first_date,
                MAX(asof_date) as last_date,
                AVG(value) as avg_value,
                STDDEV(value) as std_value,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM signal_raw 
            GROUP BY signal_name, ticker
            ORDER BY signal_name, ticker
            """
            
            return self.database_manager.execute_query(query)
            
        except Exception as e:
            logger.error(f"Error getting signal summary: {e}")
            return pd.DataFrame()
    
    def is_signal_available(self, ticker: str, signal_name: str, 
                           target_date: date) -> bool:
        """
        Check if a specific signal is available for a ticker on a given date.
        
        Args:
            ticker: Ticker symbol
            signal_name: Signal name
            target_date: Date to check
            
        Returns:
            True if signal is available, False otherwise
        """
        try:
            if not self.database_manager.is_connected():
                if not self.database_manager.connect():
                    return False
            
            query = """
            SELECT COUNT(*) as count 
            FROM signal_raw 
            WHERE ticker = %s AND signal_name = %s AND asof_date = %s
            """
            
            df = self.database_manager.execute_query(query, (ticker, signal_name, target_date))
            
            if df.empty:
                return False
            
            return df.iloc[0]['count'] > 0
            
        except Exception as e:
            logger.error(f"Error checking signal availability: {e}")
            return False
    
    # Additional methods for compatibility with BacktestEngine
    
    def get_signals_raw(self, tickers: Optional[List[str]] = None,
                       signal_names: Optional[List[str]] = None,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get raw signals from signal_forge.signal_raw table.
        Alias for get_signals() for compatibility.
        """
        return self.get_signals(tickers, signal_names, start_date, end_date)
    
    def calculate_and_enforce_signals(self, tickers: List[str], signals: List[str],
                                     start_date: date, end_date: date,
                                     store_in_db: bool = True) -> pd.DataFrame:
        """
        Calculate and enforce signals. Since this is a reader-only module,
        this method just returns existing signals from the database.
        
        Args:
            tickers: List of ticker symbols
            signals: List of signal names
            start_date: Start date for signals
            end_date: End date for signals
            store_in_db: Whether to store in database (ignored in reader)
            
        Returns:
            DataFrame with signal data
        """
        logger.warning("SignalReader is read-only. Cannot calculate new signals. "
                      "Please run the Signals repository to calculate signals first.")
        return self.get_signals(tickers, signals, start_date, end_date)
    
    def validate_signals_complete(self, tickers: List[str], signals: List[str],
                                 target_date: date) -> Tuple[bool, List[str]]:
        """
        Validate that all required signals are available for the given date.
        
        Args:
            tickers: List of ticker symbols
            signals: List of signal names
            target_date: Date to validate
            
        Returns:
            Tuple of (is_complete, missing_signals)
        """
        missing_signals = []
        
        for ticker in tickers:
            for signal in signals:
                if not self.is_signal_available(ticker, signal, target_date):
                    missing_signals.append(f"{ticker}:{signal}")
        
        is_complete = len(missing_signals) == 0
        return is_complete, missing_signals
    
    def get_scores_combined_pivot(self, tickers: Optional[List[str]] = None,
                                 signal_names: Optional[List[str]] = None,
                                 start_date: Optional[date] = None,
                                 end_date: Optional[date] = None,
                                 forward_fill: bool = False) -> pd.DataFrame:
        """
        Get combined signal scores as a pivoted DataFrame.
        This method reads from signal_raw and pivots the data.
        
        Args:
            tickers: List of ticker symbols
            signal_names: List of signal names
            start_date: Start date for filtering
            end_date: End date for filtering
            forward_fill: Whether to forward fill missing values
            
        Returns:
            Pivoted DataFrame with dates as index and tickers as columns
        """
        df = self.get_signals(tickers, signal_names, start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Pivot the data
        try:
            pivot_df = df.pivot_table(
                index='asof_date',
                columns='ticker',
                values='value',
                aggfunc='first'  # Take first value if duplicates
            )
            
            # Forward fill if requested
            if forward_fill:
                pivot_df = pivot_df.fillna(method='ffill')
            
            return pivot_df
            
        except Exception as e:
            logger.error(f"Error pivoting signal data: {e}")
            return pd.DataFrame()
    
    def calculate_signals(self, tickers: List[str], signals: List[str],
                         start_date: date, end_date: date,
                         store_in_db: bool = True) -> pd.DataFrame:
        """
        Calculate signals. Since this is a reader-only module,
        this method just returns existing signals from the database.
        
        Args:
            tickers: List of ticker symbols
            signals: List of signal names
            start_date: Start date for signals
            end_date: End date for signals
            store_in_db: Whether to store in database (ignored in reader)
            
        Returns:
            DataFrame with signal data
        """
        logger.warning("SignalReader is read-only. Cannot calculate new signals. "
                      "Please run the Signals repository to calculate signals first.")
        return self.get_signals(tickers, signals, start_date, end_date)