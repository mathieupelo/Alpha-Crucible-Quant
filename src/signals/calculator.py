"""
Signal calculator for the Quant Project system.

Calculates signals for multiple tickers and dates, integrating with the database.
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np

from .base import SignalBase
from .registry import signal_registry
from database import DatabaseManager, SignalScore
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
        all_scores = []
        
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
                            score = SignalScore(
                                ticker=ticker,
                                signal_id=signal_id,
                                date=target_date,
                                score=signal_value,
                                created_at=datetime.now()
                            )
                            all_scores.append(score)
                        
                    except Exception as e:
                        logger.error(f"Error calculating {signal_id} for {ticker} on {target_date}: {e}")
                        continue
        
        # Convert to DataFrame
        if all_scores:
            df = pd.DataFrame([{
                'ticker': score.ticker,
                'signal_id': score.signal_id,
                'date': score.date,
                'score': score.score,
                'created_at': score.created_at
            } for score in all_scores])
            
            # Store in database if requested
            if store_in_db:
                try:
                    self.database_manager.store_signal_scores(all_scores)
                    logger.info(f"Stored {len(all_scores)} signal scores in database")
                except Exception as e:
                    logger.error(f"Error storing signal scores in database: {e}")
            
            return df
        else:
            logger.warning("No signal scores calculated")
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
    
    def get_signal_scores(self, tickers: List[str], signals: List[str],
                         start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get signal scores from database.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with signal scores
        """
        try:
            return self.database_manager.get_signal_scores(tickers, signals, start_date, end_date)
        except Exception as e:
            logger.error(f"Error retrieving signal scores from database: {e}")
            return pd.DataFrame()
    
    def get_signal_scores_pivot(self, tickers: List[str], signals: List[str],
                               start_date: date, end_date: date) -> pd.DataFrame:
        """
        Get signal scores as a pivot table.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs
            start_date: Start date
            end_date: End date
            
        Returns:
            Pivot DataFrame with dates as index and ticker-signal combinations as columns
        """
        try:
            return self.database_manager.get_signal_scores_dataframe(tickers, signals, start_date, end_date)
        except Exception as e:
            logger.error(f"Error retrieving signal scores pivot from database: {e}")
            return pd.DataFrame()
    
    def combine_signals(self, signal_scores: pd.DataFrame, 
                       signal_weights: Dict[str, float]) -> pd.DataFrame:
        """
        Combine multiple signals into a single score.
        
        Args:
            signal_scores: DataFrame with signal scores
            signal_weights: Dictionary mapping signal IDs to weights
            
        Returns:
            DataFrame with combined scores
        """
        if signal_scores.empty:
            return pd.DataFrame()
        
        # Normalize weights
        total_weight = sum(signal_weights.values())
        if total_weight == 0:
            logger.warning("All signal weights are zero")
            return pd.DataFrame()
        
        normalized_weights = {k: v / total_weight for k, v in signal_weights.items()}
        
        # Group by ticker and date
        combined_scores = []
        
        for (ticker, date), group in signal_scores.groupby(['ticker', 'date']):
            combined_score = 0.0
            total_weight_used = 0.0
            
            for signal_id, weight in normalized_weights.items():
                signal_data = group[group['signal_id'] == signal_id]
                if not signal_data.empty:
                    score = signal_data['score'].iloc[0]
                    if not np.isnan(score):
                        combined_score += score * weight
                        total_weight_used += weight
            
            if total_weight_used > 0:
                # Normalize by actual weight used
                combined_score = combined_score / total_weight_used
                combined_scores.append({
                    'ticker': ticker,
                    'date': date,
                    'combined_score': combined_score
                })
        
        return pd.DataFrame(combined_scores)
    
    def get_missing_signals(self, tickers: List[str], signals: List[str],
                           start_date: date, end_date: date) -> List[Tuple[str, str, date]]:
        """
        Get list of missing signal calculations.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs
            start_date: Start date
            end_date: End date
            
        Returns:
            List of (ticker, signal_id, date) tuples for missing signals
        """
        try:
            # Get existing scores
            existing_scores = self.get_signal_scores(tickers, signals, start_date, end_date)
            
            # Get all possible combinations
            trading_days = DateUtils.get_trading_days(start_date, end_date)
            all_combinations = []
            
            for ticker in tickers:
                for signal_id in signals:
                    for target_date in trading_days:
                        all_combinations.append((ticker, signal_id, target_date))
            
            # Find missing combinations
            existing_combinations = set()
            if not existing_scores.empty:
                existing_combinations = set(zip(
                    existing_scores['ticker'],
                    existing_scores['signal_id'],
                    existing_scores['date']
                ))
            
            missing_combinations = []
            for combination in all_combinations:
                if combination not in existing_combinations:
                    missing_combinations.append(combination)
            
            return missing_combinations
            
        except Exception as e:
            logger.error(f"Error finding missing signals: {e}")
            return []
    
    def calculate_missing_signals(self, tickers: List[str], signals: List[str],
                                 start_date: date, end_date: date) -> pd.DataFrame:
        """
        Calculate only the missing signals.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with newly calculated signal scores
        """
        missing_signals = self.get_missing_signals(tickers, signals, start_date, end_date)
        
        if not missing_signals:
            logger.info("No missing signals found")
            return pd.DataFrame()
        
        logger.info(f"Found {len(missing_signals)} missing signals to calculate")
        
        # Calculate missing signals
        all_scores = []
        
        for ticker, signal_id, target_date in missing_signals:
            try:
                signal_value = self.calculate_signal_for_ticker(ticker, signal_id, target_date)
                
                if signal_value is not None:
                    score = SignalScore(
                        ticker=ticker,
                        signal_id=signal_id,
                        date=target_date,
                        score=signal_value,
                        created_at=datetime.now()
                    )
                    all_scores.append(score)
                    
            except Exception as e:
                logger.error(f"Error calculating missing signal {signal_id} for {ticker} on {target_date}: {e}")
                continue
        
        # Store in database
        if all_scores:
            try:
                self.database_manager.store_signal_scores(all_scores)
                logger.info(f"Stored {len(all_scores)} missing signal scores in database")
            except Exception as e:
                logger.error(f"Error storing missing signal scores in database: {e}")
        
        # Convert to DataFrame
        if all_scores:
            return pd.DataFrame([{
                'ticker': score.ticker,
                'signal_id': score.signal_id,
                'date': score.date,
                'score': score.score,
                'created_at': score.created_at
            } for score in all_scores])
        else:
            return pd.DataFrame()
