"""
Utility functions for running backtests from Airflow DAGs.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict

# Add paths for imports
# Note: These paths assume backend/ and src/ are mounted in docker-compose.airflow.yml
backend_path = '/opt/airflow/backend'
src_path = '/opt/airflow/src'

# Add to path if they exist
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
if os.path.exists(src_path):
    sys.path.insert(0, src_path)

# Also try relative paths (for local development/testing)
current_dir = Path(__file__).parent.parent.parent
backend_local = current_dir / 'backend'
src_local = current_dir / 'src'

if backend_local.exists() and str(backend_local) not in sys.path:
    sys.path.insert(0, str(backend_local))
if src_local.exists() and str(src_local) not in sys.path:
    sys.path.insert(0, str(src_local))

logger = logging.getLogger(__name__)


def run_backtest_task(
    universe_id: int,
    signals: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    lookback_days: int = 252,  # Default to 1 year lookback
    name: Optional[str] = None,
    initial_capital: float = 10000.0,
    rebalancing_frequency: str = 'monthly',
    **kwargs
) -> Dict:
    """
    Run a backtest for a universe.
    
    Args:
        universe_id: ID of the universe to backtest
        signals: List of signal names to use
        start_date: Start date in YYYY-MM-DD format (optional, defaults to lookback_days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to yesterday)
        lookback_days: Number of days to look back if start_date not provided
        name: Name for the backtest (optional)
        initial_capital: Initial capital for backtest
        rebalancing_frequency: Rebalancing frequency ('daily', 'weekly', 'monthly', 'quarterly')
        **kwargs: Additional backtest configuration parameters
        
    Returns:
        Dict with backtest results
    """
    try:
        # Import here to avoid issues if paths aren't set up
        from services.database_service import DatabaseService
        from src.backtest.engine import BacktestEngine
        from src.backtest.config import BacktestConfig
        
        logger.info(f"Starting backtest for universe {universe_id}")
        
        # Initialize database service
        db_service = DatabaseService()
        
        if not db_service.ensure_connection():
            raise RuntimeError("Failed to connect to database")
        
        # Validate universe exists
        universe = db_service.get_universe_by_id(universe_id)
        if universe is None:
            raise ValueError(f"Universe with ID {universe_id} not found")
        
        logger.info(f"Found universe: {universe['name']}")
        
        # Get universe tickers
        tickers_data = db_service.get_universe_tickers(universe_id)
        if not tickers_data:
            raise ValueError(f"Universe '{universe['name']}' has no tickers")
        
        tickers = [t['ticker'] for t in tickers_data]
        
        if len(tickers) < 5:
            raise ValueError(f"Universe must have at least 5 tickers. Current count: {len(tickers)}")
        
        logger.info(f"Universe has {len(tickers)} tickers: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
        
        # Determine date range
        if end_date is None:
            end_date_obj = date.today() - timedelta(days=1)  # Yesterday
        else:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date is None:
            start_date_obj = end_date_obj - timedelta(days=lookback_days)
        else:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        logger.info(f"Backtest date range: {start_date_obj} to {end_date_obj}")
        
        # Generate backtest name if not provided
        if name is None:
            name = f"Weekly Backtest - {universe['name']} - {end_date_obj.strftime('%Y-%m-%d')}"
        
        # Create backtest configuration
        config = BacktestConfig(
            start_date=start_date_obj,
            end_date=end_date_obj,
            universe_id=universe_id,
            name=name,
            initial_capital=initial_capital,
            rebalancing_frequency=rebalancing_frequency,
            evaluation_period=rebalancing_frequency,
            transaction_costs=kwargs.get('transaction_costs', 0.001),
            max_weight=kwargs.get('max_weight', 0.1),
            min_weight=kwargs.get('min_weight', 0.0),
            risk_aversion=kwargs.get('risk_aversion', 0.5),
            benchmark_ticker=kwargs.get('benchmark_ticker', 'SPY'),
            use_equal_weight_benchmark=kwargs.get('use_equal_weight_benchmark', True),
            min_lookback_days=kwargs.get('min_lookback_days', 252),
            max_lookback_days=kwargs.get('max_lookback_days', 756),
            signal_weights=kwargs.get('signal_weights'),
            signal_combination_method=kwargs.get('signal_combination_method', 'weighted'),
            forward_fill_signals=kwargs.get('forward_fill_signals', True)
        )
        
        # Convert signal names to uppercase
        signals_upper = [s.upper() for s in signals]
        
        logger.info(f"Running backtest with signals: {', '.join(signals_upper)}")
        
        # Run backtest
        engine = BacktestEngine()
        result = engine.run_backtest(
            tickers=tickers,
            signals=signals_upper,
            config=config
        )
        
        # Log results
        logger.info("=" * 60)
        logger.info("BACKTEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Backtest ID: {result.backtest_id}")
        logger.info(f"Total Return: {result.total_return:.2%}")
        logger.info(f"Annualized Return: {result.annualized_return:.2%}")
        logger.info(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        logger.info(f"Max Drawdown: {result.max_drawdown:.2%}")
        logger.info(f"Volatility: {result.volatility:.2%}")
        logger.info(f"Alpha: {result.alpha:.2%}")
        logger.info(f"Information Ratio: {result.information_ratio:.2f}")
        
        return {
            'success': True,
            'backtest_id': result.backtest_id,
            'universe_id': universe_id,
            'universe_name': universe['name'],
            'total_return': result.total_return,
            'annualized_return': result.annualized_return,
            'sharpe_ratio': result.sharpe_ratio,
            'max_drawdown': result.max_drawdown,
            'volatility': result.volatility,
            'alpha': result.alpha,
            'information_ratio': result.information_ratio,
        }
        
    except Exception as e:
        logger.error(f"Error running backtest: {e}", exc_info=True)
        raise

