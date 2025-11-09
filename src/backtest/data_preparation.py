"""
Data preparation for backtesting.

This module handles fetching and preparing all data required for backtesting:
- Trading days and rebalancing dates
- Price data
- Signal scores
"""

import logging
from datetime import date, timedelta
from typing import List, Tuple, Optional
import pandas as pd

from .config import BacktestConfig
from src.utils import DateUtils, TradingCalendar

logger = logging.getLogger(__name__)


class BacktestDataPreparation:
    """Handles data preparation for backtesting."""
    
    def __init__(self, price_fetcher, signal_reader, trading_calendar: TradingCalendar):
        """
        Initialize data preparation.
        
        Args:
            price_fetcher: Price fetcher instance
            signal_reader: Signal reader instance
            trading_calendar: Trading calendar instance
        """
        self.price_fetcher = price_fetcher
        self.signal_reader = signal_reader
        self.trading_calendar = trading_calendar
    
    def prepare_backtest_data(self, tickers: List[str], signals: List[str], 
                             config: BacktestConfig) -> Tuple[List[date], List[date], Optional[pd.DataFrame], pd.DataFrame]:
        """
        Prepare all required data for backtesting.
        
        This method coordinates the preparation of:
        - Trading days within the backtest period
        - Rebalancing dates based on the specified frequency
        - Price data for all tickers
        - Signal scores for portfolio construction
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs to calculate
            config: Backtesting configuration
            
        Returns:
            Tuple containing:
                - trading_days: List of valid trading dates
                - rebalancing_dates: List of dates when portfolio should be rebalanced
                - price_data: DataFrame with price data (or None if failed)
                - signal_scores: DataFrame with signal scores (or empty if failed)
        """
        # Get trading days
        trading_days = DateUtils.get_trading_days(config.start_date, config.end_date)
        logger.info(f"Found {len(trading_days)} trading days")
        
        # Get rebalancing dates
        rebalancing_dates = self.trading_calendar.get_rebalancing_dates(
            config.start_date, config.end_date, config.rebalancing_frequency
        )
        logger.info(f"Found {len(rebalancing_dates)} rebalancing dates for {config.rebalancing_frequency} frequency")
        
        # Ensure signal scores exist for all rebalancing dates
        rebalancing_dates = self.ensure_signal_scores_for_rebalancing_dates(
            rebalancing_dates, tickers, signals, config
        )
        logger.info(f"Adjusted to {len(rebalancing_dates)} rebalancing dates with signal scores")
        
        # Get price data for all tickers
        price_data = self.get_price_data(tickers, config)
        if price_data is None or price_data.empty:
            logger.error("Failed to get price data")
            return trading_days, rebalancing_dates, None, pd.DataFrame()
        
        # Get signal scores (combined scores)
        signal_scores = self.get_signal_scores(tickers, signals, config)
        if signal_scores.empty:
            logger.error("Failed to get signal scores")
            return trading_days, rebalancing_dates, price_data, pd.DataFrame()
        
        return trading_days, rebalancing_dates, price_data, signal_scores
    
    def ensure_signal_scores_for_rebalancing_dates(self, rebalancing_dates: List[date], 
                                                   tickers: List[str], signals: List[str], 
                                                   config: BacktestConfig) -> List[date]:
        """Ensure signal scores exist for all rebalancing dates, adjusting dates if necessary."""
        adjusted_dates = []
        
        for rebal_date in rebalancing_dates:
            # Check if signal scores exist for this date
            signal_scores = self.signal_reader.get_scores_combined_pivot(
                tickers, ['equal_weight'], rebal_date, rebal_date, 
                forward_fill=False
            )
            
            if not signal_scores.empty and rebal_date in signal_scores.index:
                # Signal scores exist for this date
                adjusted_dates.append(rebal_date)
            else:
                # No signal scores for this date, find the next available date with scores
                logger.warning(f"No signal scores for rebalancing date {rebal_date}, finding next available date...")
                
                # Look for the next few days to find one with signal scores
                found_date = None
                for days_ahead in range(1, 8):  # Check up to 7 days ahead
                    check_date = rebal_date + timedelta(days=days_ahead)
                    
                    # Skip weekends
                    if check_date.weekday() >= 5:
                        continue
                    
                    # Check if signal scores exist for this date
                    signal_scores = self.signal_reader.get_scores_combined_pivot(
                        tickers, ['equal_weight'], check_date, check_date, 
                        forward_fill=False
                    )
                    
                    if not signal_scores.empty and check_date in signal_scores.index:
                        found_date = check_date
                        break
                
                if found_date:
                    adjusted_dates.append(found_date)
                    logger.info(f"Using {found_date} instead of {rebal_date} for rebalancing")
                else:
                    # If no signal scores found, use the original date and let forward fill handle it
                    adjusted_dates.append(rebal_date)
                    logger.warning(f"No signal scores found for {rebal_date} or nearby dates, will use forward fill")
        
        return adjusted_dates
    
    def get_price_data(self, tickers: List[str], config: BacktestConfig) -> Optional[pd.DataFrame]:
        """Get price data for all tickers."""
        try:
            # Extend start date to get enough lookback data
            extended_start = config.start_date - timedelta(days=config.max_lookback_days)
            
            price_data = self.price_fetcher.get_price_matrix(tickers, extended_start, config.end_date)
            
            if price_data.empty:
                logger.error("No price data available")
                return None
            
            # Filter to trading days only
            price_data = price_data[price_data.index >= config.start_date]
            
            logger.info(f"Retrieved price data for {len(price_data.columns)} tickers over {len(price_data)} days")
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting price data: {e}")
            return None
    
    def get_signal_scores(self, tickers: List[str], signals: List[str], 
                          config: BacktestConfig) -> pd.DataFrame:
        """Get signal scores for all tickers and signals."""
        try:
            # Extend start date to get enough lookback data
            extended_start = config.start_date - timedelta(days=config.max_lookback_days)
            
            # First try to get combined scores
            signal_scores = self.signal_reader.get_scores_combined_pivot(
                tickers, [config.signal_combination_method], extended_start, config.end_date, 
                forward_fill=config.forward_fill_signals
            )
            
            if signal_scores.empty:
                logger.info("No combined scores found in database, calculating signals...")
                
                # Calculate raw signals first
                logger.info(f"Calculating raw signals for {len(tickers)} tickers from {extended_start} to {config.end_date}")
                raw_signals = self.signal_reader.calculate_signals(
                    tickers, signals, extended_start, config.end_date,
                    store_in_db=True
                )
                
                if not raw_signals.empty:
                    logger.info(f"Calculated {len(raw_signals)} raw signals")
                    
                    # Combine signals into scores
                    logger.info(f"Combining signals using method: {config.signal_combination_method}")
                    signal_scores = self._combine_signals_to_scores(
                        raw_signals, tickers, signals, config
                    )
                    
                    if not signal_scores.empty:
                        logger.info(f"Combined signals into {len(signal_scores)} scores")
                        
                        # Convert to pivot format
                        signal_scores = signal_scores.pivot_table(
                            index='asof_date',
                            columns='ticker',
                            values='score',
                            aggfunc='first'
                        )
                        logger.info(f"Created pivot table with {len(signal_scores)} dates and {len(signal_scores.columns)} tickers")
                    else:
                        logger.warning("No combined scores created")
                else:
                    logger.warning("No raw signals calculated")
            else:
                logger.info(f"Retrieved {len(signal_scores)} signal scores from database")
            
            # Ensure we have signal scores for all rebalancing dates
            if not signal_scores.empty:
                # Get rebalancing dates to check coverage
                rebalancing_dates = self.trading_calendar.get_rebalancing_dates(config.start_date, config.end_date)
                # Ensure signal scores exist for all rebalancing dates
                rebalancing_dates = self.ensure_signal_scores_for_rebalancing_dates(
                    rebalancing_dates, tickers, signals, config
                )
                
                missing_dates = []
                for rebal_date in rebalancing_dates:
                    if rebal_date not in signal_scores.index:
                        missing_dates.append(rebal_date)
                
                if missing_dates:
                    logger.warning(f"Missing signal scores for {len(missing_dates)} rebalancing dates:")
                    for i, missing_date in enumerate(missing_dates, 1):
                        logger.warning(f"  {i}. {missing_date}")
                    
                    # Try to calculate missing signals for specific dates
                    if len(missing_dates) <= 5:  # Only for a few missing dates
                        logger.info("Attempting to calculate missing signals...")
                        for missing_date in missing_dates:
                            try:
                                # Calculate signals for this specific date
                                extended_start = missing_date - timedelta(days=config.max_lookback_days)
                                raw_signals = self.signal_reader.calculate_signals(
                                    tickers, signals, extended_start, missing_date + timedelta(days=1),
                                    store_in_db=True
                                )
                                
                                if not raw_signals.empty:
                                    # Combine signals for this date
                                    combined_scores = self._combine_signals_to_scores(
                                        raw_signals, tickers, signals, config
                                    )
                                    
                                    if not combined_scores.empty:
                                        # Add to signal_scores
                                        date_scores = combined_scores[combined_scores['asof_date'] == missing_date]
                                        if not date_scores.empty:
                                            pivot_scores = date_scores.pivot_table(
                                                index='asof_date',
                                                columns='ticker',
                                                values='score',
                                                aggfunc='first'
                                            )
                                            signal_scores = pd.concat([signal_scores, pivot_scores])
                                            logger.info(f"Calculated signals for {missing_date}")
                            except Exception as e:
                                logger.warning(f"Failed to calculate signals for {missing_date}: {e}")
                    
                    # Forward fill any remaining missing dates
                    # Sort the index first to ensure monotonic ordering
                    signal_scores = signal_scores.sort_index()
                    signal_scores = signal_scores.reindex(rebalancing_dates, method='ffill')
                    logger.info("Forward filled remaining missing signal scores")
            
            logger.info(f"Final signal scores shape: {signal_scores.shape}")
            return signal_scores
            
        except Exception as e:
            logger.error(f"Error getting signal scores: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _combine_signals_to_scores(self, raw_signals: pd.DataFrame, tickers: List[str], 
                                  signals: List[str], config: BacktestConfig) -> pd.DataFrame:
        """
        Combine raw signals into scores using the configured method.
        
        Args:
            raw_signals: DataFrame with raw signal values
            tickers: List of stock ticker symbols
            signals: List of signal IDs
            config: Backtesting configuration
            
        Returns:
            DataFrame with combined scores
        """
        try:
            import numpy as np
            from datetime import datetime
            from src.database import ScoreCombined
            
            combined_scores = []
            
            for ticker in tickers:
                ticker_signals = raw_signals[raw_signals['ticker'] == ticker]
                
                for asof_date in ticker_signals['asof_date'].unique():
                    date_signals = ticker_signals[ticker_signals['asof_date'] == asof_date]
                    
                    if date_signals.empty:
                        continue
                    
                    # Filter to only include selected signals
                    # Prefer signal_name_display (from signals table) over signal_name (from signal_raw)
                    signal_name_col = None
                    if 'signal_name_display' in date_signals.columns:
                        signal_name_col = 'signal_name_display'
                    elif 'signal_name' in date_signals.columns:
                        signal_name_col = 'signal_name'
                    
                    if signal_name_col:
                        date_signals = date_signals[date_signals[signal_name_col].isin(signals)]
                        if date_signals.empty:
                            logger.debug(f"No selected signals found for {ticker} on {asof_date} after filtering")
                    else:
                        logger.warning(f"Could not find signal_name column in date_signals for {ticker} on {asof_date}. Available columns: {date_signals.columns.tolist()}")
                    
                    if date_signals.empty:
                        continue
                    
                    # Apply combination method
                    if config.signal_combination_method == 'equal_weight':
                        # Filter out NULL/NaN values and average the remaining signals
                        # Don't require all signals to be present - just average what's available
                        valid_values = date_signals['value'].dropna()
                        if valid_values.empty:
                            logger.debug(f"All signal values are NULL/NaN for {ticker} on {asof_date}, skipping")
                            continue
                        # Simple average of non-null signals (no reweighting)
                        combined_score = valid_values.mean()
                            
                    elif config.signal_combination_method == 'weighted':
                        weights = config.signal_weights or {}
                        # Collect valid signals with their values
                        valid_signals = []
                        for _, row in date_signals.iterrows():
                            signal_value = row['value']
                            # Skip NULL/NaN values
                            if pd.isna(signal_value) or signal_value is None:
                                continue
                            signal_name = row['signal_name']
                            weight = weights.get(signal_name, 1.0)
                            valid_signals.append((signal_value, weight))
                        
                        if not valid_signals:
                            logger.debug(f"All signal values are NULL/NaN for {ticker} on {asof_date}, skipping")
                            continue
                        
                        # Use original weights for non-null signals, but don't reweight
                        # If user wants equal weighting when signals are missing, average equally
                        # Otherwise, use weighted average with original weights
                        if len(valid_signals) == len(signals):
                            # All signals present - use weighted average
                            weighted_sum = sum(val * weight for val, weight in valid_signals)
                            total_weight = sum(weight for _, weight in valid_signals)
                            combined_score = weighted_sum / total_weight if total_weight > 0 else None
                        else:
                            # Some signals missing - use equal weight average (don't reweight)
                            combined_score = np.mean([val for val, _ in valid_signals])
                        
                    elif config.signal_combination_method == 'zscore':
                        # Z-score normalization
                        # Filter out NULL/NaN values
                        valid_values = date_signals['value'].dropna().values
                        if len(valid_values) == 0:
                            logger.debug(f"All signal values are NULL/NaN for {ticker} on {asof_date}, skipping")
                            continue
                        elif len(valid_values) > 1:
                            mean_val = np.mean(valid_values)
                            std_val = np.std(valid_values)
                            combined_score = (valid_values - mean_val) / std_val if std_val > 0 else 0
                            # For zscore, we take the mean of normalized values
                            combined_score = np.mean(combined_score)
                        else:
                            combined_score = valid_values[0]
                    else:
                        logger.warning(f"Unknown combination method: {config.signal_combination_method}")
                        continue
                    
                    # Skip if combined_score is NULL, NaN, or None
                    if combined_score is not None and not (isinstance(combined_score, (int, float)) and np.isnan(combined_score)):
                        combined_scores.append({
                            'asof_date': asof_date,
                            'ticker': ticker,
                            'score': combined_score,
                            'method': config.signal_combination_method,
                            'params': config.signal_weights
                        })
            
            if combined_scores:
                df = pd.DataFrame(combined_scores)
                
                # Store combined scores in database
                try:
                    score_objects = []
                    for _, row in df.iterrows():
                        score_obj = ScoreCombined(
                            asof_date=row['asof_date'],
                            ticker=row['ticker'],
                            score=row['score'],
                            method=row['method'],
                            params=row.get('params'),
                            created_at=datetime.now()
                        )
                        score_objects.append(score_obj)
                    
                    # Note: database_manager should be passed in or accessed via signal_reader
                    # For now, we'll skip storing here and let the caller handle it
                    logger.info(f"Prepared {len(score_objects)} combined scores")
                except Exception as e:
                    logger.error(f"Error preparing combined scores: {e}")
                
                return df
            else:
                logger.warning("No combined scores calculated")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return pd.DataFrame()

