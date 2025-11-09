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
            params_json = json.dumps(portfolio.params)
        
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
        INSERT INTO portfolio_positions (portfolio_id, ticker, weight, price_used, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (portfolio_id, ticker) DO UPDATE SET 
            weight = EXCLUDED.weight,
            price_used = EXCLUDED.price_used,
            created_at = EXCLUDED.created_at
        """
        
        params_list = []
        for position in positions:
            params_list.append((
                position.portfolio_id,
                position.ticker,
                position.weight,
                position.price_used,
                position.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_portfolio_positions(self, portfolio_id: Optional[int] = None,
                               tickers: Optional[List[str]] = None,
                               portfolio_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Retrieve portfolio positions from the database.
        
        Args:
            portfolio_id: Single portfolio ID to filter by
            tickers: List of tickers to filter by
            portfolio_ids: List of portfolio IDs to filter by (for batch fetching)
        """
        query = "SELECT * FROM portfolio_positions WHERE 1=1"
        params = []
        
        if portfolio_id:
            query += " AND portfolio_id = %s"
            params.append(portfolio_id)
        elif portfolio_ids:
            placeholders = ','.join(['%s'] * len(portfolio_ids))
            query += f" AND portfolio_id IN ({placeholders})"
            params.extend(portfolio_ids)
        
        if tickers:
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND ticker IN ({placeholders})"
            params.extend(tickers)
        
        query += " ORDER BY portfolio_id, ticker"
        
        return self.execute_query(query, tuple(params) if params else None)

