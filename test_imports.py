#!/usr/bin/env python3
"""
Test script to verify imports work correctly in the backend directory structure.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing imports...")
    
    # Test main imports
    from api import backtests, portfolios, signals, nav, universes, market
    print("[OK] API imports successful")
    
    from models import ErrorResponse
    print("[OK] Models imports successful")
    
    from security.input_validation import validate_ticker
    print("[OK] Security imports successful")
    
    from services.database_service import DatabaseService
    print("[OK] Services imports successful")
    
    print("\n[SUCCESS] All imports successful! The backend should work correctly.")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("\nThis indicates there are still import path issues.")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)
