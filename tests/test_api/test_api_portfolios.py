"""
Tests for Portfolio API endpoints.

Tests portfolio retrieval, positions, signals, and scores endpoints.
"""

import pytest
from fastapi import status


class TestPortfolioAuthentication:
    """Test API key authentication for portfolio endpoints."""
    
    def test_get_portfolio_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/portfolios/1")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestPortfolioEndpoints:
    """Test portfolio endpoints."""
    
    def test_get_portfolio_not_found(self, authenticated_client):
        """Test getting non-existent portfolio returns 404."""
        response = authenticated_client.get("/api/portfolios/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_portfolio_positions_not_found(self, authenticated_client):
        """Test getting positions for non-existent portfolio."""
        response = authenticated_client.get("/api/portfolios/999999/positions")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_portfolio_signals_not_found(self, authenticated_client):
        """Test getting signals for non-existent portfolio."""
        response = authenticated_client.get("/api/portfolios/999999/signals")
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_get_portfolio_scores_not_found(self, authenticated_client):
        """Test getting scores for non-existent portfolio."""
        response = authenticated_client.get("/api/portfolios/999999/scores")
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_get_portfolio_universe_tickers_not_found(self, authenticated_client):
        """Test getting universe tickers for non-existent portfolio."""
        response = authenticated_client.get("/api/portfolios/999999/universe-tickers")
        assert response.status_code == status.HTTP_404_NOT_FOUND

