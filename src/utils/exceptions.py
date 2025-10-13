"""
Custom exceptions for Alpha Crucible Quant system.

Provides standardized exception classes for different types of errors
that can occur throughout the system.
"""

from typing import Optional, Dict, Any


class AlphaCrucibleError(Exception):
    """Base exception class for all Alpha Crucible errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ValidationError(AlphaCrucibleError):
    """Raised when input validation fails."""
    pass


class DatabaseError(AlphaCrucibleError):
    """Raised when database operations fail."""
    pass


class SignalError(AlphaCrucibleError):
    """Raised when signal processing fails."""
    pass


class PortfolioError(AlphaCrucibleError):
    """Raised when portfolio operations fail."""
    pass


class BacktestError(AlphaCrucibleError):
    """Raised when backtest operations fail."""
    pass


class DataError(AlphaCrucibleError):
    """Raised when data operations fail."""
    pass


class ConfigurationError(AlphaCrucibleError):
    """Raised when configuration is invalid."""
    pass
