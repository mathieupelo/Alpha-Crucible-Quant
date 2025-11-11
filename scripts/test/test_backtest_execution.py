"""
Test script to verify backtest execution and data storage.
"""
import os
import sys
import logging
from datetime import date, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_backtest_execution():
    """Test running a backtest and verify data is stored."""
    try:
        from src.database.manager import DatabaseManager
        from src.backtest.engine import BacktestEngine
        from src.backtest.config import BacktestConfig
        
        # Initialize database
        db = DatabaseManager()
        if not db.connect():
            logger.error("Failed to connect to database")
            return False
        
        logger.info("✅ Database connected")
        
        # Get a universe with companies
        logger.info("Fetching universes...")
        universes_df = db.execute_query("SELECT id, name FROM universes ORDER BY id LIMIT 5")
        if universes_df.empty:
            logger.error("No universes found")
            return False
        
        logger.info(f"Found {len(universes_df)} universes")
        universe_id = int(universes_df.iloc[0]['id'])
        universe_name = universes_df.iloc[0]['name']
        logger.info(f"Using universe: {universe_name} (ID: {universe_id})")
        
        # Get companies from universe
        companies_df = db.get_universe_companies(universe_id)
        if companies_df.empty or len(companies_df) < 5:
            logger.error(f"Universe has only {len(companies_df) if not companies_df.empty else 0} companies, need at least 5")
            return False
        
        # Extract main tickers from DataFrame
        main_tickers = companies_df['main_ticker'].dropna().tolist()
        logger.info(f"Found {len(main_tickers)} main tickers: {main_tickers[:5]}...")
        
        # Get available signals
        signals_df = db.execute_query("SELECT id, name FROM signals ORDER BY id LIMIT 5")
        if signals_df.empty:
            logger.error("No signals found")
            return False
        
        signal_names = [s.upper() for s in signals_df['name'].tolist()]
        logger.info(f"Using signals: {signal_names}")
        
        # Create backtest config
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            universe_id=universe_id,
            name=f"Test Backtest - {date.today()}",
            initial_capital=100000,
            rebalancing_frequency='weekly',
            signal_combination_method='equal_weight'
        )
        
        logger.info(f"Running backtest from {start_date} to {end_date}...")
        
        # Run backtest
        engine = BacktestEngine()
        result = engine.run_backtest(
            tickers=main_tickers[:10],  # Limit to 10 tickers for testing
            signals=signal_names,
            config=config
        )
        
        logger.info(f"✅ Backtest completed: {result.backtest_id}")
        logger.info(f"   Total return: {result.total_return:.2%}")
        logger.info(f"   Sharpe ratio: {result.sharpe_ratio:.2f}")
        logger.info(f"   Portfolio values: {len(result.portfolio_values)}")
        
        # Verify NAV data is stored
        nav_df = db.get_backtest_nav(result.backtest_id)
        logger.info(f"✅ NAV records in database: {len(nav_df)}")
        
        if len(nav_df) > 0:
            logger.info(f"   First NAV: {nav_df.iloc[0]['nav']:.2f} on {nav_df.iloc[0]['date']}")
            logger.info(f"   Last NAV: {nav_df.iloc[-1]['nav']:.2f} on {nav_df.iloc[-1]['date']}")
        
        # Verify portfolios are stored
        portfolios_df = db.execute_query(
            "SELECT COUNT(*) as count FROM portfolios WHERE run_id = %s",
            (result.backtest_id,)
        )
        portfolio_count = int(portfolios_df.iloc[0]['count'])
        logger.info(f"✅ Portfolios in database: {portfolio_count}")
        
        # Verify positions are stored
        if portfolio_count > 0:
            positions_df = db.execute_query(
                """
                SELECT COUNT(*) as count 
                FROM portfolio_positions pp
                JOIN portfolios p ON pp.portfolio_id = p.id
                WHERE p.run_id = %s
                """,
                (result.backtest_id,)
            )
            position_count = int(positions_df.iloc[0]['count'])
            logger.info(f"✅ Positions in database: {position_count}")
        
        logger.info("✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_backtest_execution()
    sys.exit(0 if success else 1)

