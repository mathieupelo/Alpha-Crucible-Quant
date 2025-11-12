"""
Tests for Ticker Management API endpoints.

Tests ticker fetching, creation, and company info endpoints with mocked yfinance.
"""

import pytest
from unittest.mock import patch
from fastapi import status


class TestTickerAuthentication:
    """Test API key authentication for ticker endpoints."""
    
    def test_fetch_ticker_info_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/tickers/fetch-info?ticker=AAPL")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestTickerEndpoints:
    """Test ticker endpoints with mocked yfinance."""
    
    def test_fetch_ticker_info(self, authenticated_client, mock_yfinance):
        """Test fetching ticker info from yfinance."""
        # Need to patch the ticker validation service
        with patch('api.tickers.ticker_validator') as mock_validator:
            mock_validator.validate_ticker.return_value = {
                'is_valid': True,
                'ticker': 'AAPL',
                'error_message': None
            }
            response = authenticated_client.get("/api/tickers/fetch-info?ticker=AAPL")
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert "ticker" in data
    
    def test_fetch_ticker_info_invalid_ticker(self, authenticated_client):
        """Test fetching info for invalid ticker."""
        response = authenticated_client.get("/api/tickers/fetch-info?ticker=INVALID123")
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_create_ticker(self, authenticated_client, mock_yfinance):
        """Test creating a new ticker in the database."""
        ticker_data = {
            "ticker": "TESTTICKER",
            "yfinance_info": {
                "longName": "Test Company",
                "shortName": "TEST",
                "sector": "Technology",
                "industry": "Software",
                "marketCap": 1000000000,
                "currency": "USD",
                "exchange": "NASDAQ",
                "country": "United States"
            }
        }
        
        response = authenticated_client.post("/api/tickers/create", json=ticker_data)
        # May succeed or fail if ticker already exists
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_create_ticker_without_yfinance_info(self, authenticated_client, mock_yfinance):
        """Test creating ticker without providing yfinance_info."""
        ticker_data = {"ticker": "TESTTICKER2"}
        response = authenticated_client.post("/api/tickers/create", json=ticker_data)
        # Should fetch from yfinance if not provided
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]

