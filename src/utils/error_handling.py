"""
Error handling utilities for the Quant Project system.

Provides common error handling patterns and decorators to reduce code duplication.
"""

import logging
import functools
from typing import Callable, TypeVar, Optional, Any, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')


def handle_database_errors(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    Decorator to handle common database errors.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that returns None on database errors
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            return None
    return wrapper


def handle_calculation_errors(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    Decorator to handle common calculation errors.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that returns None on calculation errors
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except (ValueError, ZeroDivisionError, IndexError) as e:
            logger.error(f"Calculation error in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return None
    return wrapper


def handle_api_errors(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    Decorator to handle common API errors.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that returns None on API errors
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {e}")
            return None
    return wrapper


@contextmanager
def safe_execution(operation_name: str, return_value: Any = None):
    """
    Context manager for safe execution with error handling.
    
    Args:
        operation_name: Name of the operation for logging
        return_value: Value to return if operation fails
        
    Yields:
        None
    """
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        if return_value is not None:
            return return_value


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to retry function on failure.
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            import time
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {e}")
                        return None
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator


def validate_inputs(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate function inputs.
    
    Args:
        **validators: Dictionary mapping parameter names to validation functions
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate inputs
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        logger.error(f"Validation failed for {param_name} in {func.__name__}")
                        return None
            
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
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        import time
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
    """Check if value is positive."""
    return isinstance(value, (int, float)) and value > 0


def is_non_negative(value: Any) -> bool:
    """Check if value is non-negative."""
    return isinstance(value, (int, float)) and value >= 0


def is_valid_date(value: Any) -> bool:
    """Check if value is a valid date."""
    from datetime import date
    return isinstance(value, date)


def is_valid_ticker(value: Any) -> bool:
    """Check if value is a valid ticker symbol."""
    return isinstance(value, str) and len(value) > 0 and value.isalpha()


def is_valid_list(value: Any) -> bool:
    """Check if value is a non-empty list."""
    return isinstance(value, list) and len(value) > 0
