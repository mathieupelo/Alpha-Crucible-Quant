"""
Tests for Backtest API endpoints.

Tests all backtest-related endpoints including creation, retrieval,
metrics, portfolios, signals, and deletion.
"""

import pytest
from datetime import date, timedelta
from fastapi import status


class TestBacktestAuthentication:
    """Test API key authentication for backtest endpoints."""
    
    def test_get_backtests_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/backtests")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_create_backtest_without_auth(self, unauthenticated_client):
        """Test that creating backtest without auth is rejected."""
        response = unauthenticated_client.post("/api/backtests", json={})
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestBacktestCRUD:
    """Test backtest CRUD operations."""
    
    def test_get_all_backtests(self, authenticated_client):
        """Test getting all backtests with pagination."""
        response = authenticated_client.get("/api/backtests?page=1&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "backtests" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    def test_get_backtests_pagination(self, authenticated_client):
        """Test backtest pagination."""
        response = authenticated_client.get("/api/backtests?page=1&size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["size"] == 5
    
    def test_get_backtest_by_id(self, authenticated_client, test_universe):
        """Test getting a specific backtest by run_id."""
        # First create a backtest
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_GET_API",
            "initial_capital": 10000.0,
            "rebalancing_frequency": "monthly"
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Get the backtest
            response = authenticated_client.get(f"/api/backtests/{run_id}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["run_id"] == run_id
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")
    
    def test_get_backtest_not_found(self, authenticated_client):
        """Test getting non-existent backtest returns 404."""
        response = authenticated_client.get("/api/backtests/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_check_backtest_name(self, authenticated_client):
        """Test checking if backtest name exists."""
        name = "__TEST_CHECK_NAME_API"
        response = authenticated_client.get(f"/api/backtests/check-name?name={name}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "exists" in data
        assert "available" in data
    
    def test_create_backtest(self, authenticated_client, test_universe):
        """Test creating a new backtest."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_CREATE_API",
            "initial_capital": 10000.0,
            "rebalancing_frequency": "monthly"
        }
        
        response = authenticated_client.post("/api/backtests", json=backtest_data)
        # May succeed or fail depending on data availability
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "run_id" in data
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{data['run_id']}")
    
    def test_create_backtest_invalid_universe(self, authenticated_client):
        """Test creating backtest with invalid universe."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": 999999,
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_INVALID_UNIVERSE_API"
        }
        
        response = authenticated_client.post("/api/backtests", json=backtest_data)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_create_backtest_duplicate_name(self, authenticated_client, test_universe):
        """Test that duplicate backtest names are rejected."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_DUP_API",
            "initial_capital": 10000.0
        }
        
        # Create first backtest
        response1 = authenticated_client.post("/api/backtests", json=backtest_data)
        if response1.status_code == status.HTTP_200_OK:
            run_id = response1.json()["run_id"]
            
            # Try to create duplicate
            response2 = authenticated_client.post("/api/backtests", json=backtest_data)
            assert response2.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")
    
    def test_delete_backtest(self, authenticated_client, test_universe):
        """Test deleting a backtest."""
        # Create backtest to delete
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_DELETE_API",
            "initial_capital": 10000.0
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Delete it
            response = authenticated_client.delete(f"/api/backtests/{run_id}")
            assert response.status_code == status.HTTP_200_OK
            
            # Verify it's deleted
            get_response = authenticated_client.get(f"/api/backtests/{run_id}")
            assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_backtest_not_found(self, authenticated_client):
        """Test deleting non-existent backtest returns 404."""
        response = authenticated_client.delete("/api/backtests/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBacktestDetails:
    """Test backtest detail endpoints."""
    
    def test_get_backtest_metrics(self, authenticated_client, test_universe):
        """Test getting backtest metrics."""
        # Create a backtest first
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_METRICS_API",
            "initial_capital": 10000.0
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Get metrics
            response = authenticated_client.get(f"/api/backtests/{run_id}/metrics")
            # May return 404 if metrics not calculated yet
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")
    
    def test_get_backtest_portfolios(self, authenticated_client, test_universe):
        """Test getting portfolios for a backtest."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_PORTFOLIOS_API",
            "initial_capital": 10000.0
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Get portfolios
            response = authenticated_client.get(f"/api/backtests/{run_id}/portfolios")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "portfolios" in data
            assert "total" in data
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")
    
    def test_get_backtest_signals(self, authenticated_client, test_universe):
        """Test getting signals for a backtest."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_SIGNALS_API",
            "initial_capital": 10000.0
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Get signals
            response = authenticated_client.get(f"/api/backtests/{run_id}/signals")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "signals" in data
            assert "total" in data
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")
    
    def test_get_backtest_scores(self, authenticated_client, test_universe):
        """Test getting scores for a backtest."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_SCORES_API",
            "initial_capital": 10000.0
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Get scores
            response = authenticated_client.get(f"/api/backtests/{run_id}/scores")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "scores" in data
            assert "total" in data
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")
    
    def test_get_backtest_used_signals(self, authenticated_client, test_universe):
        """Test getting used signals for a backtest."""
        backtest_data = {
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today() - timedelta(days=1)),
            "universe_id": test_universe["id"],
            "signals": ["SENTIMENT"],
            "name": "__TEST_BACKTEST_USED_SIGNALS_API",
            "initial_capital": 10000.0
        }
        
        create_response = authenticated_client.post("/api/backtests", json=backtest_data)
        if create_response.status_code == status.HTTP_200_OK:
            run_id = create_response.json()["run_id"]
            
            # Get used signals
            response = authenticated_client.get(f"/api/backtests/{run_id}/used-signals")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "signals" in data
            assert "total" in data
            
            # Cleanup
            authenticated_client.delete(f"/api/backtests/{run_id}")

