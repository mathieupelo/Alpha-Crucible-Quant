"""
Test the full backtest flow to identify why NAV data isn't being stored.
"""
import os
import sys
import logging
from datetime import date, timedelta
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_backtest_full_flow():
    """Test the complete backtest flow."""
    try:
        from src.database.manager import DatabaseManager
        from src.backtest.engine import BacktestEngine
        from src.backtest.config import BacktestConfig
        
        db = DatabaseManager()
        if not db.connect():
            logger.error("Failed to connect to database")
            return False
        
        logger.info("✅ Database connected")
        
        # Get a universe
        universes_df = db.execute_query("SELECT id, name FROM universes ORDER BY id LIMIT 1")
        if universes_df.empty:
            logger.error("No universes found")
            return False
        
        universe_id = int(universes_df.iloc[0]['id'])
        universe_name = universes_df.iloc[0]['name']
        logger.info(f"Using universe: {universe_name} (ID: {universe_id})")
        
        # Get companies
        companies_df = db.get_universe_companies(universe_id)
        if companies_df.empty or len(companies_df) < 5:
            logger.error(f"Universe has only {len(companies_df)} companies")
            return False
        
        main_tickers = companies_df['main_ticker'].dropna().tolist()[:10]
        logger.info(f"Using {len(main_tickers)} tickers: {main_tickers[:5]}...")
        
        # Get signals
        signals_df = db.execute_query("SELECT id, name FROM signals ORDER BY id LIMIT 3")
        if signals_df.empty:
            logger.error("No signals found")
            return False
        
        signal_names = [s.upper() for s in signals_df['name'].tolist()]
        logger.info(f"Using signals: {signal_names}")
        
        # Check if signals exist for these tickers
        logger.info("Checking for existing signals...")
        ticker_placeholders = ','.join(['%s'] * len(main_tickers))
        signal_placeholders = ','.join(['%s'] * len(signal_names))
        
        signals_check_query = f"""
        SELECT COUNT(*) as count, MIN(asof_date) as min_date, MAX(asof_date) as max_date
        FROM signal_raw sr
        WHERE sr.ticker IN ({ticker_placeholders})
        AND sr.signal_id IN (SELECT id FROM signals WHERE name IN ({signal_placeholders}))
        """
        params = main_tickers + signal_names
        signals_check = db.execute_query(signals_check_query, tuple(params))
        
        if not signals_check.empty:
            count = int(signals_check.iloc[0]['count'])
            logger.info(f"Found {count} existing signal records")
            if count == 0:
                logger.warning("⚠️ No signals found in database - backtest will have no data")
        
        # Create config
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        
        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            universe_id=universe_id,
            name=f"Full Flow Test - {date.today()}",
            initial_capital=100000,
            rebalancing_frequency='weekly',
            signal_combination_method='equal_weight'
        )
        
        logger.info(f"Running backtest from {start_date} to {end_date}...")
        
        # Run backtest
        engine = BacktestEngine()
        result = engine.run_backtest(
            tickers=main_tickers,
            signals=signal_names,
            config=config
        )
        
        logger.info(f"✅ Backtest completed: {result.backtest_id}")
        logger.info(f"   Portfolio values length: {len(result.portfolio_values)}")
        logger.info(f"   Benchmark values length: {len(result.benchmark_values)}")
        logger.info(f"   Total return: {result.total_return:.2%}")
        
        # Check NAV in database
        nav_df = db.get_backtest_nav(result.backtest_id)
        logger.info(f"✅ NAV records in database: {len(nav_df)}")
        
        if len(nav_df) > 0:
            logger.info(f"   First NAV: {nav_df.iloc[0]['nav']:.2f} on {nav_df.iloc[0]['date']}")
            logger.info(f"   Last NAV: {nav_df.iloc[-1]['nav']:.2f} on {nav_df.iloc[-1]['date']}")
            
            # Verify return_pct is stored
            if 'return_pct' in nav_df.columns:
                first_return_pct = nav_df.iloc[0].get('return_pct')
                last_return_pct = nav_df.iloc[-1].get('return_pct')
                logger.info(f"   First return_pct: {first_return_pct:.4f}")
                logger.info(f"   Last return_pct: {last_return_pct:.4f}")
                
                # Verify first return_pct is ~0 (baseline)
                if first_return_pct is not None:
                    assert abs(first_return_pct) < 0.001, f"First return_pct should be ~0, got {first_return_pct}"
                    logger.info("   ✅ return_pct baseline verified")
            else:
                logger.warning("   ⚠️ return_pct column not found - migration may be needed")
        else:
            logger.error("❌ No NAV data stored!")
            logger.error(f"   Portfolio values empty: {result.portfolio_values.empty}")
            logger.error(f"   Benchmark values empty: {result.benchmark_values.empty}")
        
        # Check portfolios
        portfolios_df = db.execute_query(
            "SELECT COUNT(*) as count FROM portfolios WHERE run_id = %s",
            (result.backtest_id,)
        )
        portfolio_count = int(portfolios_df.iloc[0]['count'])
        logger.info(f"✅ Portfolios in database: {portfolio_count}")
        
        return len(nav_df) > 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_backtest_full_flow()
    sys.exit(0 if success else 1)

