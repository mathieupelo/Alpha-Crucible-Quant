#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.manager import DatabaseManager

def main():
    db = DatabaseManager()
    if db.connect():
        print('Database connected successfully')
        
        # Test the get_backtests method directly
        print("\nTesting get_backtests() method:")
        backtests_df = db.get_backtests()
        print(f"Type: {type(backtests_df)}")
        print(f"Empty: {backtests_df.empty}")
        print(f"Shape: {backtests_df.shape}")
        print(f"Columns: {list(backtests_df.columns)}")
        
        if not backtests_df.empty:
            print(f"\nFirst few rows:")
            print(backtests_df.head())
        else:
            print("DataFrame is empty")
            
        # Test the execute_query method directly
        print("\nTesting execute_query() method:")
        query = "SELECT id, name, start_date, end_date FROM backtests ORDER BY created_at DESC LIMIT 3"
        result_df = db.execute_query(query)
        print(f"Type: {type(result_df)}")
        print(f"Empty: {result_df.empty}")
        print(f"Shape: {result_df.shape}")
        print(f"Columns: {list(result_df.columns)}")
        
        if not result_df.empty:
            print(f"\nFirst few rows:")
            print(result_df.head())
        else:
            print("DataFrame is empty")
            
    else:
        print('Failed to connect to database')

if __name__ == "__main__":
    main()
