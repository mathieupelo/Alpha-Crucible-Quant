"""
Plotting utilities for backtest results visualization.

Provides functions to create performance charts and comparisons.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class BacktestPlotter:
    """Class for creating backtest visualization plots."""
    
    def __init__(self, figsize: Tuple[int, int] = (15, 10)):
        """
        Initialize the plotter.
        
        Args:
            figsize: Figure size tuple (width, height)
        """
        self.figsize = figsize
        self.colors = {
            'strategy': '#2E86AB',
            'benchmark': '#A23B72', 
            'universe': '#F18F01',
            'cash': '#C73E1D'
        }
    
    def _ensure_datetime_index(self, series: pd.Series) -> pd.Series:
        """Ensure the series has a DatetimeIndex."""
        if not isinstance(series.index, pd.DatetimeIndex):
            series = series.copy()
            series.index = pd.to_datetime(series.index)
        return series
    
    def plot_performance_comparison(self, 
                                  strategy_returns: pd.Series,
                                  benchmark_returns: pd.Series,
                                  universe_returns: Optional[pd.Series] = None,
                                  title: str = "Strategy Performance Comparison",
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot cumulative returns comparison between strategy, benchmark, and universe.
        
        Args:
            strategy_returns: Strategy returns time series
            benchmark_returns: Benchmark returns time series  
            universe_returns: Universe index returns time series (optional)
            title: Plot title
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, height_ratios=[3, 1])
        
        # Ensure datetime index
        strategy_returns = self._ensure_datetime_index(strategy_returns)
        benchmark_returns = self._ensure_datetime_index(benchmark_returns)
        
        # Calculate cumulative returns
        strategy_cumulative = (1 + strategy_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        # Plot cumulative returns
        ax1.plot(strategy_cumulative.index, strategy_cumulative.values, 
                label='Strategy', color=self.colors['strategy'], linewidth=2)
        ax1.plot(benchmark_cumulative.index, benchmark_cumulative.values, 
                label='Benchmark (SPY)', color=self.colors['benchmark'], linewidth=2)
        
        if universe_returns is not None:
            universe_returns = self._ensure_datetime_index(universe_returns)
            universe_cumulative = (1 + universe_returns).cumprod()
            ax1.plot(universe_cumulative.index, universe_cumulative.values, 
                    label='Universe Index', color=self.colors['universe'], linewidth=2)
        
        ax1.set_title(title, fontsize=16, fontweight='bold')
        ax1.set_ylabel('Cumulative Returns', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot rolling returns (30-day)
        if len(strategy_returns) > 30:
            strategy_rolling = strategy_returns.rolling(30).mean() * 252  # Annualized
            benchmark_rolling = benchmark_returns.rolling(30).mean() * 252
            
            ax2.plot(strategy_rolling.index, strategy_rolling.values, 
                    label='Strategy (30d)', color=self.colors['strategy'], alpha=0.7)
            ax2.plot(benchmark_rolling.index, benchmark_rolling.values, 
                    label='Benchmark (30d)', color=self.colors['benchmark'], alpha=0.7)
            
            ax2.set_ylabel('Rolling Returns (Annualized)', fontsize=12)
            ax2.legend(fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Format x-axis for bottom plot
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_drawdown(self, 
                     strategy_returns: pd.Series,
                     benchmark_returns: pd.Series,
                     title: str = "Drawdown Analysis",
                     save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot drawdown analysis for strategy and benchmark.
        
        Args:
            strategy_returns: Strategy returns time series
            benchmark_returns: Benchmark returns time series
            title: Plot title
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(self.figsize[0], self.figsize[1] // 2))
        
        # Ensure datetime index
        strategy_returns = self._ensure_datetime_index(strategy_returns)
        benchmark_returns = self._ensure_datetime_index(benchmark_returns)
        
        # Calculate drawdowns
        strategy_cumulative = (1 + strategy_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        strategy_drawdown = (strategy_cumulative / strategy_cumulative.cummax() - 1) * 100
        benchmark_drawdown = (benchmark_cumulative / benchmark_cumulative.cummax() - 1) * 100
        
        # Plot drawdowns
        ax.fill_between(strategy_drawdown.index, strategy_drawdown.values, 0, 
                       alpha=0.3, color=self.colors['strategy'], label='Strategy Drawdown')
        ax.fill_between(benchmark_drawdown.index, benchmark_drawdown.values, 0, 
                       alpha=0.3, color=self.colors['benchmark'], label='Benchmark Drawdown')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_rolling_metrics(self, 
                           strategy_returns: pd.Series,
                           benchmark_returns: pd.Series,
                           window: int = 252,
                           title: str = "Rolling Performance Metrics",
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot rolling Sharpe ratio and other metrics.
        
        Args:
            strategy_returns: Strategy returns time series
            benchmark_returns: Benchmark returns time series
            window: Rolling window size (default: 252 trading days)
            title: Plot title
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.figsize[0], self.figsize[1] // 2))
        
        # Ensure datetime index
        strategy_returns = self._ensure_datetime_index(strategy_returns)
        benchmark_returns = self._ensure_datetime_index(benchmark_returns)
        
        # Calculate rolling Sharpe ratios
        strategy_sharpe = (strategy_returns.rolling(window).mean() / 
                          strategy_returns.rolling(window).std()) * np.sqrt(252)
        benchmark_sharpe = (benchmark_returns.rolling(window).mean() / 
                           benchmark_returns.rolling(window).std()) * np.sqrt(252)
        
        # Plot Sharpe ratios
        ax1.plot(strategy_sharpe.index, strategy_sharpe.values, 
                label='Strategy Sharpe', color=self.colors['strategy'], linewidth=2)
        ax1.plot(benchmark_sharpe.index, benchmark_sharpe.values, 
                label='Benchmark Sharpe', color=self.colors['benchmark'], linewidth=2)
        
        ax1.set_title(f'Rolling Sharpe Ratio ({window}d window)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Sharpe Ratio', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Calculate rolling volatility
        strategy_vol = strategy_returns.rolling(window).std() * np.sqrt(252) * 100
        benchmark_vol = benchmark_returns.rolling(window).std() * np.sqrt(252) * 100
        
        ax2.plot(strategy_vol.index, strategy_vol.values, 
                label='Strategy Volatility', color=self.colors['strategy'], linewidth=2)
        ax2.plot(benchmark_vol.index, benchmark_vol.values, 
                label='Benchmark Volatility', color=self.colors['benchmark'], linewidth=2)
        
        ax2.set_title(f'Rolling Volatility ({window}d window)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Volatility (%)', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_monthly_returns_heatmap(self, 
                                   returns: pd.Series,
                                   title: str = "Monthly Returns Heatmap",
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a heatmap of monthly returns.
        
        Args:
            returns: Returns time series
            title: Plot title
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create monthly returns matrix
        returns = self._ensure_datetime_index(returns)
        monthly_returns = returns.resample('ME').apply(lambda x: (1 + x).prod() - 1) * 100
        
        # Create year-month matrix
        returns_matrix = monthly_returns.groupby([monthly_returns.index.year, 
                                                monthly_returns.index.month]).first()
        returns_matrix = returns_matrix.unstack(level=1)
        
        # Create heatmap
        sns.heatmap(returns_matrix, annot=True, fmt='.1f', cmap='RdYlGn', 
                   center=0, ax=ax, cbar_kws={'label': 'Monthly Return (%)'})
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Year', fontsize=12)
        
        # Set month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax.set_xticklabels(month_labels)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_portfolio_composition(self, 
                                 portfolio_history: List[Dict],
                                 title: str = "Portfolio Composition Over Time",
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot portfolio composition over time.
        
        Args:
            portfolio_history: List of portfolio dictionaries with dates and positions
            title: Plot title
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib Figure object
        """
        if not portfolio_history:
            fig, ax = plt.subplots(figsize=self.figsize)
            ax.text(0.5, 0.5, 'No portfolio data available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16)
            ax.set_title(title, fontsize=16, fontweight='bold')
            return fig
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Extract dates and positions
        dates = [p['date'] for p in portfolio_history]
        positions = [p.get('positions', {}) for p in portfolio_history]
        
        # Get all unique tickers
        all_tickers = set()
        for pos in positions:
            all_tickers.update(pos.keys())
        all_tickers = sorted(list(all_tickers))
        
        # Create stacked area plot
        bottom = np.zeros(len(dates))
        colors = plt.cm.Set3(np.linspace(0, 1, len(all_tickers)))
        
        for i, ticker in enumerate(all_tickers):
            weights = [pos.get(ticker, 0) for pos in positions]
            ax.fill_between(dates, bottom, bottom + weights, 
                           label=ticker, alpha=0.7, color=colors[i])
            bottom += weights
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel('Portfolio Weight', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


def create_backtest_summary_plots(backtest_result,
                                strategy_returns: pd.Series,
                                benchmark_returns: pd.Series,
                                universe_returns: Optional[pd.Series] = None,
                                portfolio_history: Optional[List[Dict]] = None,
                                save_dir: Optional[str] = None) -> List[plt.Figure]:
    """
    Create a comprehensive set of backtest visualization plots.
    
    Args:
        backtest_result: BacktestResult object
        strategy_returns: Strategy returns time series
        benchmark_returns: Benchmark returns time series
        universe_returns: Universe index returns time series (optional)
        portfolio_history: Portfolio composition history (optional)
        save_dir: Directory to save plots (optional)
        
    Returns:
        List of matplotlib Figure objects
    """
    plotter = BacktestPlotter()
    figures = []
    
    # 1. Performance comparison
    fig1 = plotter.plot_performance_comparison(
        strategy_returns, benchmark_returns, universe_returns,
        title=f"Strategy Performance: {backtest_result.start_date} to {backtest_result.end_date}",
        save_path=f"{save_dir}/performance_comparison.png" if save_dir else None
    )
    figures.append(fig1)
    
    # 2. Drawdown analysis
    fig2 = plotter.plot_drawdown(
        strategy_returns, benchmark_returns,
        title="Drawdown Analysis",
        save_path=f"{save_dir}/drawdown_analysis.png" if save_dir else None
    )
    figures.append(fig2)
    
    # 3. Rolling metrics
    fig3 = plotter.plot_rolling_metrics(
        strategy_returns, benchmark_returns,
        title="Rolling Performance Metrics",
        save_path=f"{save_dir}/rolling_metrics.png" if save_dir else None
    )
    figures.append(fig3)
    
    # 4. Monthly returns heatmap
    fig4 = plotter.plot_monthly_returns_heatmap(
        strategy_returns,
        title="Strategy Monthly Returns",
        save_path=f"{save_dir}/monthly_returns_heatmap.png" if save_dir else None
    )
    figures.append(fig4)
    
    # 5. Portfolio composition (if available)
    if portfolio_history:
        fig5 = plotter.plot_portfolio_composition(
            portfolio_history,
            title="Portfolio Composition Over Time",
            save_path=f"{save_dir}/portfolio_composition.png" if save_dir else None
        )
        figures.append(fig5)
    
    return figures
