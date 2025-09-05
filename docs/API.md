# Alpha Crucible Quant API Documentation

## Overview

The Alpha Crucible Quant API provides RESTful endpoints for accessing backtest data, portfolio information, signal scores, and performance metrics. The API is built with FastAPI and provides automatic OpenAPI documentation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `http://your-domain.com`

## Authentication

Currently, the API does not require authentication. In production, consider implementing API key authentication or OAuth2.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": { ... },
  "message": "Success",
  "status": 200
}
```

### Error Response
```json
{
  "error": "Error Type",
  "message": "Error description",
  "details": "Additional error details"
}
```

## Endpoints

### Backtests

#### Get All Backtests
```http
GET /api/backtests?page=1&size=50
```

**Query Parameters:**
- `page` (optional): Page number (default: 1, min: 1)
- `size` (optional): Page size (default: 50, min: 1, max: 100)

**Response:**
```json
{
  "backtests": [
    {
      "run_id": "backtest_123",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "tickers": ["AAPL", "MSFT", "GOOGL"],
      "signals": ["RSI", "SMA", "MACD"],
      "total_return": 0.152,
      "annualized_return": 0.145,
      "sharpe_ratio": 1.25,
      "max_drawdown": -0.08,
      "volatility": 0.18,
      "alpha": 0.021,
      "information_ratio": 0.85,
      "execution_time_seconds": 45.2,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 50,
  "total_pages": 1
}
```

#### Get Specific Backtest
```http
GET /api/backtests/{run_id}
```

**Path Parameters:**
- `run_id`: Unique identifier for the backtest

**Response:**
```json
{
  "run_id": "backtest_123",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "signals": ["RSI", "SMA", "MACD"],
  "total_return": 0.152,
  "annualized_return": 0.145,
  "sharpe_ratio": 1.25,
  "max_drawdown": -0.08,
  "volatility": 0.18,
  "alpha": 0.021,
  "information_ratio": 0.85,
  "execution_time_seconds": 45.2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Backtest Metrics
```http
GET /api/backtests/{run_id}/metrics
```

**Response:**
```json
{
  "run_id": "backtest_123",
  "metrics": {
    "total_return": 0.152,
    "annualized_return": 0.145,
    "sharpe_ratio": 1.25,
    "max_drawdown": -0.08,
    "volatility": 0.18,
    "alpha": 0.021,
    "information_ratio": 0.85,
    "beta": 0.95,
    "calmar_ratio": 1.81,
    "sortino_ratio": 1.89
  }
}
```

#### Get Backtest Portfolios
```http
GET /api/backtests/{run_id}/portfolios
```

**Response:**
```json
{
  "portfolios": [
    {
      "portfolio_id": 1,
      "creation_date": "2024-01-01",
      "weights": {
        "AAPL": 0.3,
        "MSFT": 0.4,
        "GOOGL": 0.3
      },
      "signal_weights": {
        "RSI": 0.4,
        "SMA": 0.4,
        "MACD": 0.2
      },
      "risk_aversion": 0.5,
      "max_weight": 0.1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "run_id": "backtest_123"
}
```

#### Get Backtest Signals
```http
GET /api/backtests/{run_id}/signals?start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "signals": [
    {
      "ticker": "AAPL",
      "signal_id": "RSI",
      "date": "2024-01-01",
      "score": 0.5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "run_id": "backtest_123",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

#### Get Backtest Scores
```http
GET /api/backtests/{run_id}/scores?start_date=2024-01-01&end_date=2024-01-31
```

**Response:**
```json
{
  "scores": [
    {
      "ticker": "AAPL",
      "date": "2024-01-01",
      "combined_score": 0.45,
      "signal_scores": {
        "RSI": 0.5,
        "SMA": 0.4,
        "MACD": 0.5
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "run_id": "backtest_123",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### Portfolios

#### Get Portfolio Details
```http
GET /api/portfolios/{portfolio_id}
```

**Path Parameters:**
- `portfolio_id`: Unique identifier for the portfolio

**Response:**
```json
{
  "portfolio_id": 1,
  "creation_date": "2024-01-01",
  "weights": {
    "AAPL": 0.3,
    "MSFT": 0.4,
    "GOOGL": 0.3
  },
  "signal_weights": {
    "RSI": 0.4,
    "SMA": 0.4,
    "MACD": 0.2
  },
  "risk_aversion": 0.5,
  "max_weight": 0.1,
  "positions": [
    {
      "ticker": "AAPL",
      "weight": 0.3,
      "alpha_score": 0.5
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Portfolio Positions
```http
GET /api/portfolios/{portfolio_id}/positions
```

**Response:**
```json
{
  "positions": [
    {
      "ticker": "AAPL",
      "weight": 0.3,
      "alpha_score": 0.5
    },
    {
      "ticker": "MSFT",
      "weight": 0.4,
      "alpha_score": 0.3
    }
  ],
  "total": 2,
  "portfolio_id": 1
}
```

### Signals

#### Get Raw Signals
```http
GET /api/signals?tickers=AAPL,MSFT&signal_names=RSI,SMA&start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `tickers` (optional): Comma-separated list of tickers
- `signal_names` (optional): Comma-separated list of signal names
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "signals": [
    {
      "ticker": "AAPL",
      "signal_id": "RSI",
      "date": "2024-01-01",
      "score": 0.5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "filters": {
    "tickers": ["AAPL", "MSFT"],
    "signal_names": ["RSI", "SMA"],
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

#### Get Combined Scores
```http
GET /api/scores?tickers=AAPL,MSFT&methods=equal_weight&start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `tickers` (optional): Comma-separated list of tickers
- `methods` (optional): Comma-separated list of combination methods
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "scores": [
    {
      "ticker": "AAPL",
      "date": "2024-01-01",
      "combined_score": 0.45,
      "method": "equal_weight",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "filters": {
    "tickers": ["AAPL", "MSFT"],
    "methods": ["equal_weight"],
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

### NAV (Net Asset Value)

#### Get Backtest NAV Data
```http
GET /api/backtests/{run_id}/nav?start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "nav_data": [
    {
      "nav_date": "2024-01-01",
      "portfolio_value": 10000.0,
      "benchmark_value": 10000.0,
      "portfolio_return": 0.0,
      "benchmark_return": 0.0,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "run_id": "backtest_123",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing rate limiting to prevent abuse.

## Examples

### Python Client

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api"

# Get all backtests
response = requests.get(f"{BASE_URL}/backtests")
backtests = response.json()

# Get specific backtest
backtest_id = "backtest_123"
response = requests.get(f"{BASE_URL}/backtests/{backtest_id}")
backtest = response.json()

# Get backtest NAV data
response = requests.get(f"{BASE_URL}/backtests/{backtest_id}/nav")
nav_data = response.json()

# Get portfolio details
portfolio_id = 1
response = requests.get(f"{BASE_URL}/portfolios/{portfolio_id}")
portfolio = response.json()
```

### JavaScript Client

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Get all backtests
const getBacktests = async () => {
  const response = await fetch(`${BASE_URL}/backtests`);
  return await response.json();
};

// Get specific backtest
const getBacktest = async (runId) => {
  const response = await fetch(`${BASE_URL}/backtests/${runId}`);
  return await response.json();
};

// Get backtest NAV data
const getBacktestNav = async (runId, startDate, endDate) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  const response = await fetch(`${BASE_URL}/backtests/${runId}/nav?${params}`);
  return await response.json();
};
```

### cURL Examples

```bash
# Get all backtests
curl -X GET "http://localhost:8000/api/backtests"

# Get specific backtest
curl -X GET "http://localhost:8000/api/backtests/backtest_123"

# Get backtest NAV data
curl -X GET "http://localhost:8000/api/backtests/backtest_123/nav?start_date=2024-01-01&end_date=2024-01-31"

# Get portfolio details
curl -X GET "http://localhost:8000/api/portfolios/1"
```

## Interactive Documentation

The API provides interactive documentation that you can use to test endpoints:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

These interfaces allow you to:
- Browse all available endpoints
- View request/response schemas
- Test endpoints directly from the browser
- Download OpenAPI specification

## Data Models

### Backtest
```json
{
  "run_id": "string",
  "start_date": "date",
  "end_date": "date",
  "tickers": ["string"],
  "signals": ["string"],
  "total_return": "number",
  "annualized_return": "number",
  "sharpe_ratio": "number",
  "max_drawdown": "number",
  "volatility": "number",
  "alpha": "number",
  "information_ratio": "number",
  "execution_time_seconds": "number",
  "created_at": "datetime"
}
```

### Portfolio
```json
{
  "portfolio_id": "integer",
  "creation_date": "date",
  "weights": "object",
  "signal_weights": "object",
  "risk_aversion": "number",
  "max_weight": "number",
  "positions": [
    {
      "ticker": "string",
      "weight": "number",
      "alpha_score": "number"
    }
  ],
  "created_at": "datetime"
}
```

### Signal Score
```json
{
  "ticker": "string",
  "signal_id": "string",
  "date": "date",
  "score": "number",
  "created_at": "datetime"
}
```

### NAV Data
```json
{
  "nav_date": "date",
  "portfolio_value": "number",
  "benchmark_value": "number",
  "portfolio_return": "number",
  "benchmark_return": "number",
  "created_at": "datetime"
}
```

## Best Practices

1. **Use Pagination**: For large datasets, use pagination parameters
2. **Filter Data**: Use query parameters to filter results
3. **Handle Errors**: Always check response status codes
4. **Cache Responses**: Cache frequently accessed data
5. **Rate Limiting**: Implement appropriate delays between requests
6. **Data Validation**: Validate data before sending requests

## Support

For API support and questions:
1. Check the interactive documentation
2. Review the error messages
3. Check the server logs
4. Contact the development team
