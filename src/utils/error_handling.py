"""
Error handling utilities for the Alpha Crucible Quant system.

Provides robust error handling patterns and decorators with explicit error propagation.
All decorators raise exceptions instead of returning None for better error visibility.
"""

import logging
import functools
import time
import inspect
from typing import Callable, TypeVar, Any, Union, Dict, Tuple
from contextlib import contextmanager
from datetime import date

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


class CalculationError(Exception):
    """Custom exception for calculation-related errors."""
    pass


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


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
            raise DatabaseError(f"Database operation failed in {func.__name__}: {e}") from e
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
            raise CalculationError(f"Calculation failed in {func.__name__}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise CalculationError(f"Unexpected calculation error in {func.__name__}: {e}") from e
    return wrapper


def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common API errors with explicit error propagation.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that raises APIError on API errors
        
    Raises:
        APIError: When API operations fail
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {e}")
            raise APIError(f"API operation failed in {func.__name__}: {e}") from e
    return wrapper


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
                        raise ValidationError(error_msg)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


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


# Common validation functions
def is_positive(value: Any) -> bool:
    """
    Check if value is positive.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a positive number, False otherwise
    """
    return isinstance(value, (int, float)) and value > 0


def is_non_negative(value: Any) -> bool:
    """
    Check if value is non-negative.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a non-negative number, False otherwise
    """
    return isinstance(value, (int, float)) and value >= 0


def is_valid_date(value: Any) -> bool:
    """
    Check if value is a valid date.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a date object, False otherwise
    """
    return isinstance(value, date)


def is_valid_ticker(value: Any) -> bool:
    """
    Check if value is a valid ticker symbol.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a valid ticker symbol, False otherwise
    """
    if not isinstance(value, str):
        return False
    return len(value) > 0 and len(value) <= 5 and value.isalpha()


def is_valid_list(value: Any) -> bool:
    """
    Check if value is a non-empty list.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a non-empty list, False otherwise
    """
    return isinstance(value, list) and len(value) > 0


def is_valid_string(value: Any) -> bool:
    """
    Check if value is a non-empty string.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a non-empty string, False otherwise
    """
    return isinstance(value, str) and len(value.strip()) > 0


def is_valid_number(value: Any) -> bool:
    """
    Check if value is a valid number (int or float).
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a number, False otherwise
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_valid_dict(value: Any) -> bool:
    """
    Check if value is a non-empty dictionary.
    
    Args:
        value: Value to validate
        
    Returns:
        True if value is a non-empty dict, False otherwise
    """
    return isinstance(value, dict) and len(value) > 0
