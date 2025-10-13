"""
Standardized error handling utilities for Alpha Crucible Quant system.

Provides decorators and utilities for consistent error handling across the application.
"""

import logging
import functools
from typing import Callable, Any, Optional, Type
from fastapi import HTTPException

from .exceptions import AlphaCrucibleError, DatabaseError, ValidationError, SignalError, PortfolioError, BacktestError

logger = logging.getLogger(__name__)


def handle_errors(
    error_type: Type[Exception] = Exception,
    default_message: str = "An unexpected error occurred",
    log_error: bool = True,
    reraise: bool = True
) -> Callable:
    """
    Decorator for standardized error handling.
    
    Args:
        error_type: Type of exception to catch
        default_message: Default error message if no specific message is available
        log_error: Whether to log the error
        reraise: Whether to reraise the exception after handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except error_type as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise
                else:
                    return None
        return wrapper
    return decorator


def handle_database_errors(func: Callable) -> Callable:
    """Decorator specifically for database operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}", exc_info=True)
            raise DatabaseError(f"Database operation failed: {str(e)}", error_code="DB_ERROR")
    return wrapper


def handle_api_errors(func: Callable) -> Callable:
    """Decorator for API endpoints that converts exceptions to HTTP responses."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except DatabaseError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except SignalError as e:
            logger.error(f"Signal error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Signal processing failed: {str(e)}")
        except PortfolioError as e:
            logger.error(f"Portfolio error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Portfolio operation failed: {str(e)}")
        except BacktestError as e:
            logger.error(f"Backtest error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Backtest failed: {str(e)}")
        except AlphaCrucibleError as e:
            logger.error(f"Application error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
    return wrapper


def validate_required_fields(data: dict, required_fields: list, field_type: str = "data") -> None:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        field_type: Type of data being validated (for error messages)
    
    Raises:
        ValidationError: If any required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationError(
            f"Missing required {field_type} fields: {', '.join(missing_fields)}",
            error_code="MISSING_FIELDS",
            details={"missing_fields": missing_fields}
        )


def validate_signal_scores_completeness(
    tickers: list, 
    signals: list, 
    rebalancing_dates: list, 
    signal_reader
) -> None:
    """
    Validate that signal scores exist for all required combinations.
    
    Args:
        tickers: List of ticker symbols
        signals: List of signal names
        rebalancing_dates: List of rebalancing dates
        signal_reader: SignalReader instance
    
    Raises:
        SignalError: If signal scores are missing for any required combinations
    """
    missing_signals = []
    
    for rebal_date in rebalancing_dates:
        is_complete, missing = signal_reader.validate_signals_complete(
            tickers, signals, rebal_date
        )
        if not is_complete:
            missing_signals.extend(missing)
    
    if missing_signals:
        raise SignalError(
            f"Missing signal scores for {len(missing_signals)} combinations. "
            f"Cannot proceed with backtest. Missing combinations: {missing_signals[:10]}{'...' if len(missing_signals) > 10 else ''}",
            error_code="MISSING_SIGNALS",
            details={
                "missing_count": len(missing_signals),
                "missing_combinations": missing_signals[:20]  # Limit to first 20 for details
            }
        )
