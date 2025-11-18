"""
Data validator module for the Alpha Crucible Quant system.

Provides comprehensive data validation and quality checks for market data.

NOTE: This module is primarily used in example/utility scripts (e.g., scripts/utils/run_backtest.py).
For production code, use src/utils/data_validation.py for simpler validation functions.
This DataValidator class provides more comprehensive validation including outlier detection
and detailed quality reports, making it useful for data quality checks in scripts.

This module was moved from src/data/validation.py to src/utils/data_validator.py for better organization.
"""

import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Comprehensive data validator for market data.
    
    Provides validation for:
    - Price data quality
    - Data completeness
    - Data consistency
    - Outlier detection
    - Data format validation
    """
    
    def __init__(self, 
                 min_price: float = 0.01,
                 max_price: float = 1000000.0,
                 max_daily_return: float = 0.5,  # 50% max daily return
                 min_volume: int = 1000):
        """
        Initialize data validator.
        
        Args:
            min_price: Minimum valid price
            max_price: Maximum valid price
            max_daily_return: Maximum valid daily return
            min_volume: Minimum valid volume
        """
        self.min_price = min_price
        self.max_price = max_price
        self.max_daily_return = max_daily_return
        self.min_volume = min_volume
    
    def validate_price_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate price data quality.
        
        Args:
            data: DataFrame with price data
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {},
            'cleaned_data': data.copy()
        }
        
        if data.empty:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Data is empty")
            return validation_results
        
        # Check required columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Missing required columns: {missing_columns}")
            return validation_results
        
        # Check for NaN values
        nan_counts = data[required_columns].isnull().sum()
        if nan_counts.any():
            validation_results['warnings'].append(f"NaN values found: {nan_counts.to_dict()}")
        
        # Check for negative prices
        negative_prices = (data[required_columns] <= 0).any(axis=1)
        if negative_prices.any():
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Negative or zero prices found in {negative_prices.sum()} rows")
        
        # Check OHLC relationships
        ohlc_errors = self._check_ohlc_relationships(data)
        if ohlc_errors:
            validation_results['is_valid'] = False
            validation_results['errors'].extend(ohlc_errors)
        
        # Check for extreme values
        extreme_values = self._check_extreme_values(data)
        if extreme_values:
            validation_results['warnings'].extend(extreme_values)
        
        # Check for duplicate dates
        if data.index.duplicated().any():
            validation_results['warnings'].append("Duplicate dates found")
        
        # Calculate statistics
        validation_results['statistics'] = self._calculate_statistics(data)
        
        # Clean data if there are issues
        if validation_results['warnings'] or validation_results['errors']:
            validation_results['cleaned_data'] = self._clean_data(data)
        
        return validation_results
    
    def validate_alpha_scores(self, alpha_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate alpha scores.
        
        Args:
            alpha_scores: Dictionary of ticker to alpha score
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        if not alpha_scores:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Alpha scores are empty")
            return validation_results
        
        scores = list(alpha_scores.values())
        
        # Check for NaN values
        nan_scores = [ticker for ticker, score in alpha_scores.items() if pd.isna(score)]
        if nan_scores:
            validation_results['warnings'].append(f"NaN scores found for: {nan_scores}")
        
        # Check for infinite values
        inf_scores = [ticker for ticker, score in alpha_scores.items() if np.isinf(score)]
        if inf_scores:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Infinite scores found for: {inf_scores}")
        
        # Check score range
        valid_scores = [score for score in scores if pd.notna(score) and not np.isinf(score)]
        if valid_scores:
            min_score = min(valid_scores)
            max_score = max(valid_scores)
            
            if min_score < -10 or max_score > 10:
                validation_results['warnings'].append(f"Scores outside normal range: min={min_score:.3f}, max={max_score:.3f}")
        
        # Calculate statistics
        validation_results['statistics'] = {
            'count': len(alpha_scores),
            'valid_count': len(valid_scores),
            'min_score': min(valid_scores) if valid_scores else None,
            'max_score': max(valid_scores) if valid_scores else None,
            'mean_score': np.mean(valid_scores) if valid_scores else None,
            'std_score': np.std(valid_scores) if valid_scores else None
        }
        
        return validation_results
    
    def validate_portfolio_data(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate portfolio data.
        
        Args:
            portfolio_data: Dictionary with portfolio information
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check required fields
        required_fields = ['tickers', 'weights', 'alpha_scores']
        missing_fields = [field for field in required_fields if field not in portfolio_data]
        if missing_fields:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Missing required fields: {missing_fields}")
            return validation_results
        
        tickers = portfolio_data['tickers']
        weights = portfolio_data['weights']
        alpha_scores = portfolio_data['alpha_scores']
        
        # Check data consistency
        if len(tickers) != len(weights):
            validation_results['is_valid'] = False
            validation_results['errors'].append("Mismatch between tickers and weights length")
        
        if len(tickers) != len(alpha_scores):
            validation_results['is_valid'] = False
            validation_results['errors'].append("Mismatch between tickers and alpha_scores length")
        
        # Check weight constraints
        total_weight = sum(weights)
        if abs(total_weight - 1.0) > 1e-6:
            validation_results['warnings'].append(f"Total weight is {total_weight:.6f}, expected 1.0")
        
        # Check individual weights
        negative_weights = [w for w in weights if w < 0]
        if negative_weights:
            validation_results['warnings'].append(f"Negative weights found: {len(negative_weights)}")
        
        # Calculate statistics
        validation_results['statistics'] = {
            'num_positions': len(tickers),
            'total_weight': total_weight,
            'min_weight': min(weights) if weights else None,
            'max_weight': max(weights) if weights else None,
            'weight_std': np.std(weights) if weights else None
        }
        
        return validation_results
    
    def _check_ohlc_relationships(self, data: pd.DataFrame) -> List[str]:
        """Check OHLC price relationships."""
        errors = []
        
        # High should be >= Low
        invalid_high_low = (data['High'] < data['Low']).any()
        if invalid_high_low:
            errors.append("High prices are lower than Low prices")
        
        # High should be >= Open
        invalid_high_open = (data['High'] < data['Open']).any()
        if invalid_high_open:
            errors.append("High prices are lower than Open prices")
        
        # High should be >= Close
        invalid_high_close = (data['High'] < data['Close']).any()
        if invalid_high_close:
            errors.append("High prices are lower than Close prices")
        
        # Low should be <= Open
        invalid_low_open = (data['Low'] > data['Open']).any()
        if invalid_low_open:
            errors.append("Low prices are higher than Open prices")
        
        # Low should be <= Close
        invalid_low_close = (data['Low'] > data['Close']).any()
        if invalid_low_close:
            errors.append("Low prices are higher than Close prices")
        
        return errors
    
    def _check_extreme_values(self, data: pd.DataFrame) -> List[str]:
        """Check for extreme values."""
        warnings = []
        
        # Check for extreme prices
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in data.columns:
                min_price = data[col].min()
                max_price = data[col].max()
                
                if min_price < self.min_price:
                    warnings.append(f"{col} has values below minimum price: {min_price}")
                
                if max_price > self.max_price:
                    warnings.append(f"{col} has values above maximum price: {max_price}")
        
        # Check for extreme daily returns
        if 'Close' in data.columns:
            returns = data['Close'].pct_change().dropna()
            extreme_returns = returns[abs(returns) > self.max_daily_return]
            
            if not extreme_returns.empty:
                warnings.append(f"Extreme daily returns found: {len(extreme_returns)} days with >{self.max_daily_return*100:.1f}% change")
        
        # Check volume if available
        if 'Volume' in data.columns:
            min_volume = data['Volume'].min()
            if min_volume < self.min_volume:
                warnings.append(f"Volume below minimum: {min_volume}")
        
        return warnings
    
    def _calculate_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data statistics."""
        stats = {}
        
        if data.empty:
            return stats
        
        # Basic statistics
        stats['num_rows'] = len(data)
        stats['num_columns'] = len(data.columns)
        stats['date_range'] = {
            'start': data.index.min() if hasattr(data.index, 'min') else None,
            'end': data.index.max() if hasattr(data.index, 'max') else None
        }
        
        # Price statistics
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in data.columns:
                stats[f'{col.lower()}_stats'] = {
                    'min': data[col].min(),
                    'max': data[col].max(),
                    'mean': data[col].mean(),
                    'std': data[col].std(),
                    'nan_count': data[col].isnull().sum()
                }
        
        # Volume statistics
        if 'Volume' in data.columns:
            stats['volume_stats'] = {
                'min': data['Volume'].min(),
                'max': data['Volume'].max(),
                'mean': data['Volume'].mean(),
                'std': data['Volume'].std(),
                'nan_count': data['Volume'].isnull().sum()
            }
        
        return stats
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean data by removing invalid rows."""
        cleaned = data.copy()
        
        # Remove rows with NaN values
        cleaned = cleaned.dropna()
        
        # Remove rows with negative prices
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in cleaned.columns:
                cleaned = cleaned[cleaned[col] > 0]
        
        # Remove rows with invalid OHLC relationships
        if all(col in cleaned.columns for col in ['Open', 'High', 'Low', 'Close']):
            cleaned = cleaned[
                (cleaned['High'] >= cleaned['Low']) &
                (cleaned['High'] >= cleaned['Open']) &
                (cleaned['High'] >= cleaned['Close']) &
                (cleaned['Low'] <= cleaned['Open']) &
                (cleaned['Low'] <= cleaned['Close'])
            ]
        
        # Remove duplicate dates
        cleaned = cleaned[~cleaned.index.duplicated(keep='first')]
        
        return cleaned
    
    def detect_outliers(self, data: pd.Series, method: str = 'iqr') -> pd.Series:
        """
        Detect outliers in a data series.
        
        Args:
            data: Data series to analyze
            method: Method for outlier detection ('iqr', 'zscore', 'modified_zscore')
            
        Returns:
            Boolean series indicating outliers
        """
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (data < lower_bound) | (data > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((data - data.mean()) / data.std())
            return z_scores > 3
        
        elif method == 'modified_zscore':
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z_scores = 0.6745 * (data - median) / mad
            return np.abs(modified_z_scores) > 3.5
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
    
    def validate_data_consistency(self, 
                                price_data: pd.DataFrame, 
                                alpha_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate consistency between price data and alpha scores.
        
        Args:
            price_data: Price data DataFrame
            alpha_scores: Alpha scores dictionary
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_consistent': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check if all alpha score tickers have price data
        price_tickers = set(price_data.columns)
        alpha_tickers = set(alpha_scores.keys())
        
        missing_price_data = alpha_tickers - price_tickers
        if missing_price_data:
            validation_results['is_consistent'] = False
            validation_results['errors'].append(f"Missing price data for tickers: {missing_price_data}")
        
        # Check if all price data tickers have alpha scores
        missing_alpha_scores = price_tickers - alpha_tickers
        if missing_alpha_scores:
            validation_results['warnings'].append(f"Missing alpha scores for tickers: {missing_alpha_scores}")
        
        # Calculate statistics
        common_tickers = price_tickers & alpha_tickers
        validation_results['statistics'] = {
            'total_tickers': len(alpha_tickers),
            'price_data_tickers': len(price_tickers),
            'common_tickers': len(common_tickers),
            'missing_price_data': len(missing_price_data),
            'missing_alpha_scores': len(missing_alpha_scores)
        }
        
        return validation_results


# Create default validator instance
default_validator = DataValidator()
