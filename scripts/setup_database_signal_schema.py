#!/usr/bin/env python3
"""
Database setup script for signal-specific schemas.

Creates the 'copper' schema and tables for YouTube comments data.
This script is idempotent - it can be run multiple times safely.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_copper_schema():
    """Create the copper schema if it doesn't exist."""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    
    try:
        # Connect without specifying database
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create copper schema
        cursor.execute("CREATE DATABASE IF NOT EXISTS copper")
        logger.info("Schema 'copper' created or already exists")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        logger.error(f"Error creating copper schema: {e}")
        return False


def create_youtube_comments_table():
    """Create the youtube_comments table in the copper schema."""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='copper'
        )
        
        cursor = connection.cursor()
        
        # Create youtube_comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                comment_id VARCHAR(255) NOT NULL UNIQUE,
                video_id VARCHAR(255) NOT NULL,
                text_content TEXT NOT NULL,
                author_display_name VARCHAR(255),
                like_count INT DEFAULT 0,
                published_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_video_id (video_id),
                INDEX idx_published_at (published_at),
                INDEX idx_comment_id (comment_id),
                INDEX idx_video_published (video_id, published_at)
            )
        """)
        logger.info("Created youtube_comments table")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        logger.error(f"Error creating youtube_comments table: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("Starting copper schema setup...")
    
    # Create copper schema
    if not create_copper_schema():
        logger.error("Failed to create copper schema")
        return False
    
    # Create youtube_comments table
    if not create_youtube_comments_table():
        logger.error("Failed to create youtube_comments table")
        return False
    
    logger.info("Copper schema setup completed successfully!")
    logger.info("Created schema: copper")
    logger.info("Created table: copper.youtube_comments")
    logger.info("Table includes: comment_id, video_id, text_content, author_display_name, like_count, published_at")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
