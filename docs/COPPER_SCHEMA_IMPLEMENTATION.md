# Copper Schema Implementation for YouTube Comments

This document describes the implementation of the `copper` schema for storing and retrieving YouTube comments data for sentiment analysis.

## Overview

The copper schema provides a database-backed solution for YouTube sentiment signals, replacing direct API calls with efficient database queries. This implementation ensures:

- **Point-in-time data integrity**: Only comments published on/before the target date are considered
- **Game release filtering**: Only considers trailers for games that haven't been released yet (with 7-day buffer)
- **Idempotent operations**: Safe to run scripts multiple times without duplicates
- **Efficient querying**: SQL-based filtering instead of Python-based filtering
- **Scalable architecture**: Handles large volumes of comments efficiently

### Game Release Logic

The system implements a **two-phase filtering approach**:

#### Phase 1: Data Collection (`insert_copper.py`)
- **Trailer Release Date**: Only collect comments from trailers released on/before the target date
- **No Game Release Filtering**: Collect comments from ALL eligible trailers regardless of game release status
- **Rationale**: Build comprehensive dataset for analysis flexibility

#### Phase 2: Sentiment Calculation (`sentiment_yt.py`)
- **Trailer Release Date**: Trailer must be released on/before the target date
- **Game Release Date**: Game must not be released yet (with 7-day buffer)
- **Rationale**: Stock sentiment should reflect anticipation before release, not post-release reactions

**Example Workflow**:
1. **Data Collection** (2025-10-01): Collect comments from GTA VI and Red Dead 2 trailers
2. **Sentiment Calculation** (2025-10-01): 
   - ✅ **Include**: GTA VI (game releases 2025-12-31)
   - ❌ **Exclude**: Red Dead 2 (game released 2019-11-05, within buffer)

This separation allows for flexible analysis while maintaining business logic integrity.

## Architecture

### Components

1. **Copper Schema** (`copper.youtube_comments`)
   - Stores YouTube comments with metadata
   - Optimized indexes for video_id and published_at filtering
   - Unique constraint on comment_id to prevent duplicates

2. **CopperService** (`src/services/copper_service.py`)
   - Database operations for YouTube comments
   - Point-in-time filtering capabilities
   - Batch insertion with upsert logic

3. **YouTubeCommentsFetcher** (`src/services/youtube_comments_fetcher.py`)
   - Fetches comments from YouTube Data API v3
   - Handles rate limiting and error cases
   - Formats data for database storage

4. **Modified SentimentSignalYT** (`src/signals/sentiment_yt.py`)
   - Now reads from database instead of direct API calls
   - Maintains same interface and output format
   - Improved performance with SQL-based filtering

### Database Schema

```sql
CREATE DATABASE copper;

CREATE TABLE copper.youtube_comments (
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
);
```

### Trailer Map Structure

The `data/trailer_map.json` file now includes `game_release_date` for each trailer:

```json
{
  "TTWO": [
    {
      "game": "GTA VI",
      "trailer_url": "https://www.youtube.com/watch?v=QdBZY2fkU-0",
      "release_date": "2023-12-04",
      "game_release_date": "2025-12-31"
    }
  ]
}
```

**Fields:**
- `game`: Game name
- `trailer_url`: YouTube trailer URL
- `release_date`: When the trailer was published
- `game_release_date`: When the actual game was/will be released

## Setup Instructions

### Prerequisites

1. **YouTube Data API Key**: Add `YOUTUBE_API_KEY` to your `.env` file
2. **MySQL Database**: Ensure MySQL is running and accessible
3. **Python Dependencies**: All required packages should be installed

### Environment Variables

Ensure these are set in your `.env` file:

```bash
# Database connection
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=signal_forge

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### Installation Steps

1. **Create Copper Schema and Table**
   ```bash
   python scripts/setup_database_signal_schema.py
   ```

2. **Test the Implementation**
   ```bash
   python scripts/test_copper_implementation.py
   ```

3. **Bulk Ingest Comments for GameCore-12**
   ```bash
   python scripts/insert_copper.py
   ```

4. **Verify Sentiment Calculation**
   ```bash
   python -c "
   from src.signals.sentiment_yt import SentimentSignalYT
   from datetime import date
   
   signal = SentimentSignalYT()
   result = signal.calculate(None, 'TTWO', date.today())
   print(f'Sentiment for TTWO: {result}')
   "
   ```

## Usage

### Bulk Comment Ingestion

The `scripts/insert_copper.py` script ingests comments for all GameCore-12 tickers:

```bash
python scripts/insert_copper.py
```

**Features:**
- Processes all GameCore-12 tickers from database
- Filters trailers by release date (point-in-time) - only includes trailers released on/before target date
- Fetches up to 10,000 comments per video
- **Collects ALL eligible trailers** - game release date filtering is applied during sentiment calculation
- Provides detailed progress logging
- Idempotent operation (safe to re-run)

### Sentiment Calculation

The sentiment calculation now uses database queries:

```python
from src.signals.sentiment_yt import SentimentSignalYT
from datetime import date

signal = SentimentSignalYT()
sentiment_score = signal.calculate(None, 'TTWO', date.today())
```

**Key Changes:**
- No direct YouTube API calls during calculation
- SQL-based filtering for efficiency
- Same output format as before
- Improved performance

### Database Operations

Direct database operations using CopperService:

```python
from src.services.copper_service import CopperService
from datetime import date

# Connect to copper database
copper_service = CopperService()
copper_service.connect()

# Get comments for a video up to a specific date
comments_df = copper_service.get_comments_by_video_and_date(
    'QdBZY2fkU-0',  # GTA VI video ID
    date.today()
)

# Insert new comments
comments = [
    {
        'comment_id': 'unique_id',
        'video_id': 'video_id',
        'text_content': 'Comment text',
        'author_display_name': 'Author',
        'like_count': 5,
        'published_at': datetime.now()
    }
]
copper_service.insert_youtube_comments(comments)
```

## Data Flow

1. **Ingestion Phase**
   ```
   GameCore-12 Tickers → Trailer URLs → YouTube API → Comments → Copper DB
   ```

2. **Calculation Phase**
   ```
   Ticker → Eligible Trailers → Video IDs → Copper DB Query → Sentiment Score
   ```

## Performance Optimizations

### Database Indexes

- `idx_video_id`: Fast lookup by video
- `idx_published_at`: Efficient date filtering
- `idx_video_published`: Compound index for combined queries

### Query Optimization

- Point-in-time filtering at SQL level
- Batch insertion with upsert logic
- Connection pooling for multiple operations

### Rate Limiting

- YouTube API quota management
- Error handling for rate limit exceeded
- Graceful degradation when API unavailable

## Error Handling

### Common Issues

1. **YouTube API Quota Exceeded**
   - Error logged with warning level
   - Processing continues with other videos
   - No system failure

2. **Database Connection Issues**
   - Automatic reconnection attempts
   - Clear error messages
   - Graceful degradation

3. **Invalid Video URLs**
   - URL parsing errors logged
   - Processing continues with valid URLs
   - No system failure

### Monitoring

- Comprehensive logging at all levels
- Progress tracking for bulk operations
- Error counts and summaries

## Testing

### Smoke Tests

Run the comprehensive test suite:

```bash
python scripts/test_copper_implementation.py
```

**Test Coverage:**
- Schema and table accessibility
- YouTube API availability
- Comment fetching functionality
- Database insertion operations
- Sentiment calculation
- GameCore-12 ticker access

### Manual Verification

1. **Check Database Contents**
   ```sql
   USE copper;
   SELECT COUNT(*) FROM youtube_comments;
   SELECT video_id, COUNT(*) as comment_count 
   FROM youtube_comments 
   GROUP BY video_id;
   ```

2. **Verify Point-in-Time Filtering**
   ```sql
   SELECT COUNT(*) FROM youtube_comments 
   WHERE published_at <= '2024-01-01 23:59:59';
   ```

## Maintenance

### Regular Tasks

1. **Comment Ingestion**: Run `insert_copper.py` regularly to keep data fresh
2. **Database Maintenance**: Monitor table size and performance
3. **API Quota**: Monitor YouTube API usage

### Backup and Recovery

- Standard MySQL backup procedures apply
- Copper schema can be recreated using setup script
- Data can be re-ingested from YouTube API

## Troubleshooting

### Common Problems

1. **"YouTube API not available"**
   - Check `YOUTUBE_API_KEY` in `.env`
   - Verify API key has YouTube Data API v3 enabled
   - Check quota limits in Google Cloud Console

2. **"Failed to connect to copper database"**
   - Verify MySQL is running
   - Check database connection parameters
   - Ensure copper schema exists

3. **"No comments found"**
   - Check if videos have comments enabled
   - Verify video URLs are accessible
   - Check point-in-time date filtering

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Incremental Updates**: Only fetch new comments since last update
2. **Comment Threading**: Store reply relationships
3. **Sentiment Caching**: Pre-calculate sentiment scores
4. **Video Metadata**: Store video titles, descriptions, etc.
5. **Multi-language Support**: Handle non-English comments

## API Reference

### CopperService Methods

- `insert_youtube_comments(comments)`: Insert/update comments
- `get_comments_by_video_and_date(video_id, as_of_date)`: Get comments for a video
- `get_comments_by_video_ids_and_date(video_ids, as_of_date)`: Get comments for multiple videos
- `get_comment_count_by_video(video_id)`: Get comment count
- `clear_comments_for_video(video_id)`: Clear all comments for a video

### YouTubeCommentsFetcher Methods

- `fetch_comments_for_video(video_url, max_comments)`: Fetch comments for a single video
- `fetch_comments_for_videos(video_urls, max_comments_per_video)`: Fetch comments for multiple videos
- `is_api_available()`: Check if YouTube API is available

### SentimentSignalYT Changes

- `calculate()`: Now uses database instead of direct API calls
- Same interface and output format as before
- Improved performance and reliability
