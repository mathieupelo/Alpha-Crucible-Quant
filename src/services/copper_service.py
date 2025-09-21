"""
Copper schema service for YouTube comments data.

Provides database operations for the copper.youtube_comments table.
"""

import os
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class CopperService:
    """Service for managing YouTube comments in the copper schema."""
    
    def __init__(self):
        """Initialize copper service with database connection parameters."""
        self.host = os.getenv('DB_HOST', '127.0.0.1')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = 'copper'
        self._connection = None
    
    def connect(self) -> bool:
        """Establish connection to the copper database."""
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            if self._connection.is_connected():
                logger.debug(f"Connected to copper database")
                return True
        except Error as e:
            logger.error(f"Error connecting to copper database: {e}")
            return False
        return False
    
    def disconnect(self):
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.debug("Copper database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self._connection and self._connection.is_connected()
    
    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary."""
        if not self.is_connected():
            self.connect()
    
    def insert_youtube_comments(self, comments: List[Dict[str, Any]]) -> int:
        """
        Insert YouTube comments into the copper.youtube_comments table.
        
        Args:
            comments: List of comment dictionaries with keys:
                     - comment_id: YouTube comment ID
                     - video_id: YouTube video ID
                     - text_content: Comment text
                     - author_display_name: Author name
                     - like_count: Number of likes
                     - published_at: Publication datetime (UTC)
        
        Returns:
            Number of comments inserted/updated
        """
        if not comments:
            return 0
        
        query = """
        INSERT INTO youtube_comments (
            comment_id, video_id, text_content, author_display_name, 
            like_count, published_at, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            text_content = VALUES(text_content),
            author_display_name = VALUES(author_display_name),
            like_count = VALUES(like_count),
            published_at = VALUES(published_at),
            updated_at = VALUES(updated_at)
        """
        
        self.ensure_connection()
        cursor = self._connection.cursor()
        
        try:
            params_list = []
            current_time = datetime.now()
            
            for comment in comments:
                params_list.append((
                    comment['comment_id'],
                    comment['video_id'],
                    comment['text_content'],
                    comment.get('author_display_name'),
                    comment.get('like_count', 0),
                    comment['published_at'],
                    current_time,
                    current_time
                ))
            
            cursor.executemany(query, params_list)
            inserted_count = cursor.rowcount
            logger.info(f"Inserted/updated {inserted_count} YouTube comments")
            return inserted_count
            
        except Error as e:
            logger.error(f"Error inserting YouTube comments: {e}")
            raise
        finally:
            cursor.close()
    
    def get_comments_by_video_and_date(
        self, 
        video_id: str, 
        as_of_date: date
    ) -> pd.DataFrame:
        """
        Get comments for a specific video published on or before the as_of_date.
        
        Args:
            video_id: YouTube video ID
            as_of_date: Date to filter comments by (point-in-time)
        
        Returns:
            DataFrame with comments data
        """
        query = """
        SELECT comment_id, video_id, text_content, author_display_name, 
               like_count, published_at
        FROM youtube_comments
        WHERE video_id = %s AND published_at <= %s
        ORDER BY published_at DESC
        """
        
        self.ensure_connection()
        cursor = self._connection.cursor(dictionary=True)
        
        try:
            # Convert date to datetime for comparison
            as_of_datetime = datetime.combine(as_of_date, datetime.max.time())
            cursor.execute(query, (video_id, as_of_datetime))
            results = cursor.fetchall()
            
            if not results:
                return pd.DataFrame()
            
            return pd.DataFrame(results)
            
        except Error as e:
            logger.error(f"Error fetching comments for video {video_id}: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
    
    def get_comments_by_video_ids_and_date(
        self, 
        video_ids: List[str], 
        as_of_date: date
    ) -> pd.DataFrame:
        """
        Get comments for multiple videos published on or before the as_of_date.
        
        Args:
            video_ids: List of YouTube video IDs
            as_of_date: Date to filter comments by (point-in-time)
        
        Returns:
            DataFrame with comments data
        """
        if not video_ids:
            return pd.DataFrame()
        
        placeholders = ','.join(['%s'] * len(video_ids))
        query = f"""
        SELECT comment_id, video_id, text_content, author_display_name, 
               like_count, published_at
        FROM youtube_comments
        WHERE video_id IN ({placeholders}) AND published_at <= %s
        ORDER BY video_id, published_at DESC
        """
        
        self.ensure_connection()
        cursor = self._connection.cursor(dictionary=True)
        
        try:
            # Convert date to datetime for comparison
            as_of_datetime = datetime.combine(as_of_date, datetime.max.time())
            params = video_ids + [as_of_datetime]
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if not results:
                return pd.DataFrame()
            
            return pd.DataFrame(results)
            
        except Error as e:
            logger.error(f"Error fetching comments for videos: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
    
    def get_comment_count_by_video(self, video_id: str) -> int:
        """Get the total number of comments for a video."""
        query = "SELECT COUNT(*) as count FROM youtube_comments WHERE video_id = %s"
        
        self.ensure_connection()
        cursor = self._connection.cursor()
        
        try:
            cursor.execute(query, (video_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logger.error(f"Error getting comment count for video {video_id}: {e}")
            return 0
        finally:
            cursor.close()
    
    def clear_comments_for_video(self, video_id: str) -> int:
        """Clear all comments for a specific video."""
        query = "DELETE FROM youtube_comments WHERE video_id = %s"
        
        self.ensure_connection()
        cursor = self._connection.cursor()
        
        try:
            cursor.execute(query, (video_id,))
            deleted_count = cursor.rowcount
            logger.info(f"Deleted {deleted_count} comments for video {video_id}")
            return deleted_count
        except Error as e:
            logger.error(f"Error clearing comments for video {video_id}: {e}")
            raise
        finally:
            cursor.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute a SELECT query and return results as DataFrame."""
        self.ensure_connection()
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                return pd.DataFrame()
            
            return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"Database error in execute_query: {e}")
            return pd.DataFrame()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
