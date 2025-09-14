"""
Date utility functions for the Quant Project system.

Provides common date operations and trading day calculations.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional
import pandas as pd


class DateUtils:
    """Utility class for date operations."""
    
    @staticmethod
    def get_trading_days(start_date: date, end_date: date) -> List[date]:
        """
        Get list of trading days (weekdays excluding major market holidays) between start and end dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of trading dates (weekdays excluding major holidays)
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Check if it's a major market holiday
                if not DateUtils.is_market_holiday(current_date):
                    trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    @staticmethod
    def is_market_holiday(check_date: date) -> bool:
        """
        Check if a date is a major US market holiday.
        
        Args:
            check_date: Date to check
            
        Returns:
            True if it's a market holiday, False otherwise
        """
        # Major US market holidays
        holidays = [
            # New Year's Day
            (1, 1),
            # Martin Luther King Jr. Day (3rd Monday in January)
            # Presidents' Day (3rd Monday in February) 
            # Good Friday (varies by year)
            # Memorial Day (last Monday in May)
            # Juneteenth (June 19)
            (6, 19),
            # Independence Day (July 4)
            (7, 4),
            # Labor Day (1st Monday in September)
            # Thanksgiving Day (4th Thursday in November)
            # Christmas Day (December 25)
            (12, 25),
        ]
        
        # Check fixed holidays
        if (check_date.month, check_date.day) in holidays:
            return True
        
        # Check variable holidays
        year = check_date.year
        
        # Martin Luther King Jr. Day (3rd Monday in January)
        if check_date.month == 1 and check_date.weekday() == 0:
            # Count Mondays in January up to this date
            mondays_in_jan = 0
            for day in range(1, check_date.day + 1):
                if date(year, 1, day).weekday() == 0:
                    mondays_in_jan += 1
            if mondays_in_jan == 3:
                return True
        
        # Presidents' Day (3rd Monday in February)
        if check_date.month == 2 and check_date.weekday() == 0:
            # Count Mondays in February up to this date
            mondays_in_feb = 0
            for day in range(1, check_date.day + 1):
                if date(year, 2, day).weekday() == 0:
                    mondays_in_feb += 1
            if mondays_in_feb == 3:
                return True
        
        # Memorial Day (last Monday in May)
        if check_date.month == 5 and check_date.weekday() == 0:
            # Check if this is the last Monday in May
            last_monday = None
            for day in range(1, 32):
                try:
                    test_date = date(year, 5, day)
                    if test_date.weekday() == 0:
                        last_monday = test_date
                except ValueError:
                    break
            if last_monday and check_date == last_monday:
                return True
        
        # Labor Day (1st Monday in September)
        if check_date.month == 9 and check_date.weekday() == 0:
            # Count Mondays in September up to this date
            mondays_in_sep = 0
            for day in range(1, check_date.day + 1):
                if date(year, 9, day).weekday() == 0:
                    mondays_in_sep += 1
            if mondays_in_sep == 1:
                return True
        
        # Thanksgiving Day (4th Thursday in November)
        if check_date.month == 11 and check_date.weekday() == 3:  # Thursday
            # Count Thursdays in November up to this date
            thursdays_in_nov = 0
            for day in range(1, check_date.day + 1):
                if date(year, 11, day).weekday() == 3:
                    thursdays_in_nov += 1
            if thursdays_in_nov == 4:
                return True
        
        return False
    
    @staticmethod
    def get_next_trading_day(current_date: date) -> date:
        """
        Get the next trading day after the given date.
        
        Args:
            current_date: Current date
            
        Returns:
            Next trading day
        """
        next_date = current_date + timedelta(days=1)
        
        # Skip weekends
        while next_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            next_date += timedelta(days=1)
        
        return next_date
    
    @staticmethod
    def get_previous_trading_day(current_date: date) -> date:
        """
        Get the previous trading day before the given date.
        
        Args:
            current_date: Current date
            
        Returns:
            Previous trading day
        """
        prev_date = current_date - timedelta(days=1)
        
        # Skip weekends
        while prev_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            prev_date -= timedelta(days=1)
        
        return prev_date
    
    @staticmethod
    def get_month_end(date_obj: date) -> date:
        """
        Get the last day of the month for the given date.
        
        Args:
            date_obj: Date object
            
        Returns:
            Last day of the month
        """
        if date_obj.month == 12:
            return date_obj.replace(year=date_obj.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            return date_obj.replace(month=date_obj.month + 1, day=1) - timedelta(days=1)
    
    @staticmethod
    def get_month_start(date_obj: date) -> date:
        """
        Get the first day of the month for the given date.
        
        Args:
            date_obj: Date object
            
        Returns:
            First day of the month
        """
        return date_obj.replace(day=1)
    
    @staticmethod
    def is_month_end(date_obj: date) -> bool:
        """
        Check if the given date is the last day of the month.
        
        Args:
            date_obj: Date object
            
        Returns:
            True if it's the last day of the month
        """
        return date_obj == DateUtils.get_month_end(date_obj)
    
    @staticmethod
    def is_month_start(date_obj: date) -> bool:
        """
        Check if the given date is the first day of the month.
        
        Args:
            date_obj: Date object
            
        Returns:
            True if it's the first day of the month
        """
        return date_obj.day == 1
    
    @staticmethod
    def get_quarter_end(date_obj: date) -> date:
        """
        Get the last day of the quarter for the given date.
        
        Args:
            date_obj: Date object
            
        Returns:
            Last day of the quarter
        """
        quarter = (date_obj.month - 1) // 3 + 1
        quarter_end_month = quarter * 3
        
        if quarter_end_month == 12:
            return date_obj.replace(year=date_obj.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            return date_obj.replace(month=quarter_end_month + 1, day=1) - timedelta(days=1)
    
    @staticmethod
    def get_quarter_start(date_obj: date) -> date:
        """
        Get the first day of the quarter for the given date.
        
        Args:
            date_obj: Date object
            
        Returns:
            First day of the quarter
        """
        quarter = (date_obj.month - 1) // 3 + 1
        quarter_start_month = (quarter - 1) * 3 + 1
        return date_obj.replace(month=quarter_start_month, day=1)
    
    @staticmethod
    def get_year_end(date_obj: date) -> date:
        """
        Get the last day of the year for the given date.
        
        Args:
            date_obj: Date object
            
        Returns:
            Last day of the year
        """
        return date_obj.replace(month=12, day=31)
    
    @staticmethod
    def get_year_start(date_obj: date) -> date:
        """
        Get the first day of the year for the given date.
        
        Args:
            date_obj: Date object
            
        Returns:
            First day of the year
        """
        return date_obj.replace(month=1, day=1)
    
    @staticmethod
    def add_months(date_obj: date, months: int) -> date:
        """
        Add months to a date.
        
        Args:
            date_obj: Date object
            months: Number of months to add (can be negative)
            
        Returns:
            New date with months added
        """
        year = date_obj.year
        month = date_obj.month + months
        
        # Handle year overflow
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1
        
        # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
        try:
            return date_obj.replace(year=year, month=month)
        except ValueError:
            # If the day doesn't exist in the target month, use the last day of the month
            return date(year, month, 1) + timedelta(days=32) - timedelta(days=1)
    
    @staticmethod
    def get_date_range(start_date: date, end_date: date, frequency: str = 'D') -> List[date]:
        """
        Get a range of dates between start and end dates.
        
        Args:
            start_date: Start date
            end_date: End date
            frequency: Frequency ('D' for daily, 'W' for weekly, 'M' for monthly)
            
        Returns:
            List of dates
        """
        if frequency == 'D':
            return DateUtils.get_trading_days(start_date, end_date)
        elif frequency == 'W':
            # Weekly on Mondays
            dates = []
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() == 0:  # Monday
                    dates.append(current_date)
                current_date += timedelta(days=1)
            return dates
        elif frequency == 'M':
            # Monthly on first trading day of month
            dates = []
            current_date = start_date
            while current_date <= end_date:
                if DateUtils.is_month_start(current_date):
                    dates.append(current_date)
                current_date += timedelta(days=1)
            return dates
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
    
    @staticmethod
    def parse_date(date_str: str) -> date:
        """
        Parse a date string into a date object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date object
        """
        if isinstance(date_str, date):
            return date_str
        
        if isinstance(date_str, datetime):
            return date_str.date()
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date string: {date_str}")
    
    @staticmethod
    def format_date(date_obj: date, format_str: str = '%Y-%m-%d') -> str:
        """
        Format a date object into a string.
        
        Args:
            date_obj: Date object
            format_str: Format string
            
        Returns:
            Formatted date string
        """
        return date_obj.strftime(format_str)
    
    @staticmethod
    def get_business_days_between(start_date: date, end_date: date) -> int:
        """
        Get the number of business days between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of business days
        """
        trading_days = DateUtils.get_trading_days(start_date, end_date)
        return len(trading_days)
    
    @staticmethod
    def get_days_between(start_date: date, end_date: date) -> int:
        """
        Get the number of days between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of days
        """
        return (end_date - start_date).days
