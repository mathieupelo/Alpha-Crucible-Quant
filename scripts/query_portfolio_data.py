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
        
        # Get recent backtest results
        print("\nRecent Backtest Results:")
        print("-" * 30)
        backtest_results = db_manager.get_backtest_results()
        
        if backtest_results.empty:
            print("No backtest results found in database")
            return 0
        
        # Show recent backtests
        recent_backtests = backtest_results.head(5)
        for _, result in recent_backtests.iterrows():
            print(f"Backtest ID: {result['backtest_id']}")
            print(f"  Period: {result['start_date']} to {result['end_date']}")
            print(f"  Total Return: {result['total_return']:.2%}")
            print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
            print(f"  Created: {result['created_at']}")
            print()
        
        # Get the most recent backtest ID
        latest_backtest_id = recent_backtests.iloc[0]['backtest_id']
        print(f"Analyzing portfolio data for backtest: {latest_backtest_id}")
        
        # Get portfolio values
        print("\nPortfolio Values:")
        print("-" * 20)
        portfolio_values = db_manager.get_portfolio_values(backtest_id=latest_backtest_id)
        
        if not portfolio_values.empty:
            print(f"Found {len(portfolio_values)} portfolio value records")
            
            # Show first and last values
            first_value = portfolio_values.iloc[0]
            last_value = portfolio_values.iloc[-1]
            
            print(f"\nFirst Record ({first_value['date']}):")
            print(f"  Portfolio Value: ${first_value['portfolio_value']:,.2f}")
            print(f"  Benchmark Value: ${first_value['benchmark_value']:,.2f}")
            print(f"  Portfolio Return: {first_value['portfolio_return']:.2%}")
            print(f"  Benchmark Return: {first_value['benchmark_return']:.2%}")
            
            print(f"\nLast Record ({last_value['date']}):")
            print(f"  Portfolio Value: ${last_value['portfolio_value']:,.2f}")
            print(f"  Benchmark Value: ${last_value['benchmark_value']:,.2f}")
            print(f"  Portfolio Return: {last_value['portfolio_return']:.2%}")
            print(f"  Benchmark Return: {last_value['benchmark_return']:.2%}")
            
            # Calculate total performance
            total_portfolio_return = (last_value['portfolio_value'] / first_value['portfolio_value']) - 1
            total_benchmark_return = (last_value['benchmark_value'] / first_value['benchmark_value']) - 1
            
            print(f"\nTotal Performance:")
            print(f"  Portfolio: {total_portfolio_return:.2%}")
            print(f"  Benchmark: {total_benchmark_return:.2%}")
            print(f"  Outperformance: {total_portfolio_return - total_benchmark_return:.2%}")
        else:
            print("No portfolio values found")
        
        # Get portfolio weights
        print("\nPortfolio Weights:")
        print("-" * 20)
        portfolio_weights = db_manager.get_portfolio_weights(backtest_id=latest_backtest_id)
        
        if not portfolio_weights.empty:
            print(f"Found {len(portfolio_weights)} portfolio weight records")
            
            # Get unique tickers
            unique_tickers = portfolio_weights['ticker'].unique()
            print(f"Unique tickers: {', '.join(sorted(unique_tickers))}")
            
            # Show latest weights
            latest_date = portfolio_weights['date'].max()
            latest_weights = portfolio_weights[portfolio_weights['date'] == latest_date]
            
            print(f"\nLatest Portfolio Weights ({latest_date}):")
            for _, weight in latest_weights.iterrows():
                if weight['weight'] > 0:
                    print(f"  {weight['ticker']}: {weight['weight']:.2%}")
            
            # Show weight evolution for top tickers
            print(f"\nWeight Evolution (Top 5 Tickers):")
            ticker_weights = portfolio_weights.groupby('ticker')['weight'].sum().sort_values(ascending=False)
            top_tickers = ticker_weights.head(5).index.tolist()
            
            for ticker in top_tickers:
                ticker_data = portfolio_weights[portfolio_weights['ticker'] == ticker].sort_values('date')
                if not ticker_data.empty:
                    first_weight = ticker_data.iloc[0]['weight']
                    last_weight = ticker_data.iloc[-1]['weight']
                    print(f"  {ticker}: {first_weight:.2%} → {last_weight:.2%}")
        else:
            print("No portfolio weights found")
        
        # Get portfolio weights as pivot table
        print("\nPortfolio Weights Pivot Table:")
        print("-" * 30)
        weights_pivot = db_manager.get_portfolio_weights_pivot(latest_backtest_id)
        
        if not weights_pivot.empty:
            print(f"Pivot table shape: {weights_pivot.shape}")
            print(f"Date range: {weights_pivot.index.min()} to {weights_pivot.index.max()}")
            print(f"Tickers: {', '.join(weights_pivot.columns.tolist())}")
            
            # Show sample of pivot table
            print(f"\nSample of pivot table (last 5 dates):")
            print(weights_pivot.tail().round(4))
        else:
            print("No pivot table data available")
        
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
