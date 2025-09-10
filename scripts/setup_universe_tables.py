#!/usr/bin/env python3
"""
Setup Universe Tables

Script to create the universe and universe_tickers tables in the database.
"""

import sys
import os
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Add src to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Load environment variables
load_dotenv()

def create_universe_tables():
    """Create universe tables in the database."""
    try:
        # Database connection parameters
        host = os.getenv('DB_HOST', '127.0.0.1')
        port = int(os.getenv('DB_PORT', '3306'))
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'signal_forge')
        
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            print(f"Connected to MySQL database: {database}")
            
            cursor = connection.cursor()
            
            # Read and execute the SQL file
            sql_file_path = Path(__file__).parent / 'create_universe_tables.sql'
            
            if not sql_file_path.exists():
                print(f"Error: SQL file not found at {sql_file_path}")
                return False
            
            with open(sql_file_path, 'r') as file:
                sql_script = file.read()
            
            # Split the script into individual statements
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    print(f"Executing: {statement[:50]}...")
                    cursor.execute(statement)
            
            connection.commit()
            print("Universe tables created successfully!")
            
            # Verify tables were created
            cursor.execute("SHOW TABLES LIKE 'universes'")
            if cursor.fetchone():
                print("✓ 'universes' table created")
            else:
                print("✗ 'universes' table not found")
            
            cursor.execute("SHOW TABLES LIKE 'universe_tickers'")
            if cursor.fetchone():
                print("✓ 'universe_tickers' table created")
            else:
                print("✗ 'universe_tickers' table not found")
            
            return True
            
    except Error as e:
        print(f"Error: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    print("Setting up universe tables...")
    success = create_universe_tables()
    
    if success:
        print("\n✅ Universe tables setup completed successfully!")
    else:
        print("\n❌ Universe tables setup failed!")
        sys.exit(1)
