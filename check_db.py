#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.manager import DatabaseManager

def main():
    db = DatabaseManager()
    if db.connect():
        print('Database connected successfully')
        # Check what backtests exist
        backtests = db.get_backtests()
        print(f'Found {len(backtests)} backtests:')
        for i, bt in enumerate(backtests[:10]):  # Show first 10
            if isinstance(bt, dict):
                print(f'  - ID: {bt.get("id", "N/A")}, Name: {bt.get("name", "N/A")}, Start: {bt.get("start_date", "N/A")}, End: {bt.get("end_date", "N/A")}')
            else:
                print(f'  - Backtest {i}: {bt}')
        if len(backtests) > 10:
            print(f'  ... and {len(backtests) - 10} more backtests')
    else:
        print('Failed to connect to database')

if __name__ == "__main__":
    main()
