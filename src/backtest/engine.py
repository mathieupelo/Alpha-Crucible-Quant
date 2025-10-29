"""
Backtesting engine for the Quant Project system.

Implements comprehensive backtesting with portfolio optimization and performance analysis.
"""

import logging
import time
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
import numpy as np

from .config import BacktestConfig
from .models import BacktestResult
from src.signals import SignalReader
from src.portfolio import PortfolioService
from src.database import DatabaseManager, Backtest, BacktestNav, Portfolio, PortfolioPosition
from src.utils import PriceFetcher, DateUtils, TradingCalendar
from src.utils.error_handling import BacktestError, SignalError, validate_signal_scores_completeness

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Main backtesting engine for quantitative strategies.
    
    This class orchestrates the entire backtesting process, including:
    - Data preparation and validation
    - Signal calculation and scoring
    - Portfolio optimization and rebalancing
    - Performance metrics calculation
    - Results storage and visualization
    
    The engine supports multiple rebalancing frequencies (daily, weekly, monthly, quarterly)
    and various portfolio optimization methods including score-based allocation and
    mean-variance optimization.
    
    Attributes:
        price_fetcher: Instance for fetching stock price data
        signal_reader: Instance for reading investment signals
        database_manager: Instance for database operations
        portfolio_solver: Instance for portfolio optimization
        strategy_returns: Series of strategy returns for plotting
        benchmark_returns: Series of benchmark returns for plotting
        universe_returns: Series of universe returns for plotting
        portfolio_history: List of portfolio snapshots for plotting
    """
    
    def __init__(self, price_fetcher: Optional[PriceFetcher] = None,
                 signal_reader: Optional[SignalReader] = None,
                 database_manager: Optional[DatabaseManager] = None,
                 portfolio_service: Optional[PortfolioService] = None,
                 trading_calendar: Optional[TradingCalendar] = None):
        """
        Initialize backtesting engine.
        
        Args:
            price_fetcher: Price fetcher instance (optional)
            signal_reader: Signal reader instance (optional)
            database_manager: Database manager instance (optional)
            portfolio_service: Portfolio service instance (optional)
            trading_calendar: Trading calendar instance (optional)
        """
        self.price_fetcher = price_fetcher or PriceFetcher()
        self.signal_reader = signal_reader or SignalReader()
        self.database_manager = database_manager or DatabaseManager()
        self.portfolio_service = portfolio_service or PortfolioService(
            signal_reader=self.signal_reader,
            database_manager=self.database_manager,
            price_fetcher=self.price_fetcher
        )
        self.trading_calendar = trading_calendar or TradingCalendar()
        
        # Data for plotting
        self.strategy_returns = None
        self.benchmark_returns = None
        self.universe_returns = None
        self.portfolio_history = []
    
    def run_backtest(self, tickers: List[str], signals: List[str], 
                    config: BacktestConfig) -> BacktestResult:
        """
        Run a comprehensive backtest following the new architecture.
        
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
            # Validate universe requirements before proceeding
            logger.info("Validating universe requirements...")
            config.validate_universe_requirements(self.database_manager)
            logger.info("Universe validation passed")
            
            # Initialize backtest
            run_id, result = self._initialize_backtest(tickers, signals, config)
            
            # Step 1: Get portfolio creation dates (rebalancing dates)
            rebalancing_dates = self._get_rebalancing_dates(config)
            logger.info(f"Found {len(rebalancing_dates)} rebalancing dates")
            
            # Step 2: Fetch all signal scores for all rebalancing dates
            signal_scores = self._fetch_signal_scores(tickers, signals, rebalancing_dates, config)
            if signal_scores.empty:
                logger.error("Failed to fetch signal scores")
                return result
            
            # Step 3: Validate signal completeness - fail if any missing
            try:
                validate_signal_scores_completeness(tickers, signals, rebalancing_dates, self.signal_reader)
            except SignalError as e:
                logger.error(f"Signal validation failed: {e}")
                result.error_message = str(e)
                return result
            
            # Step 4: Create portfolios for all rebalancing dates
            logger.info("Creating portfolios for rebalancing dates...")
            portfolios_created = self._create_portfolios_for_dates(
                signal_scores, rebalancing_dates, tickers, config, run_id, result
            )
            if portfolios_created is None:  # Error occurred
                logger.error("Portfolio creation failed")
                return result
            logger.info(f"Created {len(portfolios_created)} portfolios")
            
            # Step 5: Run simulation using created portfolios
            logger.info("Running simulation with created portfolios...")
            portfolio_values, benchmark_values, weights_history, first_rebalance_date = self._run_simulation_with_portfolios(
                portfolios_created, tickers, config
            )
            logger.info(f"Simulation completed. Portfolio values: {len(portfolio_values)}, Benchmark values: {len(benchmark_values)}")
            
            # Step 6: Insert backtest in database
            self._store_backtest_results(result, portfolio_values, benchmark_values, weights_history, first_rebalance_date)
            
            # Calculate and store results
            logger.info("Finalizing backtest results...")
            self._finalize_backtest_results(
                result, portfolio_values, benchmark_values, weights_history, 
                first_rebalance_date, rebalancing_dates, start_time, config
            )
            logger.info("Backtest results finalized successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            if 'result' in locals():
                result.execution_time_seconds = time.time() - start_time
                result.error_message = str(e)
                return result
            else:
                # If result was never created, create a minimal error result
                from .models import BacktestResult
                error_result = BacktestResult(
                    backtest_id=f"error_{int(time.time())}",
                    start_date=config.start_date,
                    end_date=config.end_date,
                    tickers=tickers,
                    signals=signals,
                    error_message=str(e),
                    execution_time_seconds=time.time() - start_time
                )
                return error_result
    
    def _initialize_backtest(self, tickers: List[str], signals: List[str], 
                           config: BacktestConfig) -> Tuple[str, BacktestResult]:
        """
        Initialize backtest configuration and result object.
        
        Creates a unique run ID, stores the backtest configuration in the database,
        and initializes the result object with basic metadata.
        
        Args:
            tickers: List of stock ticker symbols to include in backtest
            signals: List of signal IDs to use for portfolio construction
            config: Backtesting configuration parameters
            
        Returns:
            Tuple containing:
                - run_id: Unique identifier for this backtest run
                - result: Initialized BacktestResult object
        """
        # Generate unique run_id
        run_id = f"backtest_{int(time.time())}_{config.start_date}_{config.end_date}"
        
        # Store backtest configuration
        backtest_config = Backtest(
            run_id=run_id,
            name=config.name,
            start_date=config.start_date,
            end_date=config.end_date,
            frequency=config.rebalancing_frequency,
            universe_id=config.universe_id,
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
            # Convert signal names to signal IDs for the signals table
            signal_ids = []
            signal_weights_dict = {}
            if signals:
                logger.info(f"Converting {len(signals)} signal names to signal IDs...")
                for signal_name in signals:
                    try:
                        signal_obj = self.database_manager.get_signal_by_name(signal_name)
                        if signal_obj:
                            signal_ids.append(signal_obj.id)
                            # Map signal name weights to signal ID weights
                            weight = config.signal_weights.get(signal_name, 1.0) if config.signal_weights else 1.0
                            signal_weights_dict[signal_obj.id] = weight
                            logger.debug(f"Found signal '{signal_name}' -> ID {signal_obj.id}")
                        else:
                            # Signal doesn't exist, try to create it
                            logger.warning(f"Signal '{signal_name}' not found in database, creating it...")
                            signal_obj = self.database_manager.get_or_create_signal(signal_name)
                            signal_ids.append(signal_obj.id)
                            weight = config.signal_weights.get(signal_name, 1.0) if config.signal_weights else 1.0
                            signal_weights_dict[signal_obj.id] = weight
                            logger.info(f"Created signal '{signal_name}' -> ID {signal_obj.id}")
                    except Exception as sig_error:
                        # If signal lookup fails, log but continue - we'll store backtest without signal relationships
                        logger.error(f"Error looking up signal '{signal_name}': {sig_error}")
                        logger.warning(f"Will store backtest without signal relationship for '{signal_name}'")
            
            # Store backtest with signal relationships if we have any
            if signal_ids:
                logger.info(f"Storing backtest with {len(signal_ids)} signal relationships...")
                self.database_manager.store_backtest(backtest_config, signal_ids=signal_ids, signal_weights=signal_weights_dict)
            else:
                # No signals or couldn't resolve them, store without signal relationships
                logger.info("Storing backtest without signal relationships (signals parameter was None or empty)")
                self.database_manager.store_backtest(backtest_config)
            logger.info(f"Stored backtest configuration with run_id: {run_id}")
        except Exception as e:
            logger.error(f"Error storing backtest configuration: {e}")
            logger.exception("Full exception traceback:")
            raise  # Re-raise to be caught by outer exception handler
        
        # Initialize result
        result = BacktestResult(
            backtest_id=run_id,
            start_date=config.start_date,
            end_date=config.end_date,
            tickers=tickers,
            signals=signals,
            signal_weights=config.signal_weights or {signal: 1.0/len(signals) for signal in signals}
        )
        
        return run_id, result
    
    def _create_portfolios_for_dates(self, signal_scores: pd.DataFrame, 
                                   rebalancing_dates: List[date], tickers: List[str], 
                                   config: BacktestConfig, run_id: str, 
                                   result: BacktestResult) -> Optional[List]:
        """
        Create portfolios for all rebalancing dates.
        
        Args:
            signal_scores: DataFrame with signal scores for all dates
            rebalancing_dates: List of rebalancing dates
            tickers: List of stock ticker symbols
            config: Backtesting configuration
            run_id: Unique backtest run identifier
            result: BacktestResult object to update on error
            
        Returns:
            List of created portfolios or None if error occurred
        """
        portfolios_created = []
        for rebal_date in rebalancing_dates:
            try:
                # Get combined scores for this date
                date_scores = signal_scores[signal_scores.index == rebal_date]
                if date_scores.empty:
                    logger.warning(f"No signal scores available for {rebal_date}")
                    continue
                
                # Convert to the format expected by portfolio service
                combined_scores_df = pd.DataFrame({
                    'asof_date': rebal_date,
                    'ticker': date_scores.columns,
                    'score': date_scores.iloc[0].values
                })
                
                portfolio_result = self.portfolio_service.create_portfolio_from_scores(
                    combined_scores_df, tickers, rebal_date, config.universe_id, run_id=run_id,
                    max_weight=config.max_weight
                )
                portfolios_created.append(portfolio_result)
                logger.info(f"Created portfolio for {rebal_date}")
            except Exception as e:
                error_msg = f"Failed to create portfolio for {rebal_date}: {e}"
                logger.error(error_msg)
                result.error_message = error_msg
                return None
        
        return portfolios_created
    
    def _get_rebalancing_dates(self, config: BacktestConfig) -> List[date]:
        """
        Get rebalancing dates based on frequency between start and end dates.
        
        Args:
            config: Backtesting configuration
            
        Returns:
            List of rebalancing dates
        """
        return self.trading_calendar.get_rebalancing_dates(
            config.start_date, config.end_date, config.rebalancing_frequency
        )
    
    def _fetch_signal_scores(self, tickers: List[str], signals: List[str], 
                           rebalancing_dates: List[date], config: BacktestConfig) -> pd.DataFrame:
        """
        Fetch signal scores for all rebalancing dates.
        
        This method always uses raw signals and combines them fresh to ensure
        consistency with current backtest parameters. The combined_scores table
        is only used for visualization/debugging, not for portfolio creation.
        
        Args:
            tickers: List of stock ticker symbols
            signals: List of signal IDs
            rebalancing_dates: List of rebalancing dates
            config: Backtesting configuration
            
        Returns:
            DataFrame with signal scores
        """
        try:
            # Always use raw signals and combine them fresh to ensure consistency
            # with current backtest parameters (tickers, dates, combination method, etc.)
            logger.info("Using raw signals and combining them fresh for portfolio creation...")
            
            # Try to get raw signals from database first
            signals_df = self.signal_reader.get_signals_raw(
                tickers, signals, config.start_date, config.end_date
            )
            
            if not signals_df.empty:
                logger.info(f"Found existing raw signals in database: {len(signals_df)} records")
                # Combine existing signals into scores
                logger.info(f"Combining existing signals using method: {config.signal_combination_method}")
                combined_scores = self._combine_signals_to_scores(
                    signals_df, tickers, signals, config
                )
                
                if not combined_scores.empty:
                    # Convert to pivot format
                    signal_scores = combined_scores.pivot_table(
                        index='asof_date',
                        columns='ticker',
                        values='score',
                        aggfunc='first'
                    )
                    logger.info(f"Combined existing signals into scores: {signal_scores.shape}")
                    return signal_scores
            
            # If no signals exist in database, calculate them
            logger.info("No existing signals found in database, calculating new signals...")
            signals_df = self.signal_reader.calculate_and_enforce_signals(
                tickers, signals, config.start_date, config.end_date, store_in_db=True
            )
            
            if signals_df.empty:
                logger.warning("No signals calculated")
                return pd.DataFrame()
            
            # Combine signals into scores using configured method
            logger.info(f"Combining calculated signals using method: {config.signal_combination_method}")
            combined_scores = self._combine_signals_to_scores(
                signals_df, tickers, signals, config
            )
            
            if combined_scores.empty:
                logger.warning("No combined scores created")
                return pd.DataFrame()
            
            # Convert to pivot format
            signal_scores = combined_scores.pivot_table(
                index='asof_date',
                columns='ticker',
                values='score',
                aggfunc='first'
            )
            
            logger.info(f"Calculated and combined new signals into scores: {signal_scores.shape}")
            return signal_scores
            
        except Exception as e:
            logger.error(f"Error fetching signal scores: {e}")
            return pd.DataFrame()
    
    
    def _run_simulation_with_portfolios(self, portfolios_created: List[Dict[str, Any]], 
                                      tickers: List[str], config: BacktestConfig) -> Tuple[pd.Series, pd.Series, pd.DataFrame, date]:
        """
        Run simulation using pre-created portfolios.
        
        Args:
            portfolios_created: List of portfolio creation results
            tickers: List of stock ticker symbols
            config: Backtesting configuration
            
        Returns:
            Tuple of (portfolio_values, benchmark_values, weights_history, first_rebalance_date)
        """
        logger.info("Starting backtest simulation with pre-created portfolios...")
        
        # Get price data
        price_data = self._get_price_data(tickers, config)
        if price_data is None or price_data.empty:
            logger.error("Failed to get price data")
            return pd.Series(), pd.Series(), pd.DataFrame(), None
        
        # Initialize tracking variables
        portfolio_value = config.initial_capital
        benchmark_value = config.initial_capital
        
        portfolio_values = pd.Series(index=price_data.index, dtype=float)
        benchmark_values = pd.Series(index=price_data.index, dtype=float)
        weights_history = pd.DataFrame(index=[p['inference_date'] for p in portfolios_created], columns=tickers, dtype=float)
        
        # Store returns for plotting
        strategy_returns = pd.Series(index=price_data.index, dtype=float)
        benchmark_returns = pd.Series(index=price_data.index, dtype=float)
        
        # Get benchmark data
        if config.use_equal_weight_benchmark:
            benchmark_data = price_data
        else:
            benchmark_data = self.price_fetcher.get_price_history(
                config.benchmark_ticker, config.start_date, config.end_date
            )
            if benchmark_data is not None and not benchmark_data.empty:
                benchmark_data = benchmark_data.reindex(price_data.index, method='ffill')
            else:
                benchmark_data = pd.DataFrame()
        
        # Find first rebalance date
        first_rebalance_date = None
        for portfolio in portfolios_created:
            if portfolio['inference_date'] >= config.start_date:
                first_rebalance_date = portfolio['inference_date']
                break
        
        if first_rebalance_date is None:
            logger.error("No valid rebalancing dates found")
            return pd.Series(), pd.Series(), pd.DataFrame(), None
        
        logger.info(f"Strategy and benchmark will start on: {first_rebalance_date}")
        
        # Reset values at first rebalance date
        portfolio_value = config.initial_capital
        benchmark_value = config.initial_capital
        
        # Create portfolio weights lookup
        portfolio_weights = {}
        for portfolio in portfolios_created:
            portfolio_weights[portfolio['inference_date']] = portfolio['weights']
        
        # Run simulation
        for i, current_date in enumerate(price_data.index):
            if current_date < first_rebalance_date:
                continue
            
            # Get current portfolio weights
            current_weights = None
            for rebal_date in sorted(portfolio_weights.keys()):
                if rebal_date <= current_date:
                    current_weights = portfolio_weights[rebal_date]
                else:
                    break
            
            # Update portfolio value
            if current_weights is not None:
                # Convert weights dict to Series for compatibility
                weights_series = pd.Series(current_weights)
                portfolio_return = self._calculate_portfolio_return(
                    weights_series, price_data, current_date, i
                )
                if portfolio_return is not None:
                    portfolio_value *= (1 + portfolio_return)
                    strategy_returns.loc[current_date] = portfolio_return
            
            # Update benchmark value
            if not benchmark_data.empty and current_date in benchmark_data.index:
                if config.use_equal_weight_benchmark:
                    benchmark_return = self._calculate_equal_weight_return(
                        tickers, benchmark_data, current_date, i
                    )
                else:
                    benchmark_return = self._calculate_benchmark_return(
                        benchmark_data, current_date, i
                    )
                
                if benchmark_return is not None:
                    benchmark_value *= (1 + benchmark_return)
                    benchmark_returns.loc[current_date] = benchmark_return
            
            # Store values
            portfolio_values.loc[current_date] = portfolio_value
            benchmark_values.loc[current_date] = benchmark_value
        
        # Store weights history
        for portfolio in portfolios_created:
            weights_history.loc[portfolio['inference_date']] = portfolio['weights']
        
        # Store returns data for plotting
        self.strategy_returns = strategy_returns.dropna()
        self.benchmark_returns = benchmark_returns.dropna()
        self._use_equal_weight_benchmark = config.use_equal_weight_benchmark
        
        # Store portfolio history for plotting
        for portfolio in portfolios_created:
            self.portfolio_history.append({
                'date': portfolio['inference_date'],
                'positions': portfolio['weights']
            })
        
        logger.info("Backtest simulation completed")
        
        # Filter to only include data from first rebalance date onwards
        portfolio_values = portfolio_values[portfolio_values.index >= first_rebalance_date].dropna()
        benchmark_values = benchmark_values[benchmark_values.index >= first_rebalance_date].dropna()
        
        return portfolio_values, benchmark_values, weights_history, first_rebalance_date
    
    def _store_backtest_results(self, result: BacktestResult, portfolio_values: pd.Series,
                              benchmark_values: pd.Series, weights_history: pd.DataFrame,
                              first_rebalance_date: date):
        """Store backtest results in database."""
        # Note: NAV data and portfolio data are stored in _finalize_backtest_results
        # via _store_portfolio_data to avoid duplication
        logger.info(f"Backtest results prepared for {result.backtest_id}")
    
    def _prepare_backtest_data(self, tickers: List[str], signals: List[str], 
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
        rebalancing_dates = self._ensure_signal_scores_for_rebalancing_dates(
            rebalancing_dates, tickers, signals, config
        )
        logger.info(f"Adjusted to {len(rebalancing_dates)} rebalancing dates with signal scores")
        
        # Get price data for all tickers
        price_data = self._get_price_data(tickers, config)
        if price_data is None or price_data.empty:
            logger.error("Failed to get price data")
            return trading_days, rebalancing_dates, None, pd.DataFrame()
        
        # Get signal scores (combined scores)
        signal_scores = self._get_signal_scores(tickers, signals, config)
        if signal_scores.empty:
            logger.error("Failed to get signal scores")
            return trading_days, rebalancing_dates, price_data, pd.DataFrame()
        
        return trading_days, rebalancing_dates, price_data, signal_scores
    
    def _finalize_backtest_results(self, result: BacktestResult, portfolio_values: pd.Series,
                                 benchmark_values: pd.Series, weights_history: pd.DataFrame,
                                 first_rebalance_date: date, rebalancing_dates: List[date],
                                 start_time: float, config: BacktestConfig) -> None:
        """Finalize backtest results with metrics and database storage."""
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
            self._store_portfolio_data(result, portfolio_values, benchmark_values, weights_history, first_rebalance_date, config)
            logger.info("Stored portfolio data in database")
        except Exception as e:
            logger.error(f"Error storing portfolio data: {e}")
        
        # Calculate execution time
        result.execution_time_seconds = time.time() - start_time
        
        logger.info(f"Backtest completed in {result.execution_time_seconds:.1f} seconds")
        logger.info(f"Total return: {result.total_return:.2%}, Sharpe ratio: {result.sharpe_ratio:.2f}")
    
    
    def _ensure_signal_scores_for_rebalancing_dates(self, rebalancing_dates: List[date], 
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
                rebalancing_dates = self._ensure_signal_scores_for_rebalancing_dates(
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
            # Skip NaN values when calculating max
            valid_weights = weights.dropna()
            if not valid_weights.empty:
                max_weights.append(valid_weights.max())
        
        return np.max(max_weights) if max_weights else 0.0
    
    def _store_portfolio_data(self, result: BacktestResult, portfolio_values: pd.Series, 
                            benchmark_values: pd.Series, weights_history: pd.DataFrame, first_rebalance_date: date, config: BacktestConfig):
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
                try:
                    stored_count = self.database_manager.store_backtest_nav(nav_objects)
                    logger.info(f"Stored {stored_count} NAV records for backtest {result.backtest_id}")
                except Exception as e:
                    logger.error(f"Failed to store NAV data for backtest {result.backtest_id}: {e}")
                    raise
            else:
                logger.warning(f"No NAV data to store for backtest {result.backtest_id}")
            
            # Store portfolios and positions
            for date, weights_row in weights_history.iterrows():
                if weights_row.isna().all():
                    continue
                
                # Calculate portfolio value based on current NAV
                current_nav = portfolio_values.get(date, config.initial_capital)
                
                # Create portfolio
                portfolio = Portfolio(
                    run_id=result.backtest_id,
                    universe_id=config.universe_id,
                    asof_date=date,
                    method='optimization',
                    params={'risk_aversion': result.signal_weights},
                    cash=0.0,  # Always 0 since weights are normalized to sum to 1.0
                    total_value=current_nav,  # Total portfolio value available for investment
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
            combined_scores = []
            
            for ticker in tickers:
                ticker_signals = raw_signals[raw_signals['ticker'] == ticker]
                
                for asof_date in ticker_signals['asof_date'].unique():
                    date_signals = ticker_signals[ticker_signals['asof_date'] == asof_date]
                    
                    if date_signals.empty:
                        continue
                    
                    # Apply combination method
                    if config.signal_combination_method == 'equal_weight':
                        # Only calculate mean if we have all required signals
                        available_signals = set(date_signals['signal_name'].unique())
                        required_signals = set(signals)
                        
                        if available_signals == required_signals:
                            combined_score = date_signals['value'].mean()
                        else:
                            logger.warning(f"Missing signals for {ticker} on {asof_date}. "
                                         f"Available: {available_signals}, Required: {required_signals}")
                            continue
                            
                    elif config.signal_combination_method == 'weighted':
                        weights = config.signal_weights or {}
                        total_weight = 0
                        weighted_sum = 0
                        for _, row in date_signals.iterrows():
                            weight = weights.get(row['signal_name'], 1.0)
                            weighted_sum += row['value'] * weight
                            total_weight += weight
                        combined_score = weighted_sum / total_weight if total_weight > 0 else 0
                        
                    elif config.signal_combination_method == 'zscore':
                        # Z-score normalization
                        values = date_signals['value'].values
                        if len(values) > 1:
                            mean_val = np.mean(values)
                            std_val = np.std(values)
                            combined_score = (values - mean_val) / std_val if std_val > 0 else 0
                        else:
                            combined_score = values[0] if len(values) == 1 else 0
                    else:
                        logger.warning(f"Unknown combination method: {config.signal_combination_method}")
                        continue
                    
                    if not np.isnan(combined_score):
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
                    from src.database import ScoreCombined
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
                    
                    self.database_manager.store_scores_combined(score_objects)
                    logger.info(f"Stored {len(score_objects)} combined scores in database")
                except Exception as e:
                    logger.error(f"Error storing combined scores in database: {e}")
                
                return df
            else:
                logger.warning("No combined scores calculated")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return pd.DataFrame()

