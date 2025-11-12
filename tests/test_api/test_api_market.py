"""
Tests for Market Data API endpoints.

Tests market data retrieval endpoints with mocked yfinance.
"""

import pytest
from datetime import date, timedelta
from fastapi import status
import pandas as pd


class TestMarketAuthentication:
    """Test API key authentication for market endpoints."""
    
    def test_get_market_data_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/market-data/AAPL")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestMarketDataEndpoints:
    """Test market data endpoints with mocked yfinance."""
    
    def test_get_market_data(self, authenticated_client, mock_yfinance):
        """Test getting market data for a symbol."""
        # Setup mock return value
        mock_ticker = mock_yfinance.return_value
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        mock_ticker.history.return_value = pd.DataFrame({
            'Open': [100.0] * 10,
            'High': [105.0] * 10,
            'Low': [95.0] * 10,
            'Close': [102.0] * 10,
            'Volume': [1000000] * 10
        }, index=dates)
        
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() - timedelta(days=1)
        response = authenticated_client.get(
            f"/api/market-data/AAPL?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "symbol" in data
        assert "data" in data
        assert "total_points" in data
    
    def test_get_market_data_invalid_symbol(self, authenticated_client):
        """Test getting market data for invalid symbol."""
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() - timedelta(days=1)
        response = authenticated_client.get(
            f"/api/market-data/INVALID123?start_date={start_date}&end_date={end_date}"
        )
        # Should return 400 for invalid ticker format
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_get_normalized_market_data(self, authenticated_client, mock_yfinance):
        """Test getting normalized market data."""
        mock_ticker = mock_yfinance.return_value
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        mock_ticker.history.return_value = pd.DataFrame({
            'Open': [100.0] * 10,
            'High': [105.0] * 10,
            'Low': [95.0] * 10,
            'Close': [102.0] * 10,
            'Volume': [1000000] * 10
        }, index=dates)
        
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() - timedelta(days=1)
        response = authenticated_client.get(
            f"/api/market-data/AAPL/normalized?start_date={start_date}&end_date={end_date}&start_value=100.0"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "symbol" in data
        assert "data" in data
        assert "start_value" in data
    
    def test_get_live_price(self, authenticated_client, mock_yfinance):
        """Test getting live price for a symbol."""
        response = authenticated_client.get("/api/market-data/live/AAPL")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "symbol" in data
        assert "price" in data
        assert "previous_close" in data
        assert "daily_change" in data
    
    def test_get_live_price_invalid_symbol(self, authenticated_client):
        """Test getting live price for invalid symbol."""
        response = authenticated_client.get("/api/market-data/live/INVALID123")
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_get_live_prices_batch(self, authenticated_client, mock_yfinance):
        """Test getting live prices for multiple tickers."""
        tickers = ["AAPL", "MSFT"]
        response = authenticated_client.post("/api/market-data/live/batch", json=tickers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == len(tickers)
    
    def test_get_intraday_price_data(self, authenticated_client, mock_yfinance):
        """Test getting intraday price data."""
        # Setup mock for intraday data
        mock_ticker = mock_yfinance.return_value
        dates = pd.date_range(start='2024-01-01 09:30', periods=78, freq='5min')
        mock_ticker.history.return_value = pd.DataFrame({
            'Open': [100.0] * 78,
            'High': [105.0] * 78,
            'Low': [95.0] * 78,
            'Close': [102.0] * 78,
            'Volume': [100000] * 78
        }, index=dates)
        
        response = authenticated_client.get("/api/market-data/AAPL/intraday")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "symbol" in data
        assert "data" in data
        assert "interval" in data

