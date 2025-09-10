"""
Ticker Validation Service

Service for validating ticker symbols using yfinance with rate limiting and retry logic.
"""

import yfinance as yf
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


class TickerValidationService:
    """Service for validating ticker symbols with rate limiting and retry logic."""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3, base_delay: float = 1.0):
        """Initialize the validation service."""
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Validate a single ticker symbol with retry logic.
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            Dictionary with validation results
        """
        ticker = ticker.strip().upper()
        
        for attempt in range(self.max_retries):
            try:
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying ticker {ticker} in {delay:.2f} seconds (attempt {attempt + 1})")
                    time.sleep(delay)
                
                # Create yfinance ticker object
                yf_ticker = yf.Ticker(ticker)
                
                # Get basic info with timeout
                info = yf_ticker.info
                
                # Check if we got valid data
                if not info or 'symbol' not in info:
                    return {
                        'ticker': ticker,
                        'is_valid': False,
                        'company_name': None,
                        'error_message': 'No data available for this ticker'
                    }
                
                # Extract company name
                company_name = info.get('longName') or info.get('shortName') or info.get('name', 'Unknown')
                
                return {
                    'ticker': ticker,
                    'is_valid': True,
                    'company_name': company_name,
                    'error_message': None
                }
                
            except HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Rate limited for ticker {ticker}, retrying...")
                        continue
                    else:
                        logger.error(f"Rate limited for ticker {ticker} after {self.max_retries} attempts")
                        return {
                            'ticker': ticker,
                            'is_valid': False,
                            'company_name': None,
                            'error_message': 'Rate limited by Yahoo Finance API. Please try again later.'
                        }
                else:
                    logger.error(f"HTTP error validating ticker {ticker}: {e}")
                    return {
                        'ticker': ticker,
                        'is_valid': False,
                        'company_name': None,
                        'error_message': f'HTTP error: {e.response.status_code}'
                    }
            except Exception as e:
                logger.warning(f"Error validating ticker {ticker} (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return {
                        'ticker': ticker,
                        'is_valid': False,
                        'company_name': None,
                        'error_message': str(e)
                    }
        
        return {
            'ticker': ticker,
            'is_valid': False,
            'company_name': None,
            'error_message': 'Failed to validate after multiple attempts'
        }
    
    def validate_tickers(self, tickers: List[str], max_workers: int = 2) -> List[Dict[str, Any]]:
        """
        Validate multiple ticker symbols with reduced concurrency to avoid rate limiting.
        
        Args:
            tickers: List of ticker symbols to validate
            max_workers: Maximum number of concurrent workers (reduced to avoid rate limiting)
            
        Returns:
            List of validation results
        """
        if not tickers:
            return []
        
        # Remove duplicates and clean tickers
        unique_tickers = list(set(ticker.strip().upper() for ticker in tickers if ticker.strip()))
        
        if not unique_tickers:
            return []
        
        results = []
        
        # Use ThreadPoolExecutor with reduced concurrency
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all validation tasks
            future_to_ticker = {
                executor.submit(self.validate_ticker, ticker): ticker 
                for ticker in unique_tickers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_ticker, timeout=self.timeout * len(unique_tickers)):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    ticker = future_to_ticker[future]
                    logger.error(f"Error validating ticker {ticker}: {e}")
                    results.append({
                        'ticker': ticker,
                        'is_valid': False,
                        'company_name': None,
                        'error_message': str(e)
                    })
        
        return results
    
    def validate_tickers_batch(self, tickers: List[str], batch_size: int = 3) -> List[Dict[str, Any]]:
        """
        Validate tickers in small batches to avoid overwhelming the API.
        
        Args:
            tickers: List of ticker symbols to validate
            batch_size: Number of tickers to validate per batch (reduced to avoid rate limiting)
            
        Returns:
            List of validation results
        """
        if not tickers:
            return []
        
        all_results = []
        
        # Process in small batches
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            batch_results = self.validate_tickers(batch, max_workers=1)  # Single worker per batch
            all_results.extend(batch_results)
            
            # Longer delay between batches to be respectful to the API
            if i + batch_size < len(tickers):
                delay = 2.0 + random.uniform(0, 1)  # 2-3 seconds between batches
                logger.info(f"Waiting {delay:.2f} seconds before next batch...")
                time.sleep(delay)
        
        return all_results

