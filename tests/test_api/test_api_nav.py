"""
Tests for NAV API endpoints.

Tests NAV (Net Asset Value) data retrieval endpoints.
"""

import pytest
from datetime import date, timedelta
from fastapi import status


class TestNAVAuthentication:
    """Test API key authentication for NAV endpoints."""
    
    def test_get_nav_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/backtests/test-run-id/nav")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestNAVEndpoints:
    """Test NAV endpoints."""
    
    def test_get_nav_not_found(self, authenticated_client):
        """Test getting NAV for non-existent backtest returns 404."""
        response = authenticated_client.get("/api/backtests/non-existent-id/nav")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_nav_with_date_filters(self, authenticated_client):
        """Test getting NAV with date filters."""
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=7)
        response = authenticated_client.get(
            f"/api/backtests/non-existent-id/nav?start_date={start_date}&end_date={end_date}"
        )
        # Should return 404 for non-existent backtest
        assert response.status_code == status.HTTP_404_NOT_FOUND

