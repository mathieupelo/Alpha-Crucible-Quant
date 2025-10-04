#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.manager import DatabaseManager

def main():
    db = DatabaseManager()
    if db.connect():
        print('Database connected successfully')
        
        # Check if backtests table exists and has data
        query = "SELECT COUNT(*) as count FROM backtests"
        result = db.execute_query(query)
        print(f"Total backtests in database: {result.iloc[0]['count'] if not result.empty else 0}")
        
        # Get a few sample backtests
        query = "SELECT id, name, start_date, end_date, created_at FROM backtests ORDER BY created_at DESC LIMIT 5"
        result = db.execute_query(query)
        
        if not result.empty:
            print("\nSample backtests:")
            for _, row in result.iterrows():
                print(f"  - ID: {row['id']}, Name: {row['name']}, Start: {row['start_date']}, End: {row['end_date']}")
        else:
            print("No backtests found in database")
            
        # Check if there are any backtests with "YouTube" in the name
        query = "SELECT id, name, start_date, end_date FROM backtests WHERE name LIKE '%YouTube%' OR name LIKE '%youtube%'"
        result = db.execute_query(query)
        
        if not result.empty:
            print(f"\nFound {len(result)} YouTube backtests:")
            for _, row in result.iterrows():
                print(f"  - ID: {row['id']}, Name: {row['name']}, Start: {row['start_date']}, End: {row['end_date']}")
        else:
            print("\nNo YouTube backtests found")
            
    else:
        print('Failed to connect to database')

if __name__ == "__main__":
    main()
