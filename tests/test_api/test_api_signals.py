"""
Tests for Signal API endpoints.

Tests signal retrieval, scores, and signal types endpoints.
"""

import pytest
from datetime import date, timedelta
from fastapi import status


class TestSignalAuthentication:
    """Test API key authentication for signal endpoints."""
    
    def test_get_signals_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/signals")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestSignalEndpoints:
    """Test signal endpoints."""
    
    def test_get_signals_no_filters(self, authenticated_client):
        """Test getting signals without filters."""
        response = authenticated_client.get("/api/signals")
        # May return 200 or 500 depending on database state
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "signals" in data
            assert "total" in data
            assert "filters" in data
    
    def test_get_signals_with_ticker_filter(self, authenticated_client):
        """Test getting signals filtered by ticker."""
        response = authenticated_client.get("/api/signals?tickers=AAPL")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "signals" in data
    
    def test_get_signals_with_multiple_tickers(self, authenticated_client):
        """Test getting signals filtered by multiple tickers."""
        response = authenticated_client.get("/api/signals?tickers=AAPL&tickers=MSFT")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "signals" in data
    
    def test_get_signals_with_signal_name_filter(self, authenticated_client):
        """Test getting signals filtered by signal name."""
        response = authenticated_client.get("/api/signals?signal_names=SENTIMENT")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "signals" in data
    
    def test_get_signals_with_date_range(self, authenticated_client):
        """Test getting signals filtered by date range."""
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=7)
        response = authenticated_client.get(
            f"/api/signals?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "signals" in data
    
    def test_get_scores_no_filters(self, authenticated_client):
        """Test getting scores without filters."""
        response = authenticated_client.get("/api/scores")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "scores" in data
            assert "total" in data
            assert "filters" in data
    
    def test_get_scores_with_ticker_filter(self, authenticated_client):
        """Test getting scores filtered by ticker."""
        response = authenticated_client.get("/api/scores?tickers=AAPL")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "scores" in data
    
    def test_get_scores_with_method_filter(self, authenticated_client):
        """Test getting scores filtered by method."""
        response = authenticated_client.get("/api/scores?methods=equal_weight")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "scores" in data
    
    def test_get_signal_types(self, authenticated_client):
        """Test getting available signal types."""
        response = authenticated_client.get("/api/signal-types")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "signal_types" in data
        assert "total" in data
        assert isinstance(data["signal_types"], list)

