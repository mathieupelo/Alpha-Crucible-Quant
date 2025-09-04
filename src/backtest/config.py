"""
Backtesting configuration for the Quant Project system.

Defines configuration parameters for backtesting strategies.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, List


@dataclass
class BacktestConfig:
    """Configuration for backtesting strategies."""
    
    start_date: date
    """Start date for backtesting"""
    
    end_date: date
    """End date for backtesting"""
    
    initial_capital: float = 10000.0
    """Initial capital for backtesting (default: $10,000)"""
    
    rebalancing_frequency: str = 'monthly'
    """Rebalancing frequency ('daily', 'weekly', 'monthly', 'quarterly')"""
    
    evaluation_period: str = 'monthly'
    """Evaluation period for returns calculation ('daily', 'weekly', 'monthly', 'quarterly')"""
    
    transaction_costs: float = 0.001
    """Transaction costs as a percentage (default: 0.1%)"""
    
    max_weight: float = 0.1
    """Maximum weight for any single stock (default: 10%)"""
    
    min_weight: float = 0.0
    """Minimum weight for any single stock (default: 0%)"""
    
    risk_aversion: float = 0.5
    """Risk aversion parameter for portfolio optimization (default: 0.5)"""
    
    universe_tickers: Optional[List[str]] = None
    """List of tickers in the universe (optional)"""
    
    benchmark_ticker: str = 'SPY'
    """Benchmark ticker for comparison (default: SPY)"""
    
    use_equal_weight_benchmark: bool = True
    """Whether to use equal-weight portfolio of all stocks as benchmark (default: True)"""
    
    min_lookback_days: int = 252
    """Minimum lookback period for price data (default: 1 year)"""
    
    max_lookback_days: int = 756
    """Maximum lookback period for price data (default: 3 years)"""
    
    signal_weights: Optional[dict] = None
    """Weights for combining signals (optional)"""
    
    forward_fill_signals: bool = True
    """Whether to forward fill missing signal scores with latest available values (default: True)"""
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        
        if not 0 <= self.transaction_costs <= 1:
            raise ValueError("Transaction costs must be between 0 and 1")
        
        if not 0 <= self.max_weight <= 1:
            raise ValueError("Max weight must be between 0 and 1")
        
        if not 0 <= self.min_weight <= self.max_weight:
            raise ValueError("Min weight must be between 0 and max weight")
        
        if not 0 <= self.risk_aversion <= 1:
            raise ValueError("Risk aversion must be between 0 and 1")
        
        if self.min_lookback_days <= 0:
            raise ValueError("Min lookback days must be positive")
        
        if self.max_lookback_days < self.min_lookback_days:
            raise ValueError("Max lookback days must be >= min lookback days")
        
        # Validate frequency strings
        valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        if self.rebalancing_frequency not in valid_frequencies:
            raise ValueError(f"Rebalancing frequency must be one of {valid_frequencies}")
        
        if self.evaluation_period not in valid_frequencies:
            raise ValueError(f"Evaluation period must be one of {valid_frequencies}")
    
    def get_rebalancing_interval(self) -> timedelta:
        """
        Get the rebalancing interval as a timedelta.
        
        Returns:
            Timedelta representing the rebalancing interval
        """
        if self.rebalancing_frequency == 'daily':
            return timedelta(days=1)
        elif self.rebalancing_frequency == 'weekly':
            return timedelta(weeks=1)
        elif self.rebalancing_frequency == 'monthly':
            return timedelta(days=30)  # Approximate
        elif self.rebalancing_frequency == 'quarterly':
            return timedelta(days=90)  # Approximate
        else:
            raise ValueError(f"Unknown rebalancing frequency: {self.rebalancing_frequency}")
    
    def get_evaluation_interval(self) -> timedelta:
        """
        Get the evaluation interval as a timedelta.
        
        Returns:
            Timedelta representing the evaluation interval
        """
        if self.evaluation_period == 'daily':
            return timedelta(days=1)
        elif self.evaluation_period == 'weekly':
            return timedelta(weeks=1)
        elif self.evaluation_period == 'monthly':
            return timedelta(days=30)  # Approximate
        elif self.evaluation_period == 'quarterly':
            return timedelta(days=90)  # Approximate
        else:
            raise ValueError(f"Unknown evaluation period: {self.evaluation_period}")
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'rebalancing_frequency': self.rebalancing_frequency,
            'evaluation_period': self.evaluation_period,
            'transaction_costs': self.transaction_costs,
            'max_weight': self.max_weight,
            'min_weight': self.min_weight,
            'risk_aversion': self.risk_aversion,
            'universe_tickers': self.universe_tickers,
            'benchmark_ticker': self.benchmark_ticker,
            'use_equal_weight_benchmark': self.use_equal_weight_benchmark,
            'min_lookback_days': self.min_lookback_days,
            'max_lookback_days': self.max_lookback_days,
            'forward_fill_signals': self.forward_fill_signals
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'BacktestConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"BacktestConfig({self.start_date} to {self.end_date}, {self.rebalancing_frequency} rebalancing)"
