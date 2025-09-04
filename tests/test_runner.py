#!/usr/bin/env python3
"""
Test runner for the Quant Project system.

Runs all tests with comprehensive coverage reporting.
"""

import sys
import os
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def main():
    """Run all tests with coverage reporting."""
    print("Quant Project - Test Runner")
    print("=" * 50)
    
    # Test directory
    test_dir = Path(__file__).parent
    
    # Run tests with coverage
    args = [
        str(test_dir),
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--cov=src',  # Coverage for src directory
        '--cov-report=html',  # HTML coverage report
        '--cov-report=term-missing',  # Terminal coverage report
        '--cov-fail-under=80',  # Fail if coverage < 80%
        '--maxfail=5',  # Stop after 5 failures
        '--durations=10',  # Show 10 slowest tests
    ]
    
    print("Running tests with coverage...")
    print(f"Test directory: {test_dir}")
    print(f"Coverage target: src/")
    print()
    
    try:
        exit_code = pytest.main(args)
        
        if exit_code == 0:
            print("\n" + "=" * 50)
            print("ALL TESTS PASSED! ✓")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("SOME TESTS FAILED! ✗")
            print("=" * 50)
        
        return exit_code
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
