#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.manager import DatabaseManager

def main():
    db = DatabaseManager()
    if db.connect():
        # Get all backtests and look for YouTube ones
        query = "SELECT id, name, start_date, end_date, created_at FROM backtests WHERE name LIKE '%YouTube%' OR name LIKE '%youtube%' ORDER BY created_at DESC"
        result = db.execute_query(query)
        print(f'Found {len(result)} YouTube backtests:')
        for _, row in result.iterrows():
            print(f'  - ID: {row["id"]}, Name: {row["name"]}, Start: {row["start_date"]}, End: {row["end_date"]}, Created: {row["created_at"]}')
    else:
        print('Failed to connect to database')

if __name__ == "__main__":
    main()
