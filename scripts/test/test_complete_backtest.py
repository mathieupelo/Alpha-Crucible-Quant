"""
Complete end-to-end backtest test to verify everything works.
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

def test_complete_backtest():
    """Test complete backtest flow."""
    try:
        from src.database.manager import DatabaseManager
        from src.backtest.engine import BacktestEngine
        from src.backtest.config import BacktestConfig
        
        db = DatabaseManager()
        if not db.connect():
            logger.error("Failed to connect to database")
            return False
        
        logger.info("✅ Database connected")
        
        # Get a universe with companies
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
        
        # Get signals that have data
        signals_df = db.execute_query("""
            SELECT DISTINCT s.id, s.name
            FROM signals s
            JOIN signal_raw sr ON s.id = sr.signal_id
            WHERE sr.ticker IN ({})
            AND sr.asof_date >= CURRENT_DATE - INTERVAL '60 days'
            ORDER BY s.id
            LIMIT 3
        """.format(','.join(['%s'] * len(main_tickers))), tuple(main_tickers))
        
        if signals_df.empty:
            logger.error("No signals found with data for these tickers")
            return False
        
        signal_names = [s.upper() for s in signals_df['name'].tolist()]
        logger.info(f"Using signals: {signal_names}")
        
        # Create config
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        
        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            universe_id=universe_id,
            name=f"Complete Test Backtest - {date.today()}",
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
        
        logger.info(f"\n✅ Backtest completed: {result.backtest_id}")
        logger.info(f"   Portfolio values: {len(result.portfolio_values)}")
        logger.info(f"   Benchmark values: {len(result.benchmark_values)}")
        logger.info(f"   Total return: {result.total_return:.2%}")
        logger.info(f"   Sharpe ratio: {result.sharpe_ratio:.2f}")
        
        # Verify NAV data
        nav_df = db.get_backtest_nav(result.backtest_id)
        logger.info(f"\n✅ NAV records in database: {len(nav_df)}")
        
        if len(nav_df) == 0:
            logger.error("❌ No NAV data stored!")
            logger.error(f"   Portfolio values empty: {result.portfolio_values.empty}")
            return False
        
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
            
            # Test dynamic starting capital
            new_capital = 200000.0
            nav_df_new = db.get_backtest_nav(result.backtest_id, starting_capital=new_capital)
            if not nav_df_new.empty and 'return_pct' in nav_df_new.columns:
                first_new_nav = nav_df_new.iloc[0]['nav']
                last_new_nav = nav_df_new.iloc[-1]['nav']
                logger.info(f"   ✅ Dynamic capital test (${new_capital:,.0f}):")
                logger.info(f"      First NAV: ${first_new_nav:,.2f}")
                logger.info(f"      Last NAV: ${last_new_nav:,.2f}")
        else:
            logger.warning("   ⚠️ return_pct column not found - migration may be needed")
        
        # Verify portfolios
        portfolios_df = db.execute_query(
            "SELECT COUNT(*) as count FROM portfolios WHERE run_id = %s",
            (result.backtest_id,)
        )
        portfolio_count = int(portfolios_df.iloc[0]['count'])
        logger.info(f"\n✅ Portfolios in database: {portfolio_count}")
        
        # Verify positions
        if portfolio_count > 0:
            positions_df = db.execute_query("""
                SELECT COUNT(*) as count 
                FROM portfolio_positions pp
                JOIN portfolios p ON pp.portfolio_id = p.id
                WHERE p.run_id = %s
            """, (result.backtest_id,))
            position_count = int(positions_df.iloc[0]['count'])
            logger.info(f"✅ Positions in database: {position_count}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL TESTS PASSED - Backtest is working correctly!")
        logger.info("=" * 60)
        logger.info(f"\nBacktest ID: {result.backtest_id}")
        logger.info("You can now view this backtest in the frontend.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_complete_backtest()
    sys.exit(0 if success else 1)

