"""
Backtesting engine for the Quant Project system.

Implements comprehensive backtesting with portfolio optimization and performance analysis.
"""

import logging
import time
import uuid
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np

from .config import BacktestConfig
from .models import BacktestResult
from .plotting import create_backtest_summary_plots
from signals import SignalCalculator
from solver import PortfolioSolver, SolverConfig
from database import DatabaseManager, Backtest, BacktestNav, Portfolio, PortfolioPosition
from utils import PriceFetcher, DateUtils

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Main backtesting engine for quantitative strategies."""
    
    def __init__(self, price_fetcher: Optional[PriceFetcher] = None,
                 signal_calculator: Optional[SignalCalculator] = None,
                 database_manager: Optional[DatabaseManager] = None):
        """
        Initialize backtesting engine.
        
        Args:
            price_fetcher: Price fetcher instance (optional)
            signal_calculator: Signal calculator instance (optional)
            database_manager: Database manager instance (optional)
        """
        self.price_fetcher = price_fetcher or PriceFetcher()
        self.signal_calculator = signal_calculator or SignalCalculator(self.price_fetcher)
        self.database_manager = database_manager or DatabaseManager()
        self.portfolio_solver = PortfolioSolver()
        
        # Data for plotting
        self.strategy_returns = None
        self.benchmark_returns = None
        self.universe_returns = None
        self.portfolio_history = []
    
    def run_backtest(self, tickers: List[str], signals: List[str], 
                    config: BacktestConfig) -> BacktestResult:
        """
        Run a comprehensive backtest.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs to use
            config: Backtesting configuration
            
        Returns:
            BacktestResult with performance metrics
        """
        start_time = time.time()
        logger.info(f"Starting backtest for {len(tickers)} tickers, {len(signals)} signals from {config.start_date} to {config.end_date}")
        
        try:
            # Generate unique run_id
            run_id = f"backtest_{int(time.time())}_{config.start_date}_{config.end_date}"
            
            # Store backtest configuration
            backtest_config = Backtest(
                run_id=run_id,
                start_date=config.start_date,
                end_date=config.end_date,
                frequency=config.rebalancing_frequency,
                universe={'tickers': tickers, 'signals': signals},
                benchmark=config.benchmark_ticker,
                params={
                    'initial_capital': config.initial_capital,
                    'risk_aversion': config.risk_aversion,
                    'max_weight': config.max_weight,
                    'min_weight': config.min_weight,
                    'transaction_costs': config.transaction_costs,
                    'signal_weights': config.signal_weights
                },
                created_at=datetime.now()
            )
            
            # Store backtest configuration in database
            try:
                self.database_manager.store_backtest(backtest_config)
                logger.info(f"Stored backtest configuration with run_id: {run_id}")
            except Exception as e:
                logger.error(f"Error storing backtest configuration: {e}")
            
            # Initialize result
            result = BacktestResult(
                backtest_id=run_id,
                start_date=config.start_date,
                end_date=config.end_date,
                tickers=tickers,
                signals=signals,
                signal_weights=config.signal_weights or {signal: 1.0/len(signals) for signal in signals}
            )
            
            # Get trading days
            trading_days = DateUtils.get_trading_days(config.start_date, config.end_date)
            logger.info(f"Found {len(trading_days)} trading days")
            
            # Get rebalancing dates
            rebalancing_dates = self._get_rebalancing_dates(trading_days, config)
            logger.info(f"Found {len(rebalancing_dates)} rebalancing dates")
            
            # Get price data for all tickers
            price_data = self._get_price_data(tickers, config)
            if price_data is None or price_data.empty:
                logger.error("Failed to get price data")
                return result
            
            # Get signal scores (combined scores)
            signal_scores = self._get_signal_scores(tickers, signals, config)
            if signal_scores.empty:
                logger.error("Failed to get signal scores")
                return result
            
            # Run backtest simulation
            portfolio_values, benchmark_values, weights_history = self._run_simulation(
                tickers, signals, signal_scores, price_data, rebalancing_dates, config
            )
            
            # Calculate performance metrics
            self._calculate_performance_metrics(result, portfolio_values, benchmark_values, config)
            
            # Store time series data
            result.portfolio_values = portfolio_values
            result.benchmark_values = benchmark_values
            result.weights_history = weights_history
            
            # Calculate additional metrics
            result.num_rebalances = len(rebalancing_dates)
            result.avg_turnover = self._calculate_avg_turnover(weights_history)
            result.avg_num_positions = self._calculate_avg_num_positions(weights_history)
            result.max_concentration = self._calculate_max_concentration(weights_history)
            
            # Store portfolio data in database
            try:
                # Store portfolio values and weights
                self._store_portfolio_data(result, portfolio_values, benchmark_values, weights_history)
                logger.info("Stored portfolio data in database")
            except Exception as e:
                logger.error(f"Error storing portfolio data: {e}")
            
            # Calculate execution time
            result.execution_time_seconds = time.time() - start_time
            
            logger.info(f"Backtest completed in {result.execution_time_seconds:.1f} seconds")
            logger.info(f"Total return: {result.total_return:.2%}, Sharpe ratio: {result.sharpe_ratio:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            result.execution_time_seconds = time.time() - start_time
            return result
    
    def _get_rebalancing_dates(self, trading_days: List[date], config: BacktestConfig) -> List[date]:
        """Get rebalancing dates based on frequency."""
        if config.rebalancing_frequency == 'daily':
            return trading_days
        elif config.rebalancing_frequency == 'weekly':
            # Rebalance on Mondays
            return [day for day in trading_days if day.weekday() == 0]
        elif config.rebalancing_frequency == 'monthly':
            # Rebalance on first trading day of each month
            rebalancing_dates = []
            current_month = None
            for day in trading_days:
                if day.month != current_month:
                    rebalancing_dates.append(day)
                    current_month = day.month
            return rebalancing_dates
        elif config.rebalancing_frequency == 'quarterly':
            # Rebalance on first trading day of each quarter
            rebalancing_dates = []
            current_quarter = None
            for day in trading_days:
                quarter = (day.month - 1) // 3 + 1
                if quarter != current_quarter:
                    rebalancing_dates.append(day)
                    current_quarter = quarter
            return rebalancing_dates
        else:
            raise ValueError(f"Unknown rebalancing frequency: {config.rebalancing_frequency}")
    
    def _get_price_data(self, tickers: List[str], config: BacktestConfig) -> Optional[pd.DataFrame]:
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
    
    def _get_signal_scores(self, tickers: List[str], signals: List[str], 
                          config: BacktestConfig) -> pd.DataFrame:
        """Get signal scores for all tickers and signals."""
        try:
            # Extend start date to get enough lookback data
            extended_start = config.start_date - timedelta(days=config.max_lookback_days)
            
            # First try to get combined scores
            signal_scores = self.signal_calculator.get_scores_combined_pivot(
                tickers, ['equal_weight'], extended_start, config.end_date, 
                forward_fill=config.forward_fill_signals
            )
            
            if signal_scores.empty:
                logger.warning("No combined scores found, calculating raw signals and combining...")
                
                # Calculate raw signals
                raw_signals = self.signal_calculator.calculate_signals(
                    tickers, signals, extended_start, config.end_date
                )
                
                if not raw_signals.empty:
                    # Combine signals into scores
                    signal_scores = self.signal_calculator.combine_signals_to_scores(
                        tickers, signals, extended_start, config.end_date,
                        method='equal_weight',
                        store_in_db=True
                    )
                    
                    # Convert to pivot format
                    if not signal_scores.empty:
                        signal_scores = signal_scores.pivot_table(
                            index='asof_date',
                            columns='ticker',
                            values='score',
                            aggfunc='first'
                        )
            
            logger.info(f"Retrieved signal scores for {len(signal_scores.columns)} tickers")
            return signal_scores
            
        except Exception as e:
            logger.error(f"Error getting signal scores: {e}")
            return pd.DataFrame()
    
    def _run_simulation(self, tickers: List[str], signals: List[str], 
                       signal_scores: pd.DataFrame, price_data: pd.DataFrame,
                       rebalancing_dates: List[date], config: BacktestConfig) -> Tuple[pd.Series, pd.Series, pd.DataFrame]:
        """Run the backtest simulation."""
        logger.info("Starting backtest simulation...")
        
        # Initialize tracking variables
        portfolio_value = config.initial_capital
        benchmark_value = config.initial_capital
        
        portfolio_values = pd.Series(index=price_data.index, dtype=float)
        benchmark_values = pd.Series(index=price_data.index, dtype=float)
        weights_history = pd.DataFrame(index=rebalancing_dates, columns=tickers, dtype=float)
        
        # Store returns for plotting
        strategy_returns = pd.Series(index=price_data.index, dtype=float)
        benchmark_returns = pd.Series(index=price_data.index, dtype=float)
        
        current_weights = None
        benchmark_ready = False
        
        # Get benchmark data
        if config.use_equal_weight_benchmark:
            # Use equal-weight portfolio of all stocks as benchmark
            logger.info("Using equal-weight portfolio of all stocks as benchmark")
            benchmark_data = price_data  # Use the same price data as the strategy
        else:
            # Use traditional benchmark ticker (e.g., SPY)
            benchmark_data = self.price_fetcher.get_price_history(
                config.benchmark_ticker, config.start_date, config.end_date
            )
            
            # Ensure benchmark data is aligned with price data
            if benchmark_data is not None and not benchmark_data.empty:
                # Align benchmark data with price data dates
                benchmark_data = benchmark_data.reindex(price_data.index, method='ffill')
            else:
                logger.warning(f"No benchmark data available for {config.benchmark_ticker}")
                benchmark_data = pd.DataFrame()
        
        # Find the first rebalancing date to ensure both strategy and benchmark start together
        first_rebalance_date = None
        for current_date in price_data.index:
            if current_date >= config.start_date and current_date in rebalancing_dates:
                first_rebalance_date = current_date
                break
        
        if first_rebalance_date is None:
            logger.error("No valid rebalancing dates found within the backtest period")
            return pd.Series(), pd.Series(), pd.DataFrame()
        
        logger.info(f"Strategy and benchmark will start on: {first_rebalance_date}")
        
        for i, current_date in enumerate(price_data.index):
            if current_date < first_rebalance_date:
                continue
            
            # Check if this is a rebalancing date
            is_rebalance = current_date in rebalancing_dates
            
            if is_rebalance:
                # Rebalance portfolio
                new_weights = self._rebalance_portfolio(
                    tickers, signals, signal_scores, price_data, current_date, config
                )
                
                if new_weights is not None:
                    current_weights = new_weights
                    weights_history.loc[current_date] = current_weights
                    
                    # Calculate transaction costs
                    if current_weights is not None and len(weights_history) > 1:
                        prev_weights = weights_history.iloc[-2] if len(weights_history) > 1 else pd.Series(0, index=tickers)
                        turnover = abs(current_weights - prev_weights).sum()
                        transaction_cost = turnover * config.transaction_costs
                        portfolio_value *= (1 - transaction_cost)
                
                # Mark that benchmark is ready (no need for benchmark weights since we use SPY directly)
                benchmark_ready = True
            
            # Update portfolio value
            if current_weights is not None:
                portfolio_return = self._calculate_portfolio_return(
                    current_weights, price_data, current_date, i
                )
                if portfolio_return is not None:
                    portfolio_value *= (1 + portfolio_return)
                    strategy_returns.loc[current_date] = portfolio_return
            
            # Update benchmark value (only after first rebalance)
            if benchmark_ready and not benchmark_data.empty and current_date in benchmark_data.index:
                if config.use_equal_weight_benchmark:
                    # Calculate equal-weight portfolio return
                    benchmark_return = self._calculate_equal_weight_return(
                        tickers, benchmark_data, current_date, i
                    )
                else:
                    # Calculate traditional benchmark return (e.g., SPY)
                    benchmark_return = self._calculate_benchmark_return(
                        benchmark_data, current_date, i
                    )
                
                if benchmark_return is not None:
                    benchmark_value *= (1 + benchmark_return)
                    benchmark_returns.loc[current_date] = benchmark_return
            
            # Store values
            portfolio_values.loc[current_date] = portfolio_value
            benchmark_values.loc[current_date] = benchmark_value
            
            # Progress logging
            if i % 50 == 0:
                logger.info(f"Processed {i+1}/{len(price_data)} days, portfolio value: ${portfolio_value:,.2f}")
        
        logger.info("Backtest simulation completed")
        
        # Store returns data for plotting
        self.strategy_returns = strategy_returns.dropna()
        self.benchmark_returns = benchmark_returns.dropna()
        self._use_equal_weight_benchmark = config.use_equal_weight_benchmark
        
        # Store portfolio history for plotting
        for date_idx, date in enumerate(weights_history.index):
            if not weights_history.loc[date].isna().all():
                self.portfolio_history.append({
                    'date': date,
                    'positions': weights_history.loc[date].to_dict()
                })
        
        return portfolio_values, benchmark_values, weights_history
    
    def _rebalance_portfolio(self, tickers: List[str], signals: List[str],
                           signal_scores: pd.DataFrame, price_data: pd.DataFrame,
                           current_date: date, config: BacktestConfig) -> Optional[pd.Series]:
        """Rebalance portfolio on a specific date."""
        try:
            # Get signal scores for current date
            if current_date not in signal_scores.index:
                # Try to find the latest available date before current_date
                available_dates = signal_scores.index[signal_scores.index <= current_date]
                if len(available_dates) == 0:
                    logger.warning(f"No signal scores available for {current_date} or earlier")
                    return None
                
                # Use the latest available date
                latest_date = available_dates[-1]
                logger.info(f"No signal scores for {current_date}, using latest available from {latest_date}")
                date_scores = signal_scores.loc[latest_date]
            else:
                date_scores = signal_scores.loc[current_date]
            
            # Use combined scores directly (already combined from database)
            combined_scores = {}
            for ticker in tickers:
                try:
                    if ticker in date_scores.index:
                        score = date_scores[ticker]
                        if not pd.isna(score):
                            combined_scores[ticker] = float(score)
                        else:
                            combined_scores[ticker] = 0.0
                    else:
                        combined_scores[ticker] = 0.0
                except Exception as e:
                    logger.warning(f"Error getting score for {ticker}: {e}")
                    combined_scores[ticker] = 0.0
            
            if not combined_scores:
                logger.warning(f"No valid signal scores for {current_date}")
                return None
            
            # Get price history for optimization
            lookback_start = current_date - timedelta(days=config.min_lookback_days)
            price_history = price_data[price_data.index >= lookback_start]
            
            if price_history.empty:
                logger.warning(f"Insufficient price history for {current_date}")
                return None
            
            # Create solver config
            solver_config = SolverConfig(
                risk_aversion=config.risk_aversion,
                max_weight=config.max_weight,
                min_weight=config.min_weight
            )
            
            # Solve portfolio
            solver = PortfolioSolver(solver_config)
            portfolio = solver.solve_portfolio(combined_scores, price_history, current_date)
            
            if portfolio is None:
                logger.warning(f"Portfolio optimization failed for {current_date}")
                return None
            
            # Convert to Series
            weights = pd.Series(0.0, index=tickers)
            for ticker, position in portfolio.positions.items():
                if ticker in tickers:
                    weights[ticker] = position.weight
            
            return weights
            
        except Exception as e:
            logger.error(f"Error rebalancing portfolio on {current_date}: {e}")
            return None
    
    def _calculate_portfolio_return(self, weights: pd.Series, price_data: pd.DataFrame,
                                  current_date: date, current_index: int) -> Optional[float]:
        """Calculate portfolio return for a given date."""
        try:
            if current_index == 0:
                return 0.0  # No return on first day
            
            prev_date = price_data.index[current_index - 1]
            
            # Get current and previous prices
            current_prices = price_data.loc[current_date]
            prev_prices = price_data.loc[prev_date]
            
            # Calculate returns
            returns = (current_prices - prev_prices) / prev_prices
            
            # Calculate portfolio return
            portfolio_return = (weights * returns).sum()
            
            return portfolio_return if not pd.isna(portfolio_return) else None
            
        except Exception as e:
            logger.error(f"Error calculating portfolio return for {current_date}: {e}")
            return None
    
    def _calculate_equal_weight_return(self, tickers: List[str], price_data: pd.DataFrame,
                                     current_date: date, current_index: int) -> Optional[float]:
        """Calculate equal-weight portfolio return for a given date."""
        try:
            if current_index == 0:
                return 0.0  # No return on first day
            
            prev_date = price_data.index[current_index - 1]
            
            # Get current and previous prices for all tickers
            current_prices = price_data.loc[current_date]
            prev_prices = price_data.loc[prev_date]
            
            # Calculate individual stock returns
            returns = []
            for ticker in tickers:
                if ticker in current_prices.index and ticker in prev_prices.index:
                    current_price = current_prices[ticker]
                    prev_price = prev_prices[ticker]
                    
                    if not pd.isna(current_price) and not pd.isna(prev_price) and prev_price > 0:
                        stock_return = (current_price - prev_price) / prev_price
                        returns.append(stock_return)
            
            if not returns:
                return None
            
            # Equal-weight portfolio return is the average of individual returns
            equal_weight_return = np.mean(returns)
            
            return equal_weight_return if not pd.isna(equal_weight_return) else None
            
        except Exception as e:
            logger.error(f"Error calculating equal-weight return for {current_date}: {e}")
            return None
    
    def _calculate_benchmark_return(self, benchmark_data: pd.DataFrame,
                                  current_date: date, current_index: int) -> Optional[float]:
        """Calculate benchmark return for a given date."""
        try:
            if current_index == 0:
                return 0.0  # No return on first day
            
            prev_date = benchmark_data.index[current_index - 1]
            
            # Get current and previous benchmark prices
            current_price = benchmark_data.loc[current_date].iloc[0]  # First column (close price)
            prev_price = benchmark_data.loc[prev_date].iloc[0]
            
            # Calculate benchmark return
            benchmark_return = (current_price - prev_price) / prev_price
            
            return benchmark_return if not pd.isna(benchmark_return) else None
            
        except Exception as e:
            logger.error(f"Error calculating benchmark return for {current_date}: {e}")
            return None
    
    def _calculate_performance_metrics(self, result: BacktestResult, 
                                     portfolio_values: pd.Series, 
                                     benchmark_values: pd.Series,
                                     config: BacktestConfig):
        """Calculate performance metrics."""
        try:
            # Calculate returns
            portfolio_returns = portfolio_values.pct_change().dropna()
            benchmark_returns = benchmark_values.pct_change().dropna()
            
            # Align returns
            aligned_returns = pd.DataFrame({
                'portfolio': portfolio_returns,
                'benchmark': benchmark_returns
            }).dropna()
            
            if aligned_returns.empty:
                logger.warning("No aligned returns data for metrics calculation")
                return
            
            portfolio_returns = aligned_returns['portfolio']
            benchmark_returns = aligned_returns['benchmark']
            
            # Calculate metrics
            result.total_return = (portfolio_values.iloc[-1] / config.initial_capital) - 1
            result.annualized_return = (1 + result.total_return) ** (252 / len(portfolio_returns)) - 1
            result.volatility = portfolio_returns.std() * np.sqrt(252)
            result.sharpe_ratio = result.annualized_return / result.volatility if result.volatility > 0 else 0
            
            # Calculate max drawdown
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            result.max_drawdown = drawdown.min()
            
            # Calculate win rate
            result.win_rate = (portfolio_returns > 0).mean()
            
            # Calculate alpha and beta
            excess_returns = portfolio_returns - benchmark_returns
            result.alpha = excess_returns.mean() * 252  # Annualized
            result.beta = np.cov(portfolio_returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
            result.information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
            result.tracking_error = excess_returns.std() * np.sqrt(252)
            
            # Store returns series
            result.returns = portfolio_returns
            result.benchmark_returns = benchmark_returns
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
    
    def _calculate_avg_turnover(self, weights_history: pd.DataFrame) -> float:
        """Calculate average turnover."""
        if weights_history.empty or len(weights_history) < 2:
            return 0.0
        
        turnovers = []
        for i in range(1, len(weights_history)):
            prev_weights = weights_history.iloc[i-1]
            curr_weights = weights_history.iloc[i]
            turnover = abs(curr_weights - prev_weights).sum()
            turnovers.append(turnover)
        
        return np.mean(turnovers) if turnovers else 0.0
    
    def _calculate_avg_num_positions(self, weights_history: pd.DataFrame) -> float:
        """Calculate average number of positions."""
        if weights_history.empty:
            return 0.0
        
        num_positions = []
        for _, weights in weights_history.iterrows():
            num_positions.append((weights > 0).sum())
        
        return np.mean(num_positions) if num_positions else 0.0
    
    def _calculate_max_concentration(self, weights_history: pd.DataFrame) -> float:
        """Calculate maximum concentration."""
        if weights_history.empty:
            return 0.0
        
        max_weights = []
        for _, weights in weights_history.iterrows():
            max_weights.append(weights.max())
        
        return np.max(max_weights) if max_weights else 0.0
    
    def _store_portfolio_data(self, result: BacktestResult, portfolio_values: pd.Series, 
                            benchmark_values: pd.Series, weights_history: pd.DataFrame):
        """Store portfolio data in the database."""
        try:
            # Store backtest NAV data
            nav_objects = []
            for date, portfolio_value in portfolio_values.items():
                if pd.isna(portfolio_value):
                    continue
                    
                benchmark_value = benchmark_values.get(date, 0.0)
                if pd.isna(benchmark_value):
                    benchmark_value = 0.0
                
                # Calculate PnL
                pnl = 0.0
                if len(portfolio_values) > 1:
                    prev_date = portfolio_values.index[portfolio_values.index < date]
                    if len(prev_date) > 0:
                        prev_date = prev_date[-1]
                        prev_portfolio_value = portfolio_values.get(prev_date, portfolio_value)
                        if prev_portfolio_value > 0:
                            pnl = portfolio_value - prev_portfolio_value
                
                nav_obj = BacktestNav(
                    run_id=result.backtest_id,
                    date=date,
                    nav=float(portfolio_value),
                    benchmark_nav=float(benchmark_value) if benchmark_value > 0 else None,
                    pnl=float(pnl)
                )
                nav_objects.append(nav_obj)
            
            if nav_objects:
                self.database_manager.store_backtest_nav(nav_objects)
                logger.info(f"Stored {len(nav_objects)} NAV records")
            
            # Store portfolios and positions
            for date, weights_row in weights_history.iterrows():
                if weights_row.isna().all():
                    continue
                
                # Create portfolio
                portfolio = Portfolio(
                    run_id=result.backtest_id,
                    asof_date=date,
                    method='optimization',
                    params={'risk_aversion': result.signal_weights},
                    cash=0.0,  # Assuming no cash for now
                    notes=f'Portfolio for {date}',
                    created_at=datetime.now()
                )
                
                # Store portfolio and get ID
                portfolio_id = self.database_manager.store_portfolio(portfolio)
                
                # Store portfolio positions
                positions = []
                for ticker, weight in weights_row.items():
                    if pd.isna(weight) or weight == 0:
                        continue
                    
                    # Get price used (simplified - using last available price)
                    try:
                        price_data = self.price_fetcher.get_price_history(ticker, date, date)
                        price_used = price_data.iloc[-1]['Close'] if not price_data.empty else 0.0
                    except:
                        price_used = 0.0
                    
                    position = PortfolioPosition(
                        portfolio_id=portfolio_id,
                        ticker=ticker,
                        weight=float(weight),
                        price_used=float(price_used),
                        created_at=datetime.now()
                    )
                    positions.append(position)
                
                if positions:
                    self.database_manager.store_portfolio_positions(positions)
                    logger.info(f"Stored {len(positions)} positions for portfolio {portfolio_id}")
                
        except Exception as e:
            logger.error(f"Error storing portfolio data: {e}")
            raise
    
    def create_plots(self, save_dir: Optional[str] = None, show_plots: bool = True) -> List:
        """
        Create simplified backtest visualization plots (returns and volatility only).
        
        Args:
            save_dir: Directory to save plots (optional)
            show_plots: Whether to display plots (default: True)
            
        Returns:
            List of matplotlib Figure objects
        """
        if self.strategy_returns is None or self.benchmark_returns is None:
            logger.warning("No returns data available for plotting. Run backtest first.")
            return []
        
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import numpy as np
        
        figures = []
        
        # 1. Performance Comparison (Returns)
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        
        # Ensure datetime index and align both series
        strategy_returns = self.strategy_returns.copy()
        benchmark_returns = self.benchmark_returns.copy()
        
        if not isinstance(strategy_returns.index, pd.DatetimeIndex):
            strategy_returns.index = pd.to_datetime(strategy_returns.index)
        if not isinstance(benchmark_returns.index, pd.DatetimeIndex):
            benchmark_returns.index = pd.to_datetime(benchmark_returns.index)
        
        # Find the common date range
        start_date = max(strategy_returns.index[0], benchmark_returns.index[0])
        end_date = min(strategy_returns.index[-1], benchmark_returns.index[-1])
        
        # Filter both series to the common date range
        strategy_returns = strategy_returns.loc[start_date:end_date]
        benchmark_returns = benchmark_returns.loc[start_date:end_date]
        
        # Ensure both series have the same index (forward fill any missing dates)
        common_index = strategy_returns.index.union(benchmark_returns.index).sort_values()
        strategy_returns = strategy_returns.reindex(common_index, method='ffill')
        benchmark_returns = benchmark_returns.reindex(common_index, method='ffill')
        
        # Calculate cumulative returns starting from 1.0
        strategy_cumulative = (1 + strategy_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        # Plot cumulative returns
        ax1.plot(strategy_cumulative.index, strategy_cumulative.values, 
                label='Strategy', color='#2E86AB', linewidth=2)
        benchmark_label = 'Equal-Weight Portfolio' if hasattr(self, '_use_equal_weight_benchmark') and self._use_equal_weight_benchmark else 'Benchmark (SPY)'
        ax1.plot(benchmark_cumulative.index, benchmark_cumulative.values, 
                label=benchmark_label, color='#A23B72', linewidth=2)
        
        ax1.set_title('Strategy vs Benchmark Performance', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Cumulative Returns', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        figures.append(fig1)
        
        # 2. Rolling Volatility
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        
        # Calculate rolling volatility (30-day window)
        window = 30
        strategy_vol = strategy_returns.rolling(window).std() * np.sqrt(252) * 100
        benchmark_vol = benchmark_returns.rolling(window).std() * np.sqrt(252) * 100
        
        ax2.plot(strategy_vol.index, strategy_vol.values, 
                label='Strategy Volatility', color='#2E86AB', linewidth=2)
        ax2.plot(benchmark_vol.index, benchmark_vol.values, 
                label='Benchmark Volatility', color='#A23B72', linewidth=2)
        
        ax2.set_title(f'Rolling Volatility ({window}d window)', fontsize=16, fontweight='bold')
        ax2.set_ylabel('Volatility (%)', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        figures.append(fig2)
        
        if save_dir:
            fig1.savefig(f"{save_dir}/performance_comparison.png", dpi=300, bbox_inches='tight')
            fig2.savefig(f"{save_dir}/rolling_volatility.png", dpi=300, bbox_inches='tight')
        
        if show_plots:
            plt.show()
        
        return figures
