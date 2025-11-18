#!/usr/bin/env python3
"""
Verify that decay is being applied correctly by checking signal metadata in the database.
"""

import os
import sys
import psycopg2
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
env_path = Path(__file__).parent.parent / 'Alpha-Crucible-Quant' / '.env'
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv()

def get_main_db_connection():
    """Get connection to main database."""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return psycopg2.connect(database_url)
        
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT', '5432')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')
        
        if not all([host, user, password, database]):
            raise ValueError("Database connection parameters not found")
        
        return psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def verify_decay_for_ticker(conn, ticker: str, check_date: date):
    """Verify decay is working for a specific ticker and date."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT value, metadata, asof_date
                FROM signal_raw
                WHERE ticker = %s
                AND signal_name = 'SENTIMENT_YFINANCE_NEWS'
                AND asof_date = %s
                ORDER BY asof_date DESC
                LIMIT 1;
            """, (ticker, check_date))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            value, metadata, asof_date = row
            
            return {
                'ticker': ticker,
                'date': asof_date,
                'value': value,
                'metadata': metadata
            }
    except Exception as e:
        print(f"Error querying database: {e}")
        return None

def analyze_decay_metadata(metadata):
    """Analyze metadata to verify decay is working."""
    if not metadata:
        return None
    
    result = {
        'has_decay_factor': 'decay_factor' in metadata,
        'decay_factor': metadata.get('decay_factor'),
        'has_sentiment_by_day': 'sentiment_by_day' in metadata,
        'sentiment_by_day': metadata.get('sentiment_by_day', {}),
        'total_weight': metadata.get('total_weight'),
        'calculation_method': metadata.get('calculation_method')
    }
    
    # Verify decay weights
    if result['has_sentiment_by_day']:
        weights_verified = []
        for days_ago_str, day_data in result['sentiment_by_day'].items():
            days_ago = int(days_ago_str)
            expected_weight = 0.5 ** days_ago
            actual_weight_per_item = day_data.get('total_weight', 0) / max(day_data.get('count', 1), 1)
            weights_verified.append({
                'days_ago': days_ago,
                'expected_weight': expected_weight,
                'actual_weight': actual_weight_per_item,
                'count': day_data.get('count', 0),
                'matches': abs(actual_weight_per_item - expected_weight) < 0.0001
            })
        result['weights_verified'] = weights_verified
    
    return result

def main():
    """Main verification function."""
    conn = None
    try:
        print("=" * 60)
        print("Verifying Decay in News Signal Scores")
        print("=" * 60)
        
        conn = get_main_db_connection()
        print("✓ Connected to database\n")
        
        # Get some recent signals to verify
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT ticker, asof_date, value, metadata
                FROM signal_raw
                WHERE signal_name = 'SENTIMENT_YFINANCE_NEWS'
                AND value IS NOT NULL
                AND metadata IS NOT NULL
                ORDER BY asof_date DESC, ticker
                LIMIT 10;
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                print("No signals found in database")
                return
            
            print(f"Found {len(rows)} signals to verify\n")
            
            for ticker, asof_date, value, metadata in rows:
                print(f"{'='*60}")
                print(f"Ticker: {ticker}, Date: {asof_date}")
                print(f"Signal Value: {value:.6f}")
                print(f"{'='*60}")
                
                if metadata:
                    analysis = analyze_decay_metadata(metadata)
                    
                    if analysis:
                        print(f"Calculation Method: {analysis.get('calculation_method', 'N/A')}")
                        print(f"Decay Factor: {analysis.get('decay_factor', 'N/A')}")
                        print(f"Total Weight: {analysis.get('total_weight', 'N/A')}")
                        
                        if analysis.get('has_decay_factor'):
                            print(f"✓ Decay factor found in metadata")
                        else:
                            print(f"✗ Decay factor NOT found in metadata")
                        
                        if analysis.get('has_sentiment_by_day'):
                            print(f"\nSentiment by Day Breakdown:")
                            weights_verified = analysis.get('weights_verified', [])
                            for wv in sorted(weights_verified, key=lambda x: x['days_ago']):
                                status = "✓" if wv['matches'] else "✗"
                                print(f"  {status} Day {wv['days_ago']}: "
                                      f"count={wv['count']}, "
                                      f"weight={wv['actual_weight']:.6f} "
                                      f"(expected: {wv['expected_weight']:.6f})")
                            
                            # Check if all weights match
                            all_match = all(wv['matches'] for wv in weights_verified)
                            if all_match:
                                print(f"\n✓ PASS: All decay weights are correct!")
                            else:
                                print(f"\n✗ FAIL: Some decay weights are incorrect!")
                        else:
                            print(f"✗ No sentiment_by_day breakdown in metadata")
                    else:
                        print("Could not analyze metadata")
                else:
                    print("✗ No metadata found")
                
                print()
        
        print("=" * 60)
        print("Verification complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()


