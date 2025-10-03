#!/usr/bin/env python3
"""
Comprehensive test runner for the Alpha Crucible Quant financial investment system.

This script runs all tests to validate the system's robustness and production readiness.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_test_suite(test_path, description):
    """Run a test suite and return results."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', test_path, '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Duration: {duration:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        
        return result.returncode == 0, duration
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, 0


def main():
    """Run all comprehensive tests."""
    print("🚀 Starting Comprehensive Test Suite for Alpha Crucible Quant")
    print("=" * 80)
    
    # Define test suites
    test_suites = [
        ("tests/unit/solver/test_solver_config.py", "Solver Configuration Tests"),
        ("tests/unit/solver/test_portfolio_models.py", "Portfolio Model Tests"),
        ("tests/unit/solver/test_portfolio_solver.py", "Portfolio Solver Tests"),
        ("tests/unit/signals/test_signal_registry.py", "Signal Registry Tests"),
        ("tests/unit/signals/test_signal_reader.py", "Signal Reader Tests"),
        ("tests/integration/test_end_to_end.py", "End-to-End Integration Tests"),
        ("tests/integration/test_system_robustness.py", "System Robustness Tests"),
    ]
    
    # Run all test suites
    results = []
    total_duration = 0
    
    for test_path, description in test_suites:
        success, duration = run_test_suite(test_path, description)
        results.append((description, success, duration))
        total_duration += duration
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    failed = 0
    
    for description, success, duration in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {description} ({duration:.2f}s)")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 RESULTS:")
    print(f"  Total test suites: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total duration: {total_duration:.2f} seconds")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is production ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test suite(s) failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
