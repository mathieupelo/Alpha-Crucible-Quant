"""
Score Combined database operations.

This module contains all database operations related to combined scores.
"""

import logging
from datetime import date, datetime
from typing import List, Optional
import pandas as pd

from .models import ScoreCombined

logger = logging.getLogger(__name__)


class ScoreOperationsMixin:
    """Mixin class providing score-related database operations."""
    
    def store_scores_combined(self, scores: List[ScoreCombined]) -> int:
        """Store combined scores in the database."""
        if not scores:
            return 0
        
        query = """
        INSERT INTO scores_combined (asof_date, ticker, score, method, params, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (asof_date, ticker, method) DO UPDATE SET 
            score = EXCLUDED.score,
            method = EXCLUDED.method,
            params = EXCLUDED.params,
            created_at = EXCLUDED.created_at
        """
        
        params_list = []
        for score in scores:
            params_json = None
            if score.params:
                import json
                params_json = json.dumps(score.params)
            
            params_list.append((
                score.asof_date,
                score.ticker,
                score.score,
                score.method,
                params_json,
                score.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_scores_combined(self, tickers: Optional[List[str]] = None,
                           methods: Optional[List[str]] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve combined scores from the database."""
        query = "SELECT * FROM scores_combined WHERE 1=1"
        params = []
        
        if tickers:
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND ticker IN ({placeholders})"
            params.extend(tickers)
        
        if methods:
            placeholders = ','.join(['%s'] * len(methods))
            query += f" AND method IN ({placeholders})"
            params.extend(methods)
        
        if start_date:
            query += " AND asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY asof_date, ticker, method"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_scores_combined_pivot(self, tickers: List[str], methods: List[str],
                                 start_date: date, end_date: date, 
                                 forward_fill: bool = True) -> pd.DataFrame:
        """Get combined scores as a pivot table (date x ticker x method)."""
        df = self.get_scores_combined(tickers, methods, start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Create pivot table with date as index, ticker-method as columns
        pivot_df = df.pivot_table(
            index='asof_date',
            columns=['ticker', 'method'],
            values='score',
            aggfunc='first'
        )
        
        # Forward fill missing values if requested
        if forward_fill and not pivot_df.empty:
            pivot_df = pivot_df.ffill()
        
        return pivot_df

