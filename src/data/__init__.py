"""
Data module for the Alpha Crucible Quant system.

Provides comprehensive data fetching, validation, and integration capabilities.
"""

from .realtime_fetcher import (
    RealTimeDataFetcher,
    RealTimeDataFetcherWithFallback,
    default_fetcher,
    fallback_fetcher
)

from .validation import (
    DataValidator,
    default_validator
)

__all__ = [
    'RealTimeDataFetcher',
    'RealTimeDataFetcherWithFallback', 
    'default_fetcher',
    'fallback_fetcher',
    'DataValidator',
    'default_validator'
]
