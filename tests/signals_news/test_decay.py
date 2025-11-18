#!/usr/bin/env python3
"""
Tests for decay calculation in news signal score calculation.

Note: These tests do not touch the database, so no cleanup is needed.
They only test the calculate_aggregated_sentiment function with mock data.
"""

import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, '.')
from main import calculate_aggregated_sentiment


def test_basic_decay():
    """Test basic decay calculation with known scores."""
    target_date = date(2024, 1, 10)
    
    sentiment_list = [
        {'published_date': date(2024, 1, 10), 'sentiment_score': 1.0},  # Day 0: weight 1.0
        {'published_date': date(2024, 1, 9), 'sentiment_score': 0.5},   # Day 1: weight 0.5
        {'published_date': date(2024, 1, 8), 'sentiment_score': 0.25},  # Day 2: weight 0.25
    ]
    
    result = calculate_aggregated_sentiment(sentiment_list, target_date)
    
    # Expected: (1.0*1.0 + 0.5*0.5 + 0.25*0.25) / (1.0 + 0.5 + 0.25) = 1.3125 / 1.75 ≈ 0.75
    expected = (1.0 * 1.0 + 0.5 * 0.5 + 0.25 * 0.25) / (1.0 + 0.5 + 0.25)
    
    assert abs(result['aggregated_score'] - expected) < 0.0001, \
        f"Expected {expected:.6f}, got {result['aggregated_score']:.6f}"
    assert result['metadata']['weighted_news_count'] == 3
    print("✓ Basic decay calculation test passed")


def test_same_day_news():
    """Test that same-day news gets full weight."""
    target_date = date(2024, 1, 10)
    
    sentiment_list = [
        {'published_date': date(2024, 1, 10), 'sentiment_score': 0.8},
        {'published_date': date(2024, 1, 10), 'sentiment_score': 0.6},
        {'published_date': date(2024, 1, 10), 'sentiment_score': 0.4},
    ]
    
    result = calculate_aggregated_sentiment(sentiment_list, target_date)
    
    # All should have weight 1.0, so simple average
    expected = (0.8 + 0.6 + 0.4) / 3.0
    
    assert abs(result['aggregated_score'] - expected) < 0.0001, \
        f"Expected {expected:.6f}, got {result['aggregated_score']:.6f}"
    assert result['metadata']['total_weight'] == 3.0
    print("✓ Same-day news test passed")


def test_old_news_excluded():
    """Test that news older than window_days is excluded."""
    target_date = date(2024, 1, 10)
    
    sentiment_list = [
        {'published_date': date(2024, 1, 10), 'sentiment_score': 1.0},  # Day 0 - included
        {'published_date': date(2024, 1, 3), 'sentiment_score': 100.0}, # Day 7 - excluded (>= 28 days? No, 7 < 28)
        {'published_date': date(2024, 1, 2), 'sentiment_score': 100.0}, # Day 8 - excluded
        {'published_date': date(2023, 12, 1), 'sentiment_score': 100.0}, # Very old - excluded
    ]
    
    result = calculate_aggregated_sentiment(sentiment_list, target_date, window_days=7)
    
    # Should only include Day 0 (Day 7 and older are excluded with window_days=7)
    assert result['metadata']['weighted_news_count'] == 1, \
        f"Expected 1 news item, got {result['metadata']['weighted_news_count']}"
    assert abs(result['aggregated_score'] - 1.0) < 0.0001, \
        f"Expected 1.0, got {result['aggregated_score']:.6f}"
    print("✓ Old news exclusion test passed")


def test_future_news_excluded():
    """Test that future news is excluded."""
    target_date = date(2024, 1, 10)
    
    sentiment_list = [
        {'published_date': date(2024, 1, 10), 'sentiment_score': 1.0},  # Day 0 - included
        {'published_date': date(2024, 1, 11), 'sentiment_score': 100.0}, # Future - excluded
        {'published_date': date(2024, 1, 9), 'sentiment_score': 0.5},    # Day 1 - included
    ]
    
    result = calculate_aggregated_sentiment(sentiment_list, target_date)
    
    # Should only include Day 0 and Day 1
    assert result['metadata']['weighted_news_count'] == 2, \
        f"Expected 2 news items, got {result['metadata']['weighted_news_count']}"
    expected = (1.0 * 1.0 + 0.5 * 0.5) / (1.0 + 0.5)
    assert abs(result['aggregated_score'] - expected) < 0.0001, \
        f"Expected {expected:.6f}, got {result['aggregated_score']:.6f}"
    print("✓ Future news exclusion test passed")


def test_datetime_objects():
    """Test that datetime objects are correctly handled."""
    target_date = date(2024, 1, 10)
    
    sentiment_list = [
        {'published_date': datetime(2024, 1, 10, 14, 30, 0), 'sentiment_score': 1.0},
        {'published_date': datetime(2024, 1, 9, 10, 15, 0), 'sentiment_score': 0.5},
    ]
    
    result = calculate_aggregated_sentiment(sentiment_list, target_date)
    
    expected = (1.0 * 1.0 + 0.5 * 0.5) / (1.0 + 0.5)
    assert abs(result['aggregated_score'] - expected) < 0.0001, \
        f"Expected {expected:.6f}, got {result['aggregated_score']:.6f}"
    print("✓ Datetime objects test passed")


def test_empty_sentiment_list():
    """Test that empty sentiment list returns zero."""
    target_date = date(2024, 1, 10)
    
    result = calculate_aggregated_sentiment([], target_date)
    
    assert result['aggregated_score'] == 0.0
    assert result['count'] == 0
    print("✓ Empty sentiment list test passed")


def main():
    """Run all decay tests."""
    print("=" * 60)
    print("Testing Decay Calculation")
    print("=" * 60)
    
    try:
        test_basic_decay()
        test_same_day_news()
        test_old_news_excluded()
        test_future_news_excluded()
        test_datetime_objects()
        test_empty_sentiment_list()
        
        print("\n" + "=" * 60)
        print("All decay tests passed! ✓")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
