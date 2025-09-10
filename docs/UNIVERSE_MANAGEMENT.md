# Universe Management System

This document describes the universe management system that allows users to create, manage, and validate universes of tickers for quantitative trading strategies.

## Overview

The universe management system provides a comprehensive solution for:
- Creating and managing universes of tickers
- Adding/removing tickers from universes
- Validating ticker symbols using real-time data from yfinance
- User-friendly interface with confirmation dialogs and error handling

## Architecture

### Backend Components

#### Database Schema

**Universes Table**
```sql
CREATE TABLE universes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Universe Tickers Table**
```sql
CREATE TABLE universe_tickers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    universe_id INT NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_universe_ticker (universe_id, ticker)
);
```

#### API Endpoints

**Universe Management**
- `GET /api/universes` - Get all universes
- `GET /api/universes/{id}` - Get specific universe
- `POST /api/universes` - Create new universe
- `PUT /api/universes/{id}` - Update universe
- `DELETE /api/universes/{id}` - Delete universe

**Ticker Management**
- `GET /api/universes/{id}/tickers` - Get universe tickers
- `PUT /api/universes/{id}/tickers` - Update all tickers
- `POST /api/universes/{id}/tickers` - Add single ticker
- `DELETE /api/universes/{id}/tickers/{ticker}` - Remove ticker

**Ticker Validation**
- `POST /api/tickers/validate` - Validate ticker symbols

#### Services

**DatabaseService**
- Handles all database operations for universes and tickers
- Provides CRUD operations with proper error handling
- Manages relationships between universes and tickers

**TickerValidationService**
- Validates ticker symbols using yfinance
- Supports batch validation with concurrent processing
- Provides detailed validation results with company names

### Frontend Components

#### Pages

**Home Page (`/`)**
- Landing page with navigation cards
- Overview of platform features
- Quick access to all major sections

**Universe Manager (`/universes`)**
- List view of all universes
- Create/delete universe functionality
- Navigation to universe detail pages
- Real-time ticker count display

**Universe Detail (`/universes/{id}`)**
- Manage tickers within a specific universe
- Add/remove tickers with validation
- Real-time validation feedback
- Save changes with confirmation

#### Features

**Ticker Validation**
- Real-time validation using yfinance
- Visual indicators (✅/❌) for valid/invalid tickers
- Company name display for valid tickers
- Error messages for invalid tickers
- Batch validation with progress indicators

**User Experience**
- Confirmation dialogs for destructive actions
- Loading states and error handling
- Responsive design with Material-UI
- Intuitive navigation and breadcrumbs

## Usage

### Setting Up the Database

1. Run the database setup script (includes universe tables):
```bash
python scripts/setup_database.py
```

2. Install additional dependencies:
```bash
pip install yfinance==0.2.28
```

### Creating a Universe

1. Navigate to the Universe Manager page
2. Click "Create Universe"
3. Enter universe name and optional description
4. Click "Create" to save

### Managing Tickers

1. Click on a universe to open its detail page
2. Add tickers by typing in the input field
3. Click "Validate Tickers" to check validity
4. Review validation results
5. Click "Save Changes" to update the universe

### Ticker Validation

The system validates tickers by:
- Checking if the ticker exists in yfinance
- Retrieving company information
- Providing detailed error messages for invalid tickers
- Supporting batch validation for multiple tickers

## API Examples

### Create Universe
```bash
curl -X POST "http://localhost:8000/api/universes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "S&P 500 Tech",
    "description": "Technology stocks from S&P 500"
  }'
```

### Add Tickers
```bash
curl -X PUT "http://localhost:8000/api/universes/1/tickers" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"]
  }'
```

### Validate Tickers
```bash
curl -X POST "http://localhost:8000/api/tickers/validate" \
  -H "Content-Type: application/json" \
  -d '["AAPL", "INVALID", "MSFT"]'
```

## Error Handling

The system provides comprehensive error handling:

- **Database Errors**: Proper error messages for constraint violations
- **Validation Errors**: Clear feedback for invalid ticker symbols
- **Network Errors**: Graceful handling of API failures
- **User Input**: Validation of required fields and formats

## Security Considerations

- Input sanitization for ticker symbols
- SQL injection prevention through parameterized queries
- Rate limiting for ticker validation API
- Proper error messages without sensitive information

## Performance Optimizations

- Concurrent ticker validation using ThreadPoolExecutor
- Batch processing for multiple tickers
- Database indexing on frequently queried fields
- Efficient pagination for large universe lists

## Future Enhancements

- Bulk import/export functionality
- Universe templates and presets
- Advanced filtering and search
- Integration with more data providers
- Historical ticker data tracking
- Universe performance analytics
