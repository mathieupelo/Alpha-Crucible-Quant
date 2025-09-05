"""
Signal calculator for the Quant Project system.

Calculates signals for multiple tickers and dates, integrating with the database.
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
import numpy as np

from .base import SignalBase
from .registry import signal_registry
from database import DatabaseManager, SignalRaw, ScoreCombined
from utils import PriceFetcher, DateUtils

logger = logging.getLogger(__name__)


class SignalCalculator:
    """Calculates signals for multiple tickers and dates."""
    
    def __init__(self, price_fetcher: Optional[PriceFetcher] = None, 
                 database_manager: Optional[DatabaseManager] = None):
        """
        Initialize signal calculator.
        
        Args:
            price_fetcher: Price fetcher instance (optional)
            database_manager: Database manager instance (optional)
        """
        self.price_fetcher = price_fetcher or PriceFetcher()
        self.database_manager = database_manager or DatabaseManager()
        self.registry = signal_registry
    
    def calculate_signals(self, tickers: List[str], signals: List[str], 
                         start_date: date, end_date: date,
                         store_in_db: bool = True) -> pd.DataFrame:
        """
        Calculate signals for multiple tickers over a date range.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs to calculate
            start_date: Start date for calculation
            end_date: End date for calculation
            store_in_db: Whether to store results in database
            
        Returns:
            DataFrame with signal scores
        """
        logger.info(f"Calculating signals for {len(tickers)} tickers, {len(signals)} signals from {start_date} to {end_date}")
        
        # Get trading days
        trading_days = DateUtils.get_trading_days(start_date, end_date)
        logger.info(f"Found {len(trading_days)} trading days")
        
        # Calculate signals for each ticker and date
        all_signals = []
        
        for ticker in tickers:
            logger.info(f"Processing ticker: {ticker}")
            
            # Get price data for the ticker
            price_data = self.price_fetcher.get_price_history(ticker, start_date, end_date)
            
            if price_data is None or price_data.empty:
                logger.warning(f"No price data available for {ticker}")
                continue
            
            # Calculate signals for each date
            for target_date in trading_days:
                if target_date not in price_data.index:
                    continue
                
                for signal_id in signals:
                    try:
                        # Get signal instance
                        signal = self.registry.get_signal(signal_id)
                        if signal is None:
                            logger.warning(f"Signal not found: {signal_id}")
                            continue
                        
                        # Calculate signal value
                        signal_value = signal.calculate(price_data, ticker, target_date)
                        
                        if not np.isnan(signal_value):
                            # Store raw signal
                            raw_signal = SignalRaw(
                                asof_date=target_date,
                                ticker=ticker,
                                signal_name=signal_id,
                                value=signal_value,
                                metadata={'signal_class': signal.__class__.__name__},
                                created_at=datetime.now()
                            )
                            all_signals.append(raw_signal)
                        
                    except Exception as e:
                        logger.error(f"Error calculating {signal_id} for {ticker} on {target_date}: {e}")
                        continue
        
        # Convert to DataFrame
        if all_signals:
            df = pd.DataFrame([{
                'asof_date': signal.asof_date,
                'ticker': signal.ticker,
                'signal_name': signal.signal_name,
                'value': signal.value,
                'metadata': signal.metadata,
                'created_at': signal.created_at
            } for signal in all_signals])
            
            # Store in database if requested
            if store_in_db:
                try:
                    self.database_manager.store_signals_raw(all_signals)
                    logger.info(f"Stored {len(all_signals)} raw signals in database")
                except Exception as e:
                    logger.error(f"Error storing raw signals in database: {e}")
            
            return df
        else:
            logger.warning("No signals calculated")
            return pd.DataFrame()
    
    def calculate_signal_for_ticker(self, ticker: str, signal_id: str, 
                                   target_date: date) -> Optional[float]:
        """
        Calculate a single signal for a single ticker on a specific date.
        
        Args:
            ticker: Stock ticker symbol
            signal_id: Signal identifier
            target_date: Date to calculate signal for
            
        Returns:
            Signal value or None if calculation fails
        """
        try:
            # Get signal instance
            signal = self.registry.get_signal(signal_id)
            if signal is None:
                logger.warning(f"Signal not found: {signal_id}")
                return None
            
            # Get required price data
            start_date, end_date = signal.get_required_price_data(target_date)
            price_data = self.price_fetcher.get_price_history(ticker, start_date, end_date)
            
            if price_data is None or price_data.empty:
                logger.warning(f"No price data available for {ticker}")
                return None
            
            # Calculate signal
            signal_value = signal.calculate(price_data, ticker, target_date)
            
            if np.isnan(signal_value):
                logger.warning(f"Signal calculation returned NaN for {ticker} on {target_date}")
                return None
            
            return signal_value
            
        except Exception as e:
            logger.error(f"Error calculating {signal_id} for {ticker} on {target_date}: {e}")
            return None
    
    def get_signals_raw(self, tickers: List[str], signal_names: List[str],
                       start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get raw signals from database.
        
        Args:
            tickers: List of stock ticker symbols
            signal_names: List of signal names
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with raw signals
        """
        try:
            return self.database_manager.get_signals_raw(tickers, signal_names, start_date, end_date)
        except Exception as e:
            logger.error(f"Error retrieving raw signals from database: {e}")
            return pd.DataFrame()
    
    def combine_signals_to_scores(self, tickers: List[str], signal_names: List[str],
                                 start_date: date, end_date: date,
                                 method: str = 'equal_weight',
                                 method_params: Optional[Dict[str, Any]] = None,
                                 store_in_db: bool = True) -> pd.DataFrame:
        """
        Combine raw signals into scores using specified method.
        
        Args:
            tickers: List of stock ticker symbols
            signal_names: List of signal names to combine
            start_date: Start date
            end_date: End date
            method: Method to combine signals ('equal_weight', 'weighted', 'zscore')
            method_params: Parameters for the combination method
            store_in_db: Whether to store results in database
            
        Returns:
            DataFrame with combined scores
        """
        logger.info(f"Combining signals for {len(tickers)} tickers using method: {method}")
        
        # Get raw signals
        raw_signals_df = self.get_signals_raw(tickers, signal_names, start_date, end_date)
        
        if raw_signals_df.empty:
            logger.warning("No raw signals found to combine")
            return pd.DataFrame()
        
        # Combine signals
        combined_scores = []
        
        for ticker in tickers:
            ticker_signals = raw_signals_df[raw_signals_df['ticker'] == ticker]
            
            for asof_date in ticker_signals['asof_date'].unique():
                date_signals = ticker_signals[ticker_signals['asof_date'] == asof_date]
                
                if date_signals.empty:
                    continue
                
                # Apply combination method
                if method == 'equal_weight':
                    combined_score = date_signals['value'].mean()
                elif method == 'weighted':
                    weights = method_params.get('weights', {})
                    total_weight = 0
                    weighted_sum = 0
                    for _, row in date_signals.iterrows():
                        weight = weights.get(row['signal_name'], 1.0)
                        weighted_sum += row['value'] * weight
                        total_weight += weight
                    combined_score = weighted_sum / total_weight if total_weight > 0 else 0
                elif method == 'zscore':
                    # Z-score normalization
                    values = date_signals['value'].values
                    if len(values) > 1:
                        mean_val = np.mean(values)
                        std_val = np.std(values)
                        combined_score = (values - mean_val) / std_val if std_val > 0 else 0
                    else:
                        combined_score = values[0] if len(values) == 1 else 0
                else:
                    logger.warning(f"Unknown combination method: {method}")
                    continue
                
                if not np.isnan(combined_score):
                    score = ScoreCombined(
                        asof_date=asof_date,
                        ticker=ticker,
                        score=combined_score,
                        method=method,
                        params=method_params,
                        created_at=datetime.now()
                    )
                    combined_scores.append(score)
        
        # Convert to DataFrame
        if combined_scores:
            df = pd.DataFrame([{
                'asof_date': score.asof_date,
                'ticker': score.ticker,
                'score': score.score,
                'method': score.method,
                'params': score.params,
                'created_at': score.created_at
            } for score in combined_scores])
            
            # Store in database if requested
            if store_in_db:
                try:
                    self.database_manager.store_scores_combined(combined_scores)
                    logger.info(f"Stored {len(combined_scores)} combined scores in database")
                except Exception as e:
                    logger.error(f"Error storing combined scores in database: {e}")
            
            return df
        else:
            logger.warning("No combined scores calculated")
            return pd.DataFrame()
    
    def get_scores_combined(self, tickers: List[str], methods: List[str],
                           start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get combined scores from database.
        
        Args:
            tickers: List of stock ticker symbols
            methods: List of combination methods
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with combined scores
        """
        try:
            return self.database_manager.get_scores_combined(tickers, methods, start_date, end_date)
        except Exception as e:
            logger.error(f"Error retrieving combined scores from database: {e}")
            return pd.DataFrame()
    
    def get_scores_combined_pivot(self, tickers: List[str], methods: List[str],
                                 start_date: date, end_date: date, 
                                 forward_fill: bool = True) -> pd.DataFrame:
        """
        Get combined scores as a pivot table.
        
        Args:
            tickers: List of stock ticker symbols
            methods: List of combination methods
            start_date: Start date
            end_date: End date
            forward_fill: Whether to forward fill missing values with latest available scores
            
        Returns:
            Pivot DataFrame with dates as index and ticker-method combinations as columns
        """
        try:
            return self.database_manager.get_scores_combined_pivot(tickers, methods, start_date, end_date, forward_fill)
        except Exception as e:
            logger.error(f"Error retrieving combined scores pivot from database: {e}")
            return pd.DataFrame()
    
    def get_missing_signals(self, tickers: List[str], signal_names: List[str],
                           start_date: date, end_date: date) -> List[Tuple[str, str, date]]:
        """
        Get list of missing signal calculations.
        
        Args:
            tickers: List of stock ticker symbols
            signal_names: List of signal names
            start_date: Start date
            end_date: End date
            
        Returns:
            List of (ticker, signal_name, date) tuples for missing signals
        """
        try:
            # Get existing signals
            existing_signals = self.get_signals_raw(tickers, signal_names, start_date, end_date)
            
            # Get all possible combinations
            trading_days = DateUtils.get_trading_days(start_date, end_date)
            all_combinations = []
            
            for ticker in tickers:
                for signal_name in signal_names:
                    for target_date in trading_days:
                        all_combinations.append((ticker, signal_name, target_date))
            
            # Find missing combinations
            existing_combinations = set()
            if not existing_signals.empty:
                existing_combinations = set(zip(
                    existing_signals['ticker'],
                    existing_signals['signal_name'],
                    existing_signals['asof_date']
                ))
            
            missing_combinations = []
            for combination in all_combinations:
                if combination not in existing_combinations:
                    missing_combinations.append(combination)
            
            return missing_combinations
            
        except Exception as e:
            logger.error(f"Error finding missing signals: {e}")
            return []
    
    def calculate_missing_signals(self, tickers: List[str], signal_names: List[str],
                                 start_date: date, end_date: date) -> pd.DataFrame:
        """
        Calculate only the missing signals.
        
        Args:
            tickers: List of stock ticker symbols
            signal_names: List of signal names
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with newly calculated signals
        """
        missing_signals = self.get_missing_signals(tickers, signal_names, start_date, end_date)
        
        if not missing_signals:
            logger.info("No missing signals found")
            return pd.DataFrame()
        
        logger.info(f"Found {len(missing_signals)} missing signals to calculate")
        
        # Calculate missing signals
        all_signals = []
        
        for ticker, signal_name, target_date in missing_signals:
            try:
                signal_value = self.calculate_signal_for_ticker(ticker, signal_name, target_date)
                
                if signal_value is not None:
                    signal = SignalRaw(
                        asof_date=target_date,
                        ticker=ticker,
                        signal_name=signal_name,
                        value=signal_value,
                        metadata={'signal_class': 'calculated'},
                        created_at=datetime.now()
                    )
                    all_signals.append(signal)
                    
            except Exception as e:
                logger.error(f"Error calculating missing signal {signal_name} for {ticker} on {target_date}: {e}")
                continue
        
        # Store in database
        if all_signals:
            try:
                self.database_manager.store_signals_raw(all_signals)
                logger.info(f"Stored {len(all_signals)} missing signals in database")
            except Exception as e:
                logger.error(f"Error storing missing signals in database: {e}")
        
        # Convert to DataFrame
        if all_signals:
            return pd.DataFrame([{
                'asof_date': signal.asof_date,
                'ticker': signal.ticker,
                'signal_name': signal.signal_name,
                'value': signal.value,
                'metadata': signal.metadata,
                'created_at': signal.created_at
            } for signal in all_signals])
        else:
            return pd.DataFrame()
