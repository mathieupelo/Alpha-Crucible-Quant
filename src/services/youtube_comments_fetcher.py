"""
YouTube comments fetcher service.

Fetches comments from YouTube API and formats them for database storage.
"""

import os
import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeCommentsFetcher:
    """Fetches YouTube comments using the YouTube Data API v3."""
    
    def __init__(self, youtube_api_key: str = None):
        """
        Initialize YouTube comments fetcher.
        
        Args:
            youtube_api_key: YouTube Data API key (optional, will try env var)
        """
        self.youtube_api_key = youtube_api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube_service = None
        
        if self.youtube_api_key:
            self.youtube_service = self._get_youtube_service()
    
    def _get_youtube_service(self):
        """Initialize YouTube Data API service."""
        if not self.youtube_api_key:
            logger.warning("YouTube API key not provided")
            return None
        
        try:
            return build('youtube', 'v3', developerKey=self.youtube_api_key)
        except Exception as e:
            logger.error(f"Error initializing YouTube service: {e}")
            return None
    
    def _parse_video_id(self, url: str) -> Optional[str]:
        """
        Parse YouTube video ID from various URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if not found
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/shorts/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_comments_for_video(
        self, 
        video_url: str, 
        max_comments: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        Fetch comments for a YouTube video.
        
        Args:
            video_url: YouTube video URL
            max_comments: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries formatted for database storage
        """
        if not self.youtube_service:
            logger.warning("YouTube service not available")
            return []
        
        video_id = self._parse_video_id(video_url)
        if not video_id:
            logger.warning(f"Could not parse video ID from {video_url}")
            return []
        
        comments = []
        
        try:
            # Get video comments
            request = self.youtube_service.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_comments),  # YouTube API max is 100 per request
                order='time'
            )
            
            while request and len(comments) < max_comments:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    # Parse published date
                    published_at = datetime.fromisoformat(
                        comment['publishedAt'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    
                    # Format comment for database storage
                    formatted_comment = {
                        'comment_id': item['id'],
                        'video_id': video_id,
                        'text_content': comment['textDisplay'],
                        'author_display_name': comment['authorDisplayName'],
                        'like_count': comment.get('likeCount', 0),
                        'published_at': published_at
                    }
                    
                    comments.append(formatted_comment)
                
                # Check if we have more pages
                if 'nextPageToken' in response and len(comments) < max_comments:
                    request = self.youtube_service.commentThreads().list_next(request, response)
                else:
                    break
                    
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning(f"YouTube API quota exceeded or video comments disabled for {video_id}: {e}")
            else:
                logger.warning(f"YouTube API error for video {video_id}: {e}")
        except Exception as e:
            logger.warning(f"Error fetching comments for video {video_id}: {e}")
        
        logger.info(f"Fetched {len(comments)} comments for video {video_id}")
        return comments[:max_comments]
    
    def fetch_comments_for_videos(
        self, 
        video_urls: List[str], 
        max_comments_per_video: int = 1000
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch comments for multiple YouTube videos.
        
        Args:
            video_urls: List of YouTube video URLs
            max_comments_per_video: Maximum comments per video
            
        Returns:
            Dictionary mapping video_id to list of comments
        """
        results = {}
        
        for video_url in video_urls:
            video_id = self._parse_video_id(video_url)
            if not video_id:
                logger.warning(f"Skipping invalid URL: {video_url}")
                continue
            
            comments = self.fetch_comments_for_video(video_url, max_comments_per_video)
            results[video_id] = comments
            
            logger.info(f"Processed {video_url} -> {len(comments)} comments")
        
        total_comments = sum(len(comments) for comments in results.values())
        logger.info(f"Total comments fetched: {total_comments} from {len(results)} videos")
        
        return results
    
    def is_api_available(self) -> bool:
        """Check if YouTube API is available."""
        return self.youtube_service is not None
