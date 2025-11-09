"""
Portfolio and PortfolioPosition database operations.

This module contains all database operations related to portfolios and positions.
"""

import logging
from datetime import date, datetime
from typing import List, Optional
import pandas as pd

from .models import Portfolio, PortfolioPosition

logger = logging.getLogger(__name__)


class PortfolioOperationsMixin:
    """Mixin class providing portfolio-related database operations."""
    
    def store_portfolio(self, portfolio: Portfolio) -> int:
        """Store a portfolio in the database."""
        query = """
        INSERT INTO portfolios (run_id, universe_id, asof_date, method, params, cash, total_value, notes, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (run_id, asof_date) DO UPDATE SET
            universe_id = EXCLUDED.universe_id,
            method = EXCLUDED.method,
            params = EXCLUDED.params,
            cash = EXCLUDED.cash,
            total_value = EXCLUDED.total_value,
            notes = EXCLUDED.notes,
            created_at = EXCLUDED.created_at
        RETURNING id
        """
        
        params_json = None
        if portfolio.params:
            import json
            import numpy as np
            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy_types(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
                return obj
            
            cleaned_params = convert_numpy_types(portfolio.params)
            params_json = json.dumps(cleaned_params)
        
        params = (
            portfolio.run_id,
            portfolio.universe_id,
            portfolio.asof_date,
            portfolio.method,
            params_json,
            portfolio.cash,
            portfolio.total_value,
            portfolio.notes,
            portfolio.created_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_portfolios(self, run_id: Optional[str] = None,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve portfolios from the database."""
        query = "SELECT * FROM portfolios WHERE 1=1"
        params = []
        
        if run_id:
            query += " AND run_id = %s"
            params.append(run_id)
        
        if start_date:
            query += " AND asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY asof_date"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_portfolio_by_id(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio by ID."""
        query = "SELECT * FROM portfolios WHERE id = %s"
        df = self.execute_query(query, (portfolio_id,))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        params = None
        if row.get('params'):
            import json
            try:
                params = json.loads(row['params'])
            except (json.JSONDecodeError, TypeError):
                params = None
        
        return Portfolio(
            id=int(row['id']),
            run_id=str(row['run_id']),
            universe_id=int(row['universe_id']),
            asof_date=row['asof_date'],
            method=str(row['method']),
            params=params,
            cash=float(row.get('cash', 0.0)),
            total_value=float(row.get('total_value')) if pd.notna(row.get('total_value')) else None,
            notes=str(row.get('notes')) if pd.notna(row.get('notes')) else None,
            created_at=row.get('created_at')
        )
    
    # Portfolio Position Operations
    
    def store_portfolio_positions(self, positions: List[PortfolioPosition]) -> int:
        """Store portfolio positions in the database."""
        if not positions:
            return 0
        
        query = """
        INSERT INTO portfolio_positions (portfolio_id, ticker, weight, price_used, company_uid, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (portfolio_id, ticker) DO UPDATE SET 
            weight = EXCLUDED.weight,
            price_used = EXCLUDED.price_used,
            company_uid = EXCLUDED.company_uid,
            created_at = EXCLUDED.created_at
        """
        
        params_list = []
        for position in positions:
            # Resolve company_uid from ticker if not already provided
            company_uid = position.company_uid
            if not company_uid and position.ticker:
                try:
                    # Use resolve_ticker_to_company_uid from SignalOperationsMixin if available
                    if hasattr(self, 'resolve_ticker_to_company_uid'):
                        company_uid = self.resolve_ticker_to_company_uid(position.ticker)
                    else:
                        # Fallback: query directly
                        query_ticker = """
                        SELECT company_uid 
                        FROM varrock.tickers 
                        WHERE ticker = %s 
                        LIMIT 1
                        """
                        df = self.execute_query(query_ticker, (position.ticker.strip().upper(),))
                        if not df.empty:
                            company_uid = str(df.iloc[0]['company_uid'])
                except (ValueError, Exception) as e:
                    logger.error(f"Failed to resolve ticker {position.ticker} to company_uid: {e}")
                    # Continue without company_uid for now (will be populated by migration)
                    company_uid = None
            
            # Ensure weight and price_used are native Python types (not numpy)
            import numpy as np
            weight_value = float(position.weight) if position.weight is not None else 0.0
            price_value = float(position.price_used) if position.price_used is not None else 0.0
            
            # Convert numpy types to native Python types
            if isinstance(weight_value, (np.integer, np.floating)):
                weight_value = float(weight_value)
            if isinstance(price_value, (np.integer, np.floating)):
                price_value = float(price_value)
            
            params_list.append((
                position.portfolio_id,
                position.ticker,
                weight_value,
                price_value,
                company_uid,
                position.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_portfolio_positions(self, portfolio_id: Optional[int] = None,
                               tickers: Optional[List[str]] = None,
                               portfolio_ids: Optional[List[int]] = None,
                               company_uids: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retrieve portfolio positions from the database with company information.
        
        Args:
            portfolio_id: Single portfolio ID to filter by
            tickers: List of tickers to filter by (will be resolved to company_uids)
            portfolio_ids: List of portfolio IDs to filter by (for batch fetching)
            company_uids: List of company UIDs to filter by (preferred over tickers)
        """
        query = """
        SELECT 
            pp.*,
            c.company_uid,
            ci.name as company_name,
            mt.ticker as main_ticker
        FROM portfolio_positions pp
        LEFT JOIN varrock.companies c ON pp.company_uid = c.company_uid
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
        
        if portfolio_id:
            query += " AND pp.portfolio_id = %s"
            params.append(portfolio_id)
        elif portfolio_ids:
            placeholders = ','.join(['%s'] * len(portfolio_ids))
            query += f" AND pp.portfolio_id IN ({placeholders})"
            params.extend(portfolio_ids)
        
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
            query += f" AND pp.company_uid IN ({placeholders})"
            params.extend(company_uids)
        elif tickers:
            # Fallback to ticker filter if company_uids couldn't be resolved
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND pp.ticker IN ({placeholders})"
            params.extend(tickers)
        
        query += " ORDER BY pp.portfolio_id, pp.ticker"
        
        return self.execute_query(query, tuple(params) if params else None)

