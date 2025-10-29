"""
Input validation and sanitization utilities.
"""

import re
import html
from typing import List, Optional, Any
from datetime import date, datetime
from fastapi import HTTPException


def validate_ticker(ticker: str) -> str:
    """Validate and sanitize ticker symbol."""
    if not ticker or not isinstance(ticker, str):
        raise HTTPException(status_code=400, detail="Ticker must be a non-empty string")
    
    # Remove whitespace and convert to uppercase
    ticker = ticker.strip().upper()
    
    # Validate format (1-5 alphanumeric characters)
    if not re.match(r'^[A-Z0-9]{1,5}$', ticker):
        raise HTTPException(status_code=400, detail="Invalid ticker format")
    
    return ticker


def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> tuple:
    """Validate date range parameters."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    # Check date is not too far in the past or future
    today = date.today()
    if start_date and start_date < today.replace(year=today.year - 10):
        raise HTTPException(status_code=400, detail="Start date too far in the past")
    
    if end_date and end_date > today:
        raise HTTPException(status_code=400, detail="End date cannot be in the future")
    
    return start_date, end_date


def validate_pagination(page: int, size: int) -> tuple:
    """Validate pagination parameters."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    
    if size < 1 or size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
    
    return page, size


def sanitize_string(input_str: str, max_length: int = 255) -> str:
    """Sanitize string input to prevent XSS."""
    if not isinstance(input_str, str):
        return ""
    
    # HTML escape
    sanitized = html.escape(input_str)
    
    # Remove potential script tags
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def validate_sql_injection(input_str: str) -> str:
    """Check for potential SQL injection patterns."""
    if not isinstance(input_str, str):
        return input_str
    
    # Common SQL injection patterns
    sql_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+\w+\s*=\s*\w+)',
        r'(\'|\"|;|--|\/\*|\*\/)',
        r'(\b(UNION|SELECT)\b.*\b(SELECT|UNION)\b)',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            raise HTTPException(status_code=400, detail="Invalid input detected")
    
    return input_str


def validate_xss(input_str: str) -> str:
    """Check for potential XSS patterns."""
    if not isinstance(input_str, str):
        return input_str
    
    # Common XSS patterns
    xss_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe.*?</iframe>',
        r'<object.*?</object>',
        r'<embed.*?</embed>',
        r'<link.*?>',
        r'<meta.*?>',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_str, re.IGNORECASE | re.DOTALL):
            raise HTTPException(status_code=400, detail="Invalid input detected")
    
    return input_str


def validate_ticker_list(tickers: List[str]) -> List[str]:
    """Validate list of ticker symbols."""
    if not tickers:
        return []
    
    if len(tickers) > 50:
        raise HTTPException(status_code=400, detail="Too many tickers (max 50)")
    
    validated_tickers = []
    for ticker in tickers:
        validated_ticker = validate_ticker(ticker)
        if validated_ticker not in validated_tickers:  # Remove duplicates
            validated_tickers.append(validated_ticker)
    
    return validated_tickers


def validate_numeric_range(value: float, min_val: float, max_val: float, field_name: str) -> float:
    """Validate numeric value is within range."""
    if not isinstance(value, (int, float)):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a number")
    
    if value < min_val or value > max_val:
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name} must be between {min_val} and {max_val}"
        )
    
    return float(value)



