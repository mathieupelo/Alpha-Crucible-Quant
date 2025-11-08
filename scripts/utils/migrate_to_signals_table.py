#!/usr/bin/env python3
"""
Database migration script to restructure the database with a signals table.

⚠️ ONE-TIME USE ONLY ⚠️
This migration script should only be run once. If the migration has already been
completed, this script should not be run again as it may cause data issues.

This script:
1. Creates a new signals table for signal definitions
2. Modifies signal_raw to reference signals.id instead of signal_name
3. Creates backtest_signals junction table
4. Migrates existing data from signal_name strings to signal IDs

Status: This migration should be complete. Only run if setting up a new database
from scratch or if explicitly instructed to re-run the migration.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import psycopg2
from psycopg2 import Error as PgError
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database migration to signals table structure."""
    
    def __init__(self):
        """Initialize migrator with database connection."""
        self.database_url = os.getenv('DATABASE_URL')
        self.host = os.getenv('DB_HOST', '127.0.0.1')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'postgres')
        self._connection = None
    
    def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            common_kwargs = {
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 3,
            }
            if self.database_url:
                url_lower = self.database_url.lower()
                has_query = '?' in self.database_url
                has_ssl = 'sslmode=' in url_lower
                if not has_ssl:
                    separator = '&' if has_query else '?'
                    self.database_url = f"{self.database_url}{separator}sslmode=require"
                self._connection = psycopg2.connect(self.database_url, **common_kwargs)
            else:
                self._connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    sslmode="require",
                    **common_kwargs
                )
            
            if self._connection:
                self._connection.autocommit = False  # Use transactions
                logger.info(f"Connected to PostgreSQL database: {self.database}")
                return True
        except PgError as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False
        return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("PostgreSQL connection closed")
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        cursor = self._connection.cursor()
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        cursor = self._connection.cursor()
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = %s
                );
            """, (table_name, column_name))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
    
    def step1_create_signals_table(self) -> bool:
        """Step 1: Create the signals table."""
        logger.info("Step 1: Creating signals table...")
        cursor = self._connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    enabled BOOLEAN DEFAULT TRUE,
                    parameters JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes separately
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_signals_name ON signals(name);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_signals_enabled ON signals(enabled);
            """)
            self._connection.commit()
            logger.info("✓ Created signals table")
            return True
        except Exception as e:
            self._connection.rollback()
            logger.error(f"✗ Error creating signals table: {e}")
            return False
        finally:
            cursor.close()
    
    def step2_migrate_signal_names(self) -> Dict[str, int]:
        """Step 2: Extract unique signal names and create signal records."""
        logger.info("Step 2: Migrating signal names to signals table...")
        cursor = self._connection.cursor()
        signal_map = {}
        
        try:
            # Get all unique signal names from signal_raw
            cursor.execute("""
                SELECT DISTINCT signal_name 
                FROM signal_raw 
                WHERE signal_name IS NOT NULL
                ORDER BY signal_name;
            """)
            signal_names = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Found {len(signal_names)} unique signal names")
            
            # Create signal records for each unique signal name
            for signal_name in signal_names:
                cursor.execute("""
                    INSERT INTO signals (name, description, enabled, created_at, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id;
                """, (signal_name, f"Signal: {signal_name}", True))
                
                result = cursor.fetchone()
                if result:
                    signal_id = result[0]
                else:
                    # Signal already exists, get its ID
                    cursor.execute("SELECT id FROM signals WHERE name = %s", (signal_name,))
                    signal_id = cursor.fetchone()[0]
                
                signal_map[signal_name] = signal_id
                logger.info(f"  Created/found signal: {signal_name} -> ID {signal_id}")
            
            self._connection.commit()
            logger.info(f"✓ Migrated {len(signal_map)} signal names to signals table")
            return signal_map
            
        except Exception as e:
            self._connection.rollback()
            logger.error(f"✗ Error migrating signal names: {e}")
            return {}
        finally:
            cursor.close()
    
    def step3_modify_signal_raw(self, signal_map: Dict[str, int]) -> bool:
        """Step 3: Modify signal_raw table to use signal_id."""
        logger.info("Step 3: Modifying signal_raw table structure...")
        cursor = self._connection.cursor()
        
        try:
            # Check if signal_id column already exists
            has_signal_id = self.check_column_exists('signal_raw', 'signal_id')
            
            if not has_signal_id:
                # Add signal_id column (nullable initially)
                cursor.execute("""
                    ALTER TABLE signal_raw 
                    ADD COLUMN signal_id INTEGER;
                """)
                logger.info("  Added signal_id column")
            
            # Populate signal_id from signal_map
            logger.info("  Populating signal_id values...")
            updated_total = 0
            for signal_name, signal_id in signal_map.items():
                cursor.execute("""
                    UPDATE signal_raw 
                    SET signal_id = %s 
                    WHERE signal_name = %s AND signal_id IS NULL;
                """, (signal_id, signal_name))
                updated_total += cursor.rowcount
            
            logger.info(f"  Updated {updated_total} total rows with signal_id")
            
            # Make signal_id NOT NULL after population
            cursor.execute("""
                ALTER TABLE signal_raw 
                ALTER COLUMN signal_id SET NOT NULL;
            """)
            
            # Add foreign key constraint
            cursor.execute("""
                ALTER TABLE signal_raw 
                ADD CONSTRAINT fk_signal_raw_signal 
                FOREIGN KEY (signal_id) REFERENCES signals(id) ON DELETE RESTRICT;
            """)
            
            # Add index on signal_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_signal_raw_signal_id 
                ON signal_raw(signal_id);
            """)
            
            # Update unique constraint to use signal_id instead of signal_name
            cursor.execute("""
                ALTER TABLE signal_raw 
                DROP CONSTRAINT IF EXISTS unique_signal_raw;
            """)
            
            cursor.execute("""
                ALTER TABLE signal_raw 
                ADD CONSTRAINT unique_signal_raw 
                UNIQUE (asof_date, ticker, signal_id);
            """)
            
            # Keep signal_name for backward compatibility (but make it nullable/optional)
            # Or we can remove it after migration - for now, keep it
            logger.info("  Kept signal_name column for backward compatibility")
            
            self._connection.commit()
            logger.info("✓ Modified signal_raw table structure")
            return True
            
        except Exception as e:
            self._connection.rollback()
            logger.error(f"✗ Error modifying signal_raw table: {e}")
            return False
        finally:
            cursor.close()
    
    def step4_create_backtest_signals(self) -> bool:
        """Step 4: Create backtest_signals junction table."""
        logger.info("Step 4: Creating backtest_signals junction table...")
        cursor = self._connection.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtest_signals (
                    id SERIAL PRIMARY KEY,
                    run_id VARCHAR(100) NOT NULL,
                    signal_id INTEGER NOT NULL,
                    weight FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (run_id, signal_id),
                    FOREIGN KEY (run_id) REFERENCES backtests(run_id) ON DELETE CASCADE,
                    FOREIGN KEY (signal_id) REFERENCES signals(id) ON DELETE RESTRICT
                );
            """)
            
            # Create indexes separately
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_backtest_signals_run_id ON backtest_signals(run_id);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_backtest_signals_signal_id ON backtest_signals(signal_id);
            """)
            
            self._connection.commit()
            logger.info("✓ Created backtest_signals junction table")
            return True
            
        except Exception as e:
            self._connection.rollback()
            logger.error(f"✗ Error creating backtest_signals table: {e}")
            return False
        finally:
            cursor.close()
    
    def step5_migrate_existing_backtests(self) -> bool:
        """Step 5: Extract signal names from existing backtests and create relationships."""
        logger.info("Step 5: Migrating existing backtest signals...")
        cursor = self._connection.cursor()
        
        try:
            # Get all backtests that might have signals in params
            cursor.execute("""
                SELECT run_id, params 
                FROM backtests 
                WHERE params IS NOT NULL;
            """)
            
            backtests = cursor.fetchall()
            logger.info(f"Found {len(backtests)} backtests with params")
            
            migrated_count = 0
            for run_id, params_json in backtests:
                if params_json is None:
                    continue
                
                try:
                    if isinstance(params_json, str):
                        params = json.loads(params_json)
                    else:
                        params = params_json
                    
                    # Look for signal-related fields in params
                    signals = params.get('signals', [])
                    signal_weights = params.get('signal_weights', {})
                    
                    if not signals:
                        continue
                    
                    # Create backtest_signal relationships
                    for signal_name in signals:
                        # Get signal_id
                        cursor.execute("SELECT id FROM signals WHERE name = %s", (signal_name,))
                        result = cursor.fetchone()
                        if result:
                            signal_id = result[0]
                            weight = signal_weights.get(signal_name, 1.0)
                            
                            cursor.execute("""
                                INSERT INTO backtest_signals (run_id, signal_id, weight)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (run_id, signal_id) DO UPDATE SET weight = EXCLUDED.weight;
                            """, (run_id, signal_id, weight))
                            migrated_count += 1
                
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Could not parse params for backtest {run_id}: {e}")
                    continue
            
            self._connection.commit()
            logger.info(f"✓ Migrated signals for {migrated_count} backtest-signal relationships")
            return True
            
        except Exception as e:
            self._connection.rollback()
            logger.error(f"✗ Error migrating backtest signals: {e}")
            return False
        finally:
            cursor.close()
    
    def migrate(self) -> bool:
        """Run the complete migration."""
        logger.info("=" * 60)
        logger.info("Starting database migration to signals table structure")
        logger.info("=" * 60)
        
        if not self.connect():
            logger.error("Failed to connect to database")
            return False
        
        try:
            # Step 1: Create signals table
            if not self.step1_create_signals_table():
                return False
            
            # Step 2: Migrate signal names
            signal_map = self.step2_migrate_signal_names()
            if not signal_map:
                logger.warning("No signals found to migrate")
            else:
                # Step 3: Modify signal_raw table
                if not self.step3_modify_signal_raw(signal_map):
                    return False
            
            # Step 4: Create backtest_signals junction table
            if not self.step4_create_backtest_signals():
                return False
            
            # Step 5: Migrate existing backtests
            self.step5_migrate_existing_backtests()
            
            logger.info("=" * 60)
            logger.info("Migration completed successfully!")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self._connection.rollback()
            return False
        finally:
            self.disconnect()


def main():
    """Main migration function."""
    migrator = DatabaseMigrator()
    success = migrator.migrate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

