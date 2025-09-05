"""
Data validation utilities for the Quant Project system.

Provides common data validation functions to reduce code duplication.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)


def validate_price_data(price_data: Optional[pd.DataFrame], 
                       ticker: str, 
                       target_date: date) -> bool:
    """
    Validate price data for signal calculation.
    
    Args:
        price_data: DataFrame with price data
        ticker: Stock ticker symbol
        target_date: Date to validate for
        
    Returns:
        True if data is valid, False otherwise
    """
    if price_data is None or price_data.empty:
        logger.warning(f"No price data available for {ticker}")
        return False
    
    if target_date not in price_data.index:
        logger.warning(f"No price data for {ticker} on {target_date}")
        return False
    
    # Check for required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in price_data.columns]
    if missing_columns:
        logger.warning(f"Missing columns in price data for {ticker}: {missing_columns}")
        return False
    
    # Check for NaN values in required columns
    row_data = price_data.loc[target_date]
    for col in required_columns:
        if pd.isna(row_data[col]):
            logger.warning(f"NaN value in {col} for {ticker} on {target_date}")
            return False
    
    # Check for negative prices
    for col in ['Open', 'High', 'Low', 'Close']:
        if row_data[col] <= 0:
            logger.warning(f"Non-positive {col} for {ticker} on {target_date}: {row_data[col]}")
            return False
    
    # Check for negative volume
    if row_data['Volume'] < 0:
        logger.warning(f"Negative volume for {ticker} on {target_date}: {row_data['Volume']}")
        return False
    
    return True


def validate_signal_value(signal_value: float, signal_name: str, 
                         ticker: str, target_date: date) -> bool:
    """
    Validate signal value.
    
    Args:
        signal_value: Calculated signal value
        signal_name: Name of the signal
        ticker: Stock ticker symbol
        target_date: Date of calculation
        
    Returns:
        True if signal value is valid, False otherwise
    """
    if np.isnan(signal_value):
        logger.warning(f"NaN signal value for {signal_name} on {ticker} at {target_date}")
        return False
    
    if np.isinf(signal_value):
        logger.warning(f"Infinite signal value for {signal_name} on {ticker} at {target_date}")
        return False
    
    return True


def validate_portfolio_weights(weights: Union[pd.Series, Dict[str, float]], 
                             tickers: List[str]) -> bool:
    """
    Validate portfolio weights.
    
    Args:
        weights: Portfolio weights
        tickers: List of expected tickers
        
    Returns:
        True if weights are valid, False otherwise
    """
    if isinstance(weights, dict):
        weights = pd.Series(weights)
    
    # Check if all tickers are present
    missing_tickers = set(tickers) - set(weights.index)
    if missing_tickers:
        logger.warning(f"Missing weights for tickers: {missing_tickers}")
        return False
    
    # Check for NaN values
    if weights.isna().any():
        logger.warning("NaN values in portfolio weights")
        return False
    
    # Check for negative weights
    if (weights < 0).any():
        logger.warning("Negative weights in portfolio")
        return False
    
    # Check if weights sum to approximately 1
    total_weight = weights.sum()
    if abs(total_weight - 1.0) > 1e-6:
        logger.warning(f"Portfolio weights sum to {total_weight:.6f}, expected 1.0")
        return False
    
    return True


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if date range is valid, False otherwise
    """
    if start_date > end_date:
        logger.warning(f"Start date {start_date} is after end date {end_date}")
        return False
    
    if start_date > date.today():
        logger.warning(f"Start date {start_date} is in the future")
        return False
    
    return True


def validate_ticker_list(tickers: List[str]) -> bool:
    """
    Validate list of ticker symbols.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        True if tickers are valid, False otherwise
    """
    if not tickers:
        logger.warning("Empty ticker list")
        return False
    
    if not isinstance(tickers, list):
        logger.warning("Tickers must be a list")
        return False
    
    for ticker in tickers:
        if not isinstance(ticker, str):
            logger.warning(f"Ticker must be string, got {type(ticker)}: {ticker}")
            return False
        
        if not ticker.strip():
            logger.warning("Empty ticker symbol")
            return False
        
        if not ticker.isalpha():
            logger.warning(f"Ticker contains non-alphabetic characters: {ticker}")
            return False
    
    return True


def validate_signal_list(signals: List[str]) -> bool:
    """
    Validate list of signal names.
    
    Args:
        signals: List of signal names
        
    Returns:
        True if signals are valid, False otherwise
    """
    if not signals:
        logger.warning("Empty signal list")
        return False
    
    if not isinstance(signals, list):
        logger.warning("Signals must be a list")
        return False
    
    for signal in signals:
        if not isinstance(signal, str):
            logger.warning(f"Signal must be string, got {type(signal)}: {signal}")
            return False
        
        if not signal.strip():
            logger.warning("Empty signal name")
            return False
    
    return True


def clean_price_data(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean price data by removing invalid rows and filling missing values.
    
    Args:
        price_data: Raw price data
        
    Returns:
        Cleaned price data
    """
    # Remove rows with all NaN values
    price_data = price_data.dropna(how='all')
    
    # Remove rows with negative prices
    price_data = price_data[
        (price_data['Open'] > 0) & 
        (price_data['High'] > 0) & 
        (price_data['Low'] > 0) & 
        (price_data['Close'] > 0)
    ]
    
    # Remove rows with negative volume
    price_data = price_data[price_data['Volume'] >= 0]
    
    # Forward fill missing values
    price_data = price_data.fillna(method='ffill')
    
    return price_data


def normalize_signal_values(signal_values: pd.Series, 
                          method: str = 'zscore') -> pd.Series:
    """
    Normalize signal values.
    
    Args:
        signal_values: Series of signal values
        method: Normalization method ('zscore', 'minmax', 'rank')
        
    Returns:
        Normalized signal values
    """
    if method == 'zscore':
        mean_val = signal_values.mean()
        std_val = signal_values.std()
        if std_val > 0:
            return (signal_values - mean_val) / std_val
        else:
            return signal_values - mean_val
    
    elif method == 'minmax':
        min_val = signal_values.min()
        max_val = signal_values.max()
        if max_val > min_val:
            return (signal_values - min_val) / (max_val - min_val)
        else:
            return signal_values - min_val
    
    elif method == 'rank':
        return signal_values.rank(pct=True)
    
    else:
        logger.warning(f"Unknown normalization method: {method}")
        return signal_values


def check_data_quality(data: pd.DataFrame, 
                      required_columns: List[str],
                      min_rows: int = 1) -> Dict[str, Any]:
    """
    Check data quality and return quality metrics.
    
    Args:
        data: DataFrame to check
        required_columns: List of required columns
        min_rows: Minimum number of rows required
        
    Returns:
        Dictionary with quality metrics
    """
    quality_report = {
        'total_rows': len(data),
        'total_columns': len(data.columns),
        'missing_columns': [],
        'missing_values': {},
        'duplicate_rows': 0,
        'data_types': {},
        'quality_score': 0.0
    }
    
    # Check for required columns
    quality_report['missing_columns'] = [
        col for col in required_columns if col not in data.columns
    ]
    
    # Check for missing values
    for col in data.columns:
        missing_count = data[col].isna().sum()
        quality_report['missing_values'][col] = missing_count
    
    # Check for duplicate rows
    quality_report['duplicate_rows'] = data.duplicated().sum()
    
    # Check data types
    quality_report['data_types'] = data.dtypes.to_dict()
    
    # Calculate quality score
    score = 1.0
    
    # Penalize missing columns
    if quality_report['missing_columns']:
        score -= 0.3
    
    # Penalize missing values
    total_missing = sum(quality_report['missing_values'].values())
    if total_missing > 0:
        score -= min(0.3, total_missing / (len(data) * len(data.columns)) * 2)
    
    # Penalize duplicate rows
    if quality_report['duplicate_rows'] > 0:
        score -= min(0.2, quality_report['duplicate_rows'] / len(data))
    
    # Penalize insufficient rows
    if len(data) < min_rows:
        score -= 0.2
    
    quality_report['quality_score'] = max(0.0, score)
    
    return quality_report
