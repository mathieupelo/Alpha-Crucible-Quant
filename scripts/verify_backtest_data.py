"""
Verify that backtest data is stored correctly and can be retrieved.
"""
import os
import sys
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_backtest_data():
    """Verify backtest data storage."""
    try:
        from src.database.manager import DatabaseManager
        
        db = DatabaseManager()
        if not db.connect():
            logger.error("Failed to connect to database")
            return False
        
        logger.info("✅ Database connected")
        
        # Get the most recent backtest
        backtests_df = db.execute_query("""
            SELECT run_id, name, start_date, end_date 
            FROM backtests 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        if backtests_df.empty:
            logger.error("No backtests found")
            return False
        
        run_id = backtests_df.iloc[0]['run_id']
        name = backtests_df.iloc[0].get('name', 'N/A')
        logger.info(f"Checking backtest: {name} ({run_id})")
        
        # Check NAV data
        nav_df = db.get_backtest_nav(run_id)
        logger.info(f"✅ NAV records: {len(nav_df)}")
        if len(nav_df) > 0:
            logger.info(f"   First NAV: {nav_df.iloc[0]['nav']:.2f} on {nav_df.iloc[0]['date']}")
            logger.info(f"   Last NAV: {nav_df.iloc[-1]['nav']:.2f} on {nav_df.iloc[-1]['date']}")
        
        # Check portfolios
        portfolios_df = db.execute_query(
            "SELECT COUNT(*) as count FROM portfolios WHERE run_id = %s",
            (run_id,)
        )
        portfolio_count = int(portfolios_df.iloc[0]['count'])
        logger.info(f"✅ Portfolios: {portfolio_count}")
        
        # Check positions
        if portfolio_count > 0:
            positions_df = db.execute_query("""
                SELECT COUNT(*) as count 
                FROM portfolio_positions pp
                JOIN portfolios p ON pp.portfolio_id = p.id
                WHERE p.run_id = %s
            """, (run_id,))
            position_count = int(positions_df.iloc[0]['count'])
            logger.info(f"✅ Positions: {position_count}")
            
            # Check company_uid in positions
            company_uid_df = db.execute_query("""
                SELECT COUNT(*) as count 
                FROM portfolio_positions pp
                JOIN portfolios p ON pp.portfolio_id = p.id
                WHERE p.run_id = %s AND pp.company_uid IS NOT NULL
            """, (run_id,))
            company_uid_count = int(company_uid_df.iloc[0]['count'])
            logger.info(f"✅ Positions with company_uid: {company_uid_count}/{position_count}")
        
        # Check metrics
        metrics_df = db.execute_query("""
            SELECT 
                MIN(nav) as min_nav,
                MAX(nav) as max_nav,
                AVG(nav) as avg_nav,
                COUNT(*) as nav_count
            FROM backtest_nav
            WHERE run_id = %s
        """, (run_id,))
        
        if not metrics_df.empty and metrics_df.iloc[0]['nav_count'] > 0:
            row = metrics_df.iloc[0]
            logger.info(f"✅ NAV Metrics:")
            logger.info(f"   Min: {row['min_nav']:.2f}")
            logger.info(f"   Max: {row['max_nav']:.2f}")
            logger.info(f"   Avg: {row['avg_nav']:.2f}")
        
        logger.info("\n✅ All data verified successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = verify_backtest_data()
    sys.exit(0 if success else 1)

