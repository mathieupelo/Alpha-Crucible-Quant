#!/usr/bin/env python3
"""
Test script to test the backend API directly.
"""

import requests
import json
from datetime import date

def test_backend_api():
    """Test the backend API directly."""
    base_url = "http://localhost:8000/api"
    
    try:
        # Test 1: Get existing backtests
        print("=== Testing GET /backtests ===")
        response = requests.get(f"{base_url}/backtests?page=1&size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['backtests'])} backtests")
            for i, backtest in enumerate(data['backtests'][:3]):
                print(f"Backtest {i+1}:")
                print(f"  Run ID: {backtest['run_id']}")
                print(f"  Name: {backtest.get('name', 'MISSING')}")
                print(f"  Start Date: {backtest['start_date']}")
                print(f"  End Date: {backtest['end_date']}")
                print("  ---")
        else:
            print(f"Error getting backtests: {response.status_code} - {response.text}")
            return False
        
        # Test 2: Create a new backtest with a name
        print("\n=== Testing POST /backtests ===")
        new_backtest = {
            "name": "API Test Backtest",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "universe_id": 1,
            "signals": ["RSI", "SMA"],
            "initial_capital": 10000,
            "rebalancing_frequency": "monthly",
            "transaction_costs": 0.001,
            "max_weight": 0.1,
            "min_weight": 0.0,
            "risk_aversion": 0.5,
            "benchmark_ticker": "SPY",
            "use_equal_weight_benchmark": True,
            "min_lookback_days": 252,
            "max_lookback_days": 756,
            "signal_combination_method": "equal_weight",
            "forward_fill_signals": True
        }
        
        print(f"Creating backtest with name: {new_backtest['name']}")
        response = requests.post(f"{base_url}/backtests", json=new_backtest)
        
        if response.status_code == 200:
            created_backtest = response.json()
            print("Backtest created successfully!")
            print(f"  Run ID: {created_backtest['run_id']}")
            print(f"  Name: {created_backtest.get('name', 'MISSING')}")
            print(f"  Start Date: {created_backtest['start_date']}")
            print(f"  End Date: {created_backtest['end_date']}")
            
            # Test 3: Get the created backtest by run_id
            print(f"\n=== Testing GET /backtests/{created_backtest['run_id']} ===")
            response = requests.get(f"{base_url}/backtests/{created_backtest['run_id']}")
            if response.status_code == 200:
                retrieved_backtest = response.json()
                print("Retrieved backtest successfully!")
                print(f"  Run ID: {retrieved_backtest['run_id']}")
                print(f"  Name: {retrieved_backtest.get('name', 'MISSING')}")
                print(f"  Start Date: {retrieved_backtest['start_date']}")
                print(f"  End Date: {retrieved_backtest['end_date']}")
            else:
                print(f"Error retrieving backtest: {response.status_code} - {response.text}")
        else:
            print(f"Error creating backtest: {response.status_code} - {response.text}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to backend API. Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_backend_api()
