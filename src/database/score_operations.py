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
        INSERT INTO scores_combined (asof_date, ticker, score, method, params, company_uid, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (asof_date, ticker, method) DO UPDATE SET 
            score = EXCLUDED.score,
            method = EXCLUDED.method,
            params = EXCLUDED.params,
            company_uid = EXCLUDED.company_uid,
            created_at = EXCLUDED.created_at
        """
        
        params_list = []
        for score in scores:
            params_json = None
            if score.params:
                import json
                params_json = json.dumps(score.params)
            
            # Resolve company_uid from ticker if not already provided
            company_uid = score.company_uid
            if not company_uid and score.ticker:
                try:
                    # Use resolve_ticker_to_company_uid from SignalOperationsMixin if available
                    if hasattr(self, 'resolve_ticker_to_company_uid'):
                        company_uid = self.resolve_ticker_to_company_uid(score.ticker)
                    else:
                        # Fallback: query directly
                        query_ticker = """
                        SELECT company_uid 
                        FROM varrock.tickers 
                        WHERE ticker = %s 
                        LIMIT 1
                        """
                        df = self.execute_query(query_ticker, (score.ticker.strip().upper(),))
                        if not df.empty:
                            company_uid = str(df.iloc[0]['company_uid'])
                except (ValueError, Exception) as e:
                    logger.error(f"Failed to resolve ticker {score.ticker} to company_uid: {e}")
                    # Continue without company_uid for now (will be populated by migration)
                    company_uid = None
            
            params_list.append((
                score.asof_date,
                score.ticker,
                score.score,
                score.method,
                params_json,
                company_uid,
                score.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_scores_combined(self, tickers: Optional[List[str]] = None,
                           methods: Optional[List[str]] = None,
                           company_uids: Optional[List[str]] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieve combined scores from the database with company information.
        
        Args:
            tickers: Optional list of tickers (will be resolved to company_uids)
            methods: Optional list of methods
            company_uids: Optional list of company UIDs (preferred over tickers)
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        query = """
        SELECT 
            sc.*,
            c.company_uid,
            ci.name as company_name,
            mt.ticker as main_ticker
        FROM scores_combined sc
        LEFT JOIN varrock.companies c ON sc.company_uid = c.company_uid
        LEFT JOIN varrock.company_info ci ON c.company_uid = ci.company_uid
        LEFT JOIN LATERAL (
            SELECT ticker 
            FROM varrock.tickers 
            WHERE company_uid = c.company_uid 
            AND is_main_ticker = TRUE 
            LIMIT 1
        ) mt ON TRUE
        WHERE 1=1
        """
        params = []
        
        # Resolve tickers to company_uids if provided
        if tickers and not company_uids:
            resolved_company_uids = []
            for ticker in tickers:
                try:
                    if hasattr(self, 'resolve_ticker_to_company_uid'):
                        company_uid = self.resolve_ticker_to_company_uid(ticker)
                    else:
                        # Fallback: query directly
                        query_ticker = """
                        SELECT company_uid 
                        FROM varrock.tickers 
                        WHERE ticker = %s 
                        LIMIT 1
                        """
                        df = self.execute_query(query_ticker, (ticker.strip().upper(),))
                        if not df.empty:
                            company_uid = str(df.iloc[0]['company_uid'])
                        else:
                            raise ValueError(f"Ticker '{ticker}' not found")
                    resolved_company_uids.append(company_uid)
                except (ValueError, Exception):
                    logger.warning(f"Ticker {ticker} not found, skipping")
            if resolved_company_uids:
                company_uids = resolved_company_uids
        
        if company_uids:
            placeholders = ','.join(['%s'] * len(company_uids))
            query += f" AND sc.company_uid IN ({placeholders})"
            params.extend(company_uids)
        elif tickers:
            # Fallback to ticker filter if company_uids couldn't be resolved
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND sc.ticker IN ({placeholders})"
            params.extend(tickers)
        
        if methods:
            placeholders = ','.join(['%s'] * len(methods))
            query += f" AND sc.method IN ({placeholders})"
            params.extend(methods)
        
        if start_date:
            query += " AND sc.asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND sc.asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY sc.asof_date, sc.ticker, sc.method"
        
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

