"""
Backtesting models for the Quant Project system.

Defines the BacktestResult class and related data structures.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np


@dataclass
class BacktestResult:
    """Results from a backtesting run."""
    
    backtest_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)
    
    # Strategy parameters
    tickers: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    signal_weights: Dict[str, float] = field(default_factory=dict)
    
    # Performance metrics
    total_return: float = 0.0
    annualized_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    
    # Risk metrics
    alpha: float = 0.0
    beta: float = 0.0
    information_ratio: float = 0.0
    tracking_error: float = 0.0
    
    # Portfolio metrics
    num_rebalances: int = 0
    avg_turnover: float = 0.0
    avg_num_positions: float = 0.0
    max_concentration: float = 0.0
    
    # Time series data
    portfolio_values: pd.Series = field(default_factory=pd.Series)
    benchmark_values: pd.Series = field(default_factory=pd.Series)
    returns: pd.Series = field(default_factory=pd.Series)
    benchmark_returns: pd.Series = field(default_factory=pd.Series)
    weights_history: pd.DataFrame = field(default_factory=pd.DataFrame)
    
    # Metadata
    execution_time_seconds: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of backtest results.
        
        Returns:
            Dictionary with key performance metrics
        """
        return {
            'backtest_id': self.backtest_id,
            'period': f"{self.start_date} to {self.end_date}",
            'total_return': f"{self.total_return:.2%}",
            'annualized_return': f"{self.annualized_return:.2%}",
            'volatility': f"{self.volatility:.2%}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'alpha': f"{self.alpha:.2%}",
            'information_ratio': f"{self.information_ratio:.2f}",
            'num_rebalances': self.num_rebalances,
            'avg_turnover': f"{self.avg_turnover:.2%}",
            'execution_time': f"{self.execution_time_seconds:.1f}s"
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get performance metrics as a dictionary.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'alpha': self.alpha,
            'beta': self.beta,
            'information_ratio': self.information_ratio,
            'tracking_error': self.tracking_error
        }
    
    def get_portfolio_metrics(self) -> Dict[str, float]:
        """
        Get portfolio metrics as a dictionary.
        
        Returns:
            Dictionary with portfolio metrics
        """
        return {
            'num_rebalances': self.num_rebalances,
            'avg_turnover': self.avg_turnover,
            'avg_num_positions': self.avg_num_positions,
            'max_concentration': self.max_concentration
        }
    
    def get_returns_analysis(self) -> Dict[str, Any]:
        """
        Get detailed returns analysis.
        
        Returns:
            Dictionary with returns analysis
        """
        if self.returns.empty:
            return {}
        
        returns = self.returns.dropna()
        
        return {
            'total_return': returns.sum(),
            'annualized_return': (1 + returns).prod() ** (252 / len(returns)) - 1,
            'volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(returns),
            'win_rate': (returns > 0).mean(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'var_95': returns.quantile(0.05),
            'var_99': returns.quantile(0.01),
            'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),
            'cvar_99': returns[returns <= returns.quantile(0.01)].mean()
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown from returns series."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def get_benchmark_comparison(self) -> Dict[str, Any]:
        """
        Get benchmark comparison metrics.
        
        Returns:
            Dictionary with benchmark comparison
        """
        if self.returns.empty or self.benchmark_returns.empty:
            return {}
        
        # Align returns
        aligned_returns = pd.DataFrame({
            'strategy': self.returns,
            'benchmark': self.benchmark_returns
        }).dropna()
        
        if aligned_returns.empty:
            return {}
        
        strategy_returns = aligned_returns['strategy']
        benchmark_returns = aligned_returns['benchmark']
        
        # Calculate metrics
        excess_returns = strategy_returns - benchmark_returns
        
        return {
            'alpha': excess_returns.mean() * 252,  # Annualized
            'beta': np.cov(strategy_returns, benchmark_returns)[0, 1] / np.var(benchmark_returns),
            'information_ratio': excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0,
            'tracking_error': excess_returns.std() * np.sqrt(252),
            'correlation': strategy_returns.corr(benchmark_returns),
            'outperformance': (strategy_returns > benchmark_returns).mean()
        }
    
    def get_turnover_analysis(self) -> Dict[str, Any]:
        """
        Get turnover analysis.
        
        Returns:
            Dictionary with turnover analysis
        """
        if self.weights_history.empty:
            return {}
        
        # Calculate turnover for each rebalancing
        turnovers = []
        for i in range(1, len(self.weights_history)):
            prev_weights = self.weights_history.iloc[i-1]
            curr_weights = self.weights_history.iloc[i]
            
            # Calculate turnover as sum of absolute weight changes
            turnover = abs(curr_weights - prev_weights).sum()
            turnovers.append(turnover)
        
        if not turnovers:
            return {}
        
        return {
            'avg_turnover': np.mean(turnovers),
            'max_turnover': np.max(turnovers),
            'min_turnover': np.min(turnovers),
            'turnover_std': np.std(turnovers),
            'total_turnover': np.sum(turnovers)
        }
    
    def get_concentration_analysis(self) -> Dict[str, Any]:
        """
        Get portfolio concentration analysis.
        
        Returns:
            Dictionary with concentration analysis
        """
        if self.weights_history.empty:
            return {}
        
        # Calculate concentration metrics for each rebalancing
        herfindahl_indices = []
        max_weights = []
        num_positions = []
        
        for _, weights in self.weights_history.iterrows():
            active_weights = weights[weights > 0]
            
            if len(active_weights) > 0:
                herfindahl_indices.append((active_weights ** 2).sum())
                max_weights.append(active_weights.max())
                num_positions.append(len(active_weights))
        
        if not herfindahl_indices:
            return {}
        
        return {
            'avg_herfindahl_index': np.mean(herfindahl_indices),
            'max_herfindahl_index': np.max(herfindahl_indices),
            'avg_max_weight': np.mean(max_weights),
            'max_max_weight': np.max(max_weights),
            'avg_num_positions': np.mean(num_positions),
            'min_num_positions': np.min(num_positions),
            'max_num_positions': np.max(num_positions)
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert backtest result to DataFrame.
        
        Returns:
            DataFrame with backtest results
        """
        data = {
            'backtest_id': self.backtest_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'tickers': ','.join(self.tickers),
            'signals': ','.join(self.signals),
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'alpha': self.alpha,
            'information_ratio': self.information_ratio,
            'num_rebalances': self.num_rebalances,
            'avg_turnover': self.avg_turnover,
            'execution_time_seconds': self.execution_time_seconds,
            'created_at': self.created_at
        }
        
        return pd.DataFrame([data])
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert backtest result to dictionary.
        
        Returns:
            Dictionary representation of backtest result
        """
        return {
            'backtest_id': self.backtest_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'tickers': self.tickers,
            'signals': self.signals,
            'signal_weights': self.signal_weights,
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'alpha': self.alpha,
            'beta': self.beta,
            'information_ratio': self.information_ratio,
            'tracking_error': self.tracking_error,
            'num_rebalances': self.num_rebalances,
            'avg_turnover': self.avg_turnover,
            'avg_num_positions': self.avg_num_positions,
            'max_concentration': self.max_concentration,
            'execution_time_seconds': self.execution_time_seconds,
            'created_at': self.created_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BacktestResult':
        """
        Create backtest result from dictionary.
        
        Args:
            data: Dictionary representation of backtest result
            
        Returns:
            BacktestResult instance
        """
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of backtest result."""
        return f"BacktestResult(id={self.backtest_id[:8]}..., return={self.total_return:.2%}, sharpe={self.sharpe_ratio:.2f})"
    
    def __repr__(self) -> str:
        """Detailed string representation of backtest result."""
        return f"BacktestResult(backtest_id='{self.backtest_id}', start_date={self.start_date}, end_date={self.end_date})"
