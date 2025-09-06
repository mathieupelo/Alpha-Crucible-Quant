"""
Trading calendar utilities for NYSE validation.

This module provides utilities for validating trading dates and determining
whether a given date is a valid trading day according to NYSE rules.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TradingCalendar:
    """
    NYSE trading calendar utilities.
    
    Provides methods to validate trading dates and determine if a given date
    is a valid trading day according to NYSE rules (weekdays excluding holidays).
    """
    
    def __init__(self):
        """Initialize the trading calendar."""
        self._holidays = self._get_nyse_holidays()
    
    def _get_nyse_holidays(self) -> List[date]:
        """
        Get NYSE holidays for the current year and a few years ahead.
        
        Returns:
            List of NYSE holiday dates
        """
        # This is a simplified implementation. In production, you might want to
        # use a more comprehensive holiday calendar or an external service.
        holidays = []
        current_year = date.today().year
        
        # Add holidays for the next 5 years
        for year in range(current_year - 2, current_year + 5):
            # New Year's Day
            holidays.append(date(year, 1, 1))
            
            # Martin Luther King Jr. Day (third Monday in January)
            mlk_day = self._get_nth_weekday(year, 1, 3, 0)  # 0 = Monday
            holidays.append(mlk_day)
            
            # Presidents' Day (third Monday in February)
            presidents_day = self._get_nth_weekday(year, 2, 3, 0)  # 0 = Monday
            holidays.append(presidents_day)
            
            # Good Friday (varies by year - simplified approximation)
            good_friday = self._get_good_friday(year)
            holidays.append(good_friday)
            
            # Memorial Day (last Monday in May)
            memorial_day = self._get_last_weekday(year, 5, 0)  # 0 = Monday
            holidays.append(memorial_day)
            
            # Juneteenth (June 19th, since 2021)
            if year >= 2021:
                holidays.append(date(year, 6, 19))
            
            # Independence Day (July 4th)
            holidays.append(date(year, 7, 4))
            
            # Labor Day (first Monday in September)
            labor_day = self._get_nth_weekday(year, 9, 1, 0)  # 0 = Monday
            holidays.append(labor_day)
            
            # Thanksgiving Day (fourth Thursday in November)
            thanksgiving = self._get_nth_weekday(year, 11, 4, 3)  # 3 = Thursday
            holidays.append(thanksgiving)
            
            # Christmas Day (December 25th)
            holidays.append(date(year, 12, 25))
        
        return holidays
    
    def _get_nth_weekday(self, year: int, month: int, n: int, weekday: int) -> date:
        """
        Get the nth occurrence of a weekday in a given month.
        
        Args:
            year: Year
            month: Month (1-12)
            n: Which occurrence (1-based)
            weekday: Weekday (0=Monday, 1=Tuesday, ..., 6=Sunday)
            
        Returns:
            Date of the nth weekday
        """
        # Start from the first day of the month
        first_day = date(year, month, 1)
        
        # Find the first occurrence of the target weekday
        days_ahead = weekday - first_day.weekday()
        if days_ahead < 0:
            days_ahead += 7
        
        first_occurrence = first_day + timedelta(days=days_ahead)
        
        # Add (n-1) weeks to get the nth occurrence
        return first_occurrence + timedelta(weeks=n-1)
    
    def _get_last_weekday(self, year: int, month: int, weekday: int) -> date:
        """
        Get the last occurrence of a weekday in a given month.
        
        Args:
            year: Year
            month: Month (1-12)
            weekday: Weekday (0=Monday, 1=Tuesday, ..., 6=Sunday)
            
        Returns:
            Date of the last weekday
        """
        # Get the last day of the month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # Find the last occurrence of the target weekday
        days_back = last_day.weekday() - weekday
        if days_back < 0:
            days_back += 7
        
        return last_day - timedelta(days=days_back)
    
    def _get_good_friday(self, year: int) -> date:
        """
        Get Good Friday for a given year (simplified approximation).
        
        Args:
            year: Year
            
        Returns:
            Date of Good Friday
        """
        # This is a simplified calculation. In production, you might want to
        # use a more accurate method or an external library.
        # Good Friday is typically 2 days before Easter Sunday
        # Easter is the first Sunday after the first full moon on or after March 21
        
        # Simplified approximation: Good Friday is usually in late March or early April
        # This is not accurate for all years but serves as a placeholder
        if year == 2024:
            return date(2024, 3, 29)
        elif year == 2025:
            return date(2025, 4, 18)
        elif year == 2026:
            return date(2026, 4, 3)
        elif year == 2027:
            return date(2027, 3, 26)
        elif year == 2028:
            return date(2028, 4, 14)
        else:
            # Fallback to a reasonable date in March/April
            return date(year, 3, 29)
    
    def is_trading_day(self, target_date: date) -> bool:
        """
        Check if a given date is a valid NYSE trading day.
        
        Args:
            target_date: Date to check
            
        Returns:
            True if the date is a trading day, False otherwise
        """
        # Check if it's a weekday (Monday=0, Sunday=6)
        if target_date.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if it's a holiday
        if target_date in self._holidays:
            return False
        
        return True
    
    def get_next_trading_day(self, target_date: date) -> date:
        """
        Get the next trading day after the given date.
        
        Args:
            target_date: Starting date
            
        Returns:
            Next trading day
        """
        next_date = target_date + timedelta(days=1)
        while not self.is_trading_day(next_date):
            next_date += timedelta(days=1)
        return next_date
    
    def get_previous_trading_day(self, target_date: date) -> date:
        """
        Get the previous trading day before the given date.
        
        Args:
            target_date: Starting date
            
        Returns:
            Previous trading day
        """
        prev_date = target_date - timedelta(days=1)
        while not self.is_trading_day(prev_date):
            prev_date -= timedelta(days=1)
        return prev_date
    
    def get_trading_days(self, start_date: date, end_date: date) -> List[date]:
        """
        Get all trading days between start_date and end_date (inclusive).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of trading days
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def get_first_trading_day_of_month(self, year: int, month: int) -> date:
        """
        Get the first trading day of a given month.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            First trading day of the month
        """
        first_day = date(year, month, 1)
        return self.get_next_trading_day(first_day - timedelta(days=1))
    
    def get_rebalancing_dates(self, start_date: date, end_date: date) -> List[date]:
        """
        Get rebalancing dates (first trading day of each month) between start and end dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of rebalancing dates
        """
        rebalancing_dates = []
        current_date = start_date
        
        # Get the first trading day of the start month
        first_rebalance = self.get_first_trading_day_of_month(start_date.year, start_date.month)
        if first_rebalance >= start_date:
            rebalancing_dates.append(first_rebalance)
        
        # Add first trading day of each subsequent month
        current_month = start_date.month
        current_year = start_date.year
        
        while True:
            # Move to next month
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
            
            rebalance_date = self.get_first_trading_day_of_month(current_year, current_month)
            
            if rebalance_date > end_date:
                break
            
            rebalancing_dates.append(rebalance_date)
        
        return rebalancing_dates
    
    def validate_trading_date(self, target_date: date) -> bool:
        """
        Validate that a date is a valid trading date.
        
        Args:
            target_date: Date to validate
            
        Returns:
            True if valid trading date, False otherwise
        """
        if not isinstance(target_date, date):
            logger.error(f"Invalid date type: {type(target_date)}")
            return False
        
        if target_date < date(1900, 1, 1) or target_date > date(2100, 12, 31):
            logger.error(f"Date out of reasonable range: {target_date}")
            return False
        
        return self.is_trading_day(target_date)
