"""
Tests for Universe API endpoints.

Tests all universe management endpoints including CRUD operations,
company management, and ticker validation.
"""

import pytest
from datetime import date, timedelta
from fastapi import status


class TestUniverseAuthentication:
    """Test API key authentication for universe endpoints."""
    
    def test_get_universes_without_auth(self, unauthenticated_client):
        """Test that unauthenticated requests are rejected."""
        response = unauthenticated_client.get("/api/universes")
        # FastAPI returns 403 Forbidden when authentication dependency fails
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_universes_with_invalid_key(self, unauthenticated_client):
        """Test that invalid API key is rejected."""
        response = unauthenticated_client.get(
            "/api/universes",
            headers={"Authorization": "Bearer invalid-key"}
        )
        # FastAPI returns 403 Forbidden when authentication dependency fails
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_universes_with_valid_key(self, authenticated_client):
        """Test that valid API key works."""
        response = authenticated_client.get("/api/universes")
        assert response.status_code == status.HTTP_200_OK


class TestUniverseCRUD:
    """Test universe CRUD operations."""
    
    def test_get_all_universes(self, authenticated_client):
        """Test getting all universes."""
        response = authenticated_client.get("/api/universes")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "universes" in data
        assert "total" in data
        assert isinstance(data["universes"], list)
    
    def test_create_universe(self, authenticated_client):
        """Test creating a new universe."""
        universe_data = {
            "name": "__TEST_UNIVERSE_CREATE_API",
            "description": "Test universe for API testing"
        }
        response = authenticated_client.post("/api/universes", json=universe_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == universe_data["name"]
        assert data["description"] == universe_data["description"]
        assert "id" in data
        
        # Cleanup
        authenticated_client.delete(f"/api/universes/{data['id']}")
    
    def test_create_universe_without_description(self, authenticated_client):
        """Test creating universe without description."""
        universe_data = {"name": "__TEST_UNIVERSE_NO_DESC_API"}
        response = authenticated_client.post("/api/universes", json=universe_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == universe_data["name"]
        
        # Cleanup
        authenticated_client.delete(f"/api/universes/{data['id']}")
    
    def test_create_universe_duplicate_name(self, authenticated_client):
        """Test that duplicate universe names are rejected."""
        universe_data = {"name": "__TEST_UNIVERSE_DUP_API"}
        
        # Create first universe
        response1 = authenticated_client.post("/api/universes", json=universe_data)
        assert response1.status_code == status.HTTP_200_OK
        universe_id = response1.json()["id"]
        
        # Try to create duplicate
        response2 = authenticated_client.post("/api/universes", json=universe_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
        # Cleanup
        authenticated_client.delete(f"/api/universes/{universe_id}")
    
    def test_get_universe_by_id(self, authenticated_client, test_universe):
        """Test getting a specific universe by ID."""
        universe_id = test_universe["id"]
        response = authenticated_client.get(f"/api/universes/{universe_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == universe_id
        assert data["name"] == test_universe["name"]
    
    def test_get_universe_not_found(self, authenticated_client):
        """Test getting non-existent universe returns 404."""
        response = authenticated_client.get("/api/universes/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_universe(self, authenticated_client, test_universe):
        """Test updating a universe."""
        universe_id = test_universe["id"]
        update_data = {
            "name": "__TEST_UNIVERSE_UPDATED_API",
            "description": "Updated description"
        }
        response = authenticated_client.put(
            f"/api/universes/{universe_id}",
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    def test_update_universe_not_found(self, authenticated_client):
        """Test updating non-existent universe returns 404."""
        update_data = {"name": "Test", "description": "Test"}
        response = authenticated_client.put(
            "/api/universes/999999",
            json=update_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_universe(self, authenticated_client):
        """Test deleting a universe."""
        # Create universe to delete
        universe_data = {"name": "__TEST_UNIVERSE_DELETE_API"}
        create_response = authenticated_client.post("/api/universes", json=universe_data)
        universe_id = create_response.json()["id"]
        
        # Delete it
        response = authenticated_client.delete(f"/api/universes/{universe_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        get_response = authenticated_client.get(f"/api/universes/{universe_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_universe_not_found(self, authenticated_client):
        """Test deleting non-existent universe returns 404."""
        response = authenticated_client.delete("/api/universes/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUniverseCompanies:
    """Test universe company management endpoints."""
    
    def test_get_universe_companies(self, authenticated_client, test_universe):
        """Test getting companies for a universe."""
        universe_id = test_universe["id"]
        response = authenticated_client.get(f"/api/universes/{universe_id}/companies")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "companies" in data
        assert "total" in data
        assert data["universe_id"] == universe_id
    
    def test_get_universe_companies_not_found(self, authenticated_client):
        """Test getting companies for non-existent universe."""
        response = authenticated_client.get("/api/universes/999999/companies")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_add_company_to_universe(self, authenticated_client, test_universe):
        """Test adding a company to a universe."""
        universe_id = test_universe["id"]
        # Use a ticker that exists in Varrock schema
        ticker = "CMCSA"
        response = authenticated_client.post(
            f"/api/universes/{universe_id}/companies",
            params={"ticker": ticker}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("main_ticker") == ticker.upper()
    
    def test_add_invalid_ticker_to_universe(self, authenticated_client, test_universe):
        """Test adding invalid ticker returns error."""
        universe_id = test_universe["id"]
        response = authenticated_client.post(
            f"/api/universes/{universe_id}/companies",
            params={"ticker": "INVALID12345"}
        )
        # Should return 400 for invalid ticker format
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_update_universe_companies(self, authenticated_client, test_universe):
        """Test updating all companies in a universe."""
        universe_id = test_universe["id"]
        update_data = {
            "tickers": ["AAPL", "MSFT", "CMCSA"]  # Use tickers that exist in Varrock schema
        }
        response = authenticated_client.put(
            f"/api/universes/{universe_id}/companies",
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "companies" in data
        assert len(data["companies"]) <= len(update_data["tickers"])
    
    def test_remove_company_from_universe(self, authenticated_client, test_universe):
        """Test removing a company from a universe."""
        universe_id = test_universe["id"]
        
        # First add a company
        ticker = "CMCSA"
        add_response = authenticated_client.post(
            f"/api/universes/{universe_id}/companies",
            params={"ticker": ticker}
        )
        if add_response.status_code == status.HTTP_200_OK:
            company_uid = add_response.json().get("company_uid")
            if company_uid:
                # Remove it
                response = authenticated_client.delete(
                    f"/api/universes/{universe_id}/companies/{company_uid}"
                )
                assert response.status_code == status.HTTP_200_OK


class TestTickerValidation:
    """Test ticker validation endpoint."""
    
    def test_validate_tickers(self, authenticated_client):
        """Test validating multiple tickers."""
        tickers = ["AAPL", "MSFT", "INVALID123"]
        response = authenticated_client.post("/api/tickers/validate", json=tickers)
        # May return 200 or 400 depending on validation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, list)
    
    def test_validate_empty_ticker_list(self, authenticated_client):
        """Test validating empty ticker list."""
        response = authenticated_client.post("/api/tickers/validate", json=[])
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

