#!/usr/bin/env python3
"""
Script to query portfolio data from the database.

This script demonstrates how to retrieve and analyze portfolio values and weights
stored in the database.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager


def main():
    """Query and display portfolio data."""
    print("Quant Project - Portfolio Data Query")
    print("=" * 50)
    
    try:
        # Initialize database manager
        print("Connecting to database...")
        db_manager = DatabaseManager()
        
        if not db_manager.connect():
            print("Failed to connect to database")
            return 1
        
        # Get recent backtests
        print("\nRecent Backtests:")
        print("-" * 30)
        backtests = db_manager.get_backtests()
        
        if backtests.empty:
            print("No backtests found in database")
            return 0
        
        # Show recent backtests
        recent_backtests = backtests.head(5)
        for _, backtest in recent_backtests.iterrows():
            print(f"Run ID: {backtest['run_id']}")
            print(f"  Period: {backtest['start_date']} to {backtest['end_date']}")
            print(f"  Frequency: {backtest['frequency']}")
            print(f"  Benchmark: {backtest['benchmark']}")
            print(f"  Created: {backtest['created_at']}")
            print()
        
        # Get the most recent backtest ID
        latest_run_id = recent_backtests.iloc[0]['run_id']
        print(f"Analyzing portfolio data for backtest: {latest_run_id}")
        
        # Get backtest NAV data
        print("\nBacktest NAV Data:")
        print("-" * 20)
        nav_data = db_manager.get_backtest_nav(run_id=latest_run_id)
        
        if not nav_data.empty:
            print(f"Found {len(nav_data)} NAV records")
            
            # Show first and last values
            first_nav = nav_data.iloc[0]
            last_nav = nav_data.iloc[-1]
            
            print(f"\nFirst Record ({first_nav['date']}):")
            print(f"  NAV: ${first_nav['nav']:,.2f}")
            if first_nav['benchmark_nav']:
                print(f"  Benchmark NAV: ${first_nav['benchmark_nav']:,.2f}")
            if first_nav['pnl']:
                print(f"  PnL: ${first_nav['pnl']:,.2f}")
            
            print(f"\nLast Record ({last_nav['date']}):")
            print(f"  NAV: ${last_nav['nav']:,.2f}")
            if last_nav['benchmark_nav']:
                print(f"  Benchmark NAV: ${last_nav['benchmark_nav']:,.2f}")
            if last_nav['pnl']:
                print(f"  PnL: ${last_nav['pnl']:,.2f}")
            
            # Calculate total performance
            total_return = (last_nav['nav'] / first_nav['nav']) - 1
            print(f"\nTotal Return: {total_return:.2%}")
            
            if first_nav['benchmark_nav'] and last_nav['benchmark_nav']:
                total_benchmark_return = (last_nav['benchmark_nav'] / first_nav['benchmark_nav']) - 1
                print(f"Total Benchmark Return: {total_benchmark_return:.2%}")
                print(f"Outperformance: {total_return - total_benchmark_return:.2%}")
        else:
            print("No NAV data found")
        
        # Get portfolios
        print("\nPortfolios:")
        print("-" * 20)
        portfolios = db_manager.get_portfolios(run_id=latest_run_id)
        
        if not portfolios.empty:
            print(f"Found {len(portfolios)} portfolio records")
            
            # Show recent portfolios
            recent_portfolios = portfolios.tail(3)
            for _, portfolio in recent_portfolios.iterrows():
                print(f"\nPortfolio ({portfolio['asof_date']}):")
                print(f"  Method: {portfolio['method']}")
                print(f"  Cash: ${portfolio['cash']:,.2f}")
                if portfolio['notes']:
                    print(f"  Notes: {portfolio['notes']}")
        else:
            print("No portfolios found")
        
        # Get portfolio positions for the most recent portfolio
        if not portfolios.empty:
            latest_portfolio = portfolios.iloc[-1]
            portfolio_id = latest_portfolio.name  # Assuming the index is the portfolio ID
            
            print(f"\nPortfolio Positions (Portfolio ID: {portfolio_id}):")
            print("-" * 40)
            positions = db_manager.get_portfolio_positions(portfolio_id=portfolio_id)
            
            if not positions.empty:
                print(f"Found {len(positions)} position records")
                
                # Show positions
                print(f"\nPositions:")
                for _, position in positions.iterrows():
                    if position['weight'] > 0:
                        print(f"  {position['ticker']}: {position['weight']:.2%} (Price: ${position['price_used']:.2f})")
            else:
                print("No positions found")
        
        # Get signals raw data
        print("\nRaw Signals:")
        print("-" * 20)
        raw_signals = db_manager.get_signals_raw()
        
        if not raw_signals.empty:
            print(f"Found {len(raw_signals)} raw signal records")
            
            # Show unique signal names
            unique_signals = raw_signals['signal_name'].unique()
            print(f"Signal types: {', '.join(sorted(unique_signals))}")
            
            # Show recent signals
            recent_signals = raw_signals.tail(5)
            print(f"\nRecent signals:")
            for _, signal in recent_signals.iterrows():
                print(f"  {signal['asof_date']}: {signal['ticker']} - {signal['signal_name']} = {signal['value']:.3f}")
        else:
            print("No raw signals found")
        
        # Get combined scores
        print("\nCombined Scores:")
        print("-" * 20)
        combined_scores = db_manager.get_scores_combined()
        
        if not combined_scores.empty:
            print(f"Found {len(combined_scores)} combined score records")
            
            # Show unique methods
            unique_methods = combined_scores['method'].unique()
            print(f"Combination methods: {', '.join(sorted(unique_methods))}")
            
            # Show recent scores
            recent_scores = combined_scores.tail(5)
            print(f"\nRecent scores:")
            for _, score in recent_scores.iterrows():
                print(f"  {score['asof_date']}: {score['ticker']} - {score['method']} = {score['score']:.3f}")
        else:
            print("No combined scores found")
        
        db_manager.disconnect()
        print("\nPortfolio data query completed successfully!")
        
    except Exception as e:
        print(f"Error querying portfolio data: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
