"""
Comprehensive error handling utilities for Alpha Crucible Quant system.

Consolidates all error handling functionality into a single module:
- Custom exception classes
- Error handling decorators
- Validation utilities
- Retry mechanisms
"""

import logging
import functools
import time
import inspect
from typing import Callable, TypeVar, Any, Union, Dict, Tuple, Optional, Type
from contextlib import contextmanager
from datetime import date
from fastapi import HTTPException

logger = logging.getLogger(__name__)

T = TypeVar('T')

# ============================================================================
# CUSTOM EXCEPTION CLASSES
# ============================================================================

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


class CalculationError(AlphaCrucibleError):
    """Raised when calculation operations fail."""
    pass


class APIError(AlphaCrucibleError):
    """Raised when API operations fail."""
    pass


# ============================================================================
# ERROR HANDLING DECORATORS
# ============================================================================

def handle_database_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common database errors with explicit error propagation.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that raises DatabaseError on database errors
        
    Raises:
        DatabaseError: When database operations fail
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed in {func.__name__}: {e}", error_code="DB_ERROR") from e
    return wrapper


def handle_calculation_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common calculation errors with explicit error propagation.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that raises CalculationError on calculation errors
        
    Raises:
        CalculationError: When calculations fail
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except (ValueError, ZeroDivisionError, IndexError, ArithmeticError) as e:
            logger.error(f"Calculation error in {func.__name__}: {e}")
            raise CalculationError(f"Calculation failed in {func.__name__}: {e}", error_code="CALC_ERROR") from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise CalculationError(f"Unexpected calculation error in {func.__name__}: {e}", error_code="CALC_ERROR") from e
    return wrapper


def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for API endpoints that converts exceptions to HTTP responses.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that raises HTTPException on API errors
        
    Raises:
        HTTPException: When API operations fail
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
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


def handle_errors(
    error_type: Type[Exception] = Exception,
    default_message: str = "An unexpected error occurred",
    log_error: bool = True,
    reraise: bool = True
) -> Callable:
    """
    Generic decorator for standardized error handling.
    
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


# ============================================================================
# RETRY MECHANISMS
# ============================================================================

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    exceptions: Tuple[type, ...] = (Exception,)) -> Callable:
    """
    Decorator to retry function on failure with explicit error propagation.
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorator function that raises the last exception after all retries fail
        
    Raises:
        Exception: The last exception encountered after all retries are exhausted
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {e}")
                        raise e
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected error in retry logic for {func.__name__}")
        return wrapper
    return decorator


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

@contextmanager
def safe_execution(operation_name: str, raise_on_error: bool = True):
    """
    Context manager for safe execution with error handling.
    
    Args:
        operation_name: Name of the operation for logging
        raise_on_error: Whether to raise exceptions or suppress them
        
    Yields:
        None
        
    Raises:
        Exception: If raise_on_error is True and an error occurs
    """
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        if raise_on_error:
            raise


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

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


def validate_inputs(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate function inputs with explicit error propagation.
    
    Args:
        **validators: Dictionary mapping parameter names to validation functions
        
    Returns:
        Decorator function that raises ValidationError on validation failure
        
    Raises:
        ValidationError: When input validation fails
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate inputs
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        error_msg = f"Validation failed for parameter '{param_name}' in {func.__name__}: invalid value {value}"
                        logger.error(error_msg)
                        raise ValidationError(error_msg, error_code="INVALID_INPUT")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with execution time logging
        
    Raises:
        Exception: Re-raises any exception from the wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {e}")
            raise
    
    return wrapper


# ============================================================================
# COMMON VALIDATION FUNCTIONS
# ============================================================================

def is_positive(value: Any) -> bool:
    """Check if value is positive."""
    return isinstance(value, (int, float)) and value > 0


def is_non_negative(value: Any) -> bool:
    """Check if value is non-negative."""
    return isinstance(value, (int, float)) and value >= 0


def is_valid_date(value: Any) -> bool:
    """Check if value is a valid date."""
    return isinstance(value, date)


def is_valid_ticker(value: Any) -> bool:
    """Check if value is a valid ticker symbol."""
    if not isinstance(value, str):
        return False
    return len(value) > 0 and len(value) <= 5 and value.isalpha()


def is_valid_list(value: Any) -> bool:
    """Check if value is a non-empty list."""
    return isinstance(value, list) and len(value) > 0


def is_valid_string(value: Any) -> bool:
    """Check if value is a non-empty string."""
    return isinstance(value, str) and len(value.strip()) > 0


def is_valid_number(value: Any) -> bool:
    """Check if value is a valid number (int or float)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_valid_dict(value: Any) -> bool:
    """Check if value is a non-empty dictionary."""
    return isinstance(value, dict) and len(value) > 0