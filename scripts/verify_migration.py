#!/usr/bin/env python3
"""Quick verification of migration results."""

import sys
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from database import DatabaseManager

db = DatabaseManager()
if db.connect():
    companies = db.execute_query('SELECT COUNT(*) as count FROM varrock.companies')
    tickers = db.execute_query('SELECT COUNT(*) as count FROM varrock.tickers')
    universe_companies = db.execute_query('SELECT COUNT(*) as count FROM universe_companies')
    company_info = db.execute_query('SELECT COUNT(*) as count FROM varrock.company_info')
    main_tickers = db.execute_query('SELECT COUNT(*) as count FROM varrock.tickers WHERE is_main_ticker = TRUE')
    
    print("\n" + "="*60)
    print("Migration Verification Results")
    print("="*60)
    print(f"Companies created:        {companies.iloc[0]['count']}")
    print(f"Tickers stored:           {tickers.iloc[0]['count']}")
    print(f"Company info records:     {company_info.iloc[0]['count']}")
    print(f"Main tickers determined:  {main_tickers.iloc[0]['count']}")
    print(f"Universe companies:       {universe_companies.iloc[0]['count']}")
    print("="*60)
    
    # Show sample data
    sample = db.execute_query("""
        SELECT 
            c.company_uid,
            ci.name,
            t.ticker,
            t.exchange,
            t.is_main_ticker
        FROM varrock.companies c
        LEFT JOIN varrock.company_info ci ON c.company_uid = ci.company_uid
        LEFT JOIN varrock.tickers t ON c.company_uid = t.company_uid AND t.is_main_ticker = TRUE
        LIMIT 5
    """)
    
    if not sample.empty:
        print("\nSample Data (first 5 companies):")
        print("-" * 60)
        for _, row in sample.iterrows():
            print(f"Company: {row.get('name', 'N/A')} | Ticker: {row.get('ticker', 'N/A')} | Exchange: {row.get('exchange', 'N/A')} | Main: {row.get('is_main_ticker', False)}")
    
    db.disconnect()
    print("\n✓ Verification complete!")
else:
    print("Failed to connect to database")

