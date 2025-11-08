"""
Tests for universe creation functionality.

These tests verify that universes can be created correctly.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.database_service import DatabaseService

# Test universe name - will be created and cleaned up
TEST_UNIVERSE_NAME = "__TEST_UNIVERSE_CREATE__"


@pytest.fixture(autouse=True)
def cleanup_test_universe():
    """Clean up test universe before and after each test."""
    db_service = DatabaseService()
    if db_service.ensure_connection():
        # Try to find and delete test universe
        universes = db_service.get_all_universes()
        for universe in universes:
            if universe['name'] == TEST_UNIVERSE_NAME:
                db_service.delete_universe(universe['id'])
                break
    
    yield
    
    # Cleanup after test
    if db_service.ensure_connection():
        universes = db_service.get_all_universes()
        for universe in universes:
            if universe['name'] == TEST_UNIVERSE_NAME:
                db_service.delete_universe(universe['id'])
                break


def test_create_universe_basic():
    """Test basic universe creation."""
    db_service = DatabaseService()
    assert db_service.ensure_connection(), "Failed to connect to database"
    
    # Create universe
    universe = db_service.create_universe(
        name=TEST_UNIVERSE_NAME,
        description="Test universe for creation"
    )
    
    assert universe is not None
    assert universe['name'] == TEST_UNIVERSE_NAME
    assert universe['description'] == "Test universe for creation"
    assert universe['ticker_count'] == 0
    assert 'id' in universe
    assert universe['id'] > 0


def test_create_universe_without_description():
    """Test universe creation without description."""
    db_service = DatabaseService()
    assert db_service.ensure_connection(), "Failed to connect to database"
    
    # Create universe without description
    universe = db_service.create_universe(name=TEST_UNIVERSE_NAME)
    
    assert universe is not None
    assert universe['name'] == TEST_UNIVERSE_NAME
    assert universe.get('description') is None or universe['description'] == ""
    assert universe['ticker_count'] == 0


def test_create_universe_duplicate_name():
    """Test that creating a universe with duplicate name fails."""
    db_service = DatabaseService()
    assert db_service.ensure_connection(), "Failed to connect to database"
    
    # Create first universe
    universe1 = db_service.create_universe(name=TEST_UNIVERSE_NAME)
    assert universe1 is not None
    
    # Try to create duplicate - should raise ValueError
    with pytest.raises(ValueError, match="already exists"):
        db_service.create_universe(name=TEST_UNIVERSE_NAME)


def test_get_universe_after_creation():
    """Test that we can retrieve a universe after creating it."""
    db_service = DatabaseService()
    assert db_service.ensure_connection(), "Failed to connect to database"
    
    # Create universe
    created_universe = db_service.create_universe(
        name=TEST_UNIVERSE_NAME,
        description="Test description"
    )
    universe_id = created_universe['id']
    
    # Retrieve universe
    retrieved_universe = db_service.get_universe_by_id(universe_id)
    
    assert retrieved_universe is not None
    assert retrieved_universe['id'] == universe_id
    assert retrieved_universe['name'] == TEST_UNIVERSE_NAME
    assert retrieved_universe['description'] == "Test description"

