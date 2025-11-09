"""
Signal and SignalRaw database operations.

This module contains all database operations related to signals and raw signal data.
"""

import logging
from datetime import date, datetime
from typing import List, Optional
import pandas as pd

from .models import Signal, SignalRaw

logger = logging.getLogger(__name__)


class SignalOperationsMixin:
    """Mixin class providing signal-related database operations."""
    
    def resolve_ticker_to_company_uid(self, ticker: str) -> Optional[str]:
        """
        Resolve a ticker symbol to company_uid via varrock.tickers.
        
        Args:
            ticker: Ticker symbol to resolve
            
        Returns:
            company_uid if found, None if not found (raises error per user requirement)
            
        Raises:
            ValueError: If ticker doesn't exist in Varrock schema
        """
        query = """
        SELECT company_uid 
        FROM varrock.tickers 
        WHERE ticker = %s 
        LIMIT 1
        """
        df = self.execute_query(query, (ticker.strip().upper(),))
        
        if df.empty:
            raise ValueError(f"Ticker '{ticker}' not found in Varrock schema. Please add it to a universe first.")
        
        return str(df.iloc[0]['company_uid'])
    
    # Signal Operations
    
    def store_signal(self, signal: Signal) -> int:
        """Store a signal definition in the database."""
        query = """
        INSERT INTO signals (name, description, enabled, parameters, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            description = EXCLUDED.description,
            enabled = EXCLUDED.enabled,
            parameters = EXCLUDED.parameters,
            updated_at = EXCLUDED.updated_at
        RETURNING id
        """
        
        parameters_json = None
        if signal.parameters:
            import json
            parameters_json = json.dumps(signal.parameters)
        
        params = (
            signal.name,
            signal.description,
            signal.enabled,
            parameters_json,
            signal.created_at or datetime.now(),
            signal.updated_at or datetime.now()
        )
        
        return self.execute_insert(query, params)
    
    def get_signal_by_name(self, name: str) -> Optional[Signal]:
        """Get a signal by its name."""
        query = "SELECT * FROM signals WHERE name = %s"
        df = self.execute_query(query, (name,))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        parameters = None
        if row.get('parameters'):
            import json
            try:
                parameters = json.loads(row['parameters'])
            except (json.JSONDecodeError, TypeError):
                parameters = None
        
        return Signal(
            id=int(row['id']),
            name=str(row['name']),
            description=str(row.get('description')) if pd.notna(row.get('description')) else None,
            enabled=bool(row.get('enabled', True)),
            parameters=parameters,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def get_signal_by_id(self, signal_id: int) -> Optional[Signal]:
        """Get a signal by its ID."""
        query = "SELECT * FROM signals WHERE id = %s"
        df = self.execute_query(query, (signal_id,))
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        parameters = None
        if row.get('parameters'):
            import json
            try:
                parameters = json.loads(row['parameters'])
            except (json.JSONDecodeError, TypeError):
                parameters = None
        
        return Signal(
            id=int(row['id']),
            name=str(row['name']),
            description=str(row.get('description')) if pd.notna(row.get('description')) else None,
            enabled=bool(row.get('enabled', True)),
            parameters=parameters,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def get_all_signals(self, enabled_only: bool = False) -> pd.DataFrame:
        """Get all signals from the database."""
        if enabled_only:
            query = "SELECT * FROM signals WHERE enabled = TRUE ORDER BY name"
        else:
            query = "SELECT * FROM signals ORDER BY name"
        return self.execute_query(query)
    
    def get_or_create_signal(self, name: str, description: Optional[str] = None) -> Signal:
        """Get an existing signal or create a new one."""
        signal = self.get_signal_by_name(name)
        if signal:
            return signal
        
        # Create new signal
        new_signal = Signal(
            name=name,
            description=description or f"Signal: {name}",
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        signal_id = self.store_signal(new_signal)
        new_signal.id = signal_id
        return new_signal
    
    # Signal Raw Operations
    
    def store_signals_raw(self, signals: List[SignalRaw]) -> int:
        """Store raw signals in the database."""
        if not signals:
            return 0
        
        # Use signal_id if available, otherwise look up by signal_name
        query = """
        INSERT INTO signal_raw (asof_date, ticker, signal_id, signal_name, value, metadata, company_uid, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (asof_date, ticker, signal_id) DO UPDATE SET 
            value = EXCLUDED.value,
            metadata = EXCLUDED.metadata,
            company_uid = EXCLUDED.company_uid,
            created_at = EXCLUDED.created_at
        """
        
        params_list = []
        for signal in signals:
            metadata_json = None
            if signal.metadata:
                import json
                metadata_json = json.dumps(signal.metadata)
            
            # Resolve signal_id if only signal_name is provided
            signal_id = signal.signal_id
            signal_name = signal.signal_name
            
            if not signal_id and signal_name:
                # Look up signal_id from signal_name
                signal_obj = self.get_signal_by_name(signal_name)
                if signal_obj:
                    signal_id = signal_obj.id
                else:
                    # Create signal if it doesn't exist
                    signal_obj = self.get_or_create_signal(signal_name)
                    signal_id = signal_obj.id
            
            # Resolve company_uid from ticker if not already provided
            company_uid = signal.company_uid
            if not company_uid and signal.ticker:
                try:
                    company_uid = self.resolve_ticker_to_company_uid(signal.ticker)
                except ValueError as e:
                    logger.error(f"Failed to resolve ticker {signal.ticker} to company_uid: {e}")
                    # Continue without company_uid for now (will be populated by migration)
                    company_uid = None
            
            params_list.append((
                signal.asof_date,
                signal.ticker,
                signal_id,
                signal_name,
                signal.value,
                metadata_json,
                company_uid,
                signal.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_signals_raw(self, tickers: Optional[List[str]] = None,
                       signal_names: Optional[List[str]] = None,
                       signal_ids: Optional[List[int]] = None,
                       company_uids: Optional[List[str]] = None,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieve raw signals from the database with company information.
        
        Args:
            tickers: Optional list of tickers (will be resolved to company_uids)
            signal_names: Optional list of signal names
            signal_ids: Optional list of signal IDs
            company_uids: Optional list of company UIDs (preferred over tickers)
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        # Check if company_uid column exists in signal_raw
        column_check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'signal_raw' 
        AND column_name = 'company_uid'
        """
        has_company_uid = not self.execute_query(column_check_query).empty
        
        if has_company_uid:
            query = """
            SELECT 
                sr.*, 
                s.name as signal_name_display, 
                s.description as signal_description,
                c.company_uid,
                ci.name as company_name,
                mt.ticker as main_ticker
            FROM signal_raw sr
            LEFT JOIN signals s ON sr.signal_id = s.id
            LEFT JOIN varrock.companies c ON sr.company_uid = c.company_uid AND sr.company_uid IS NOT NULL
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
        else:
            # Fallback query without company_uid joins
            query = """
            SELECT 
                sr.*, 
                s.name as signal_name_display, 
                s.description as signal_description,
                NULL as company_uid,
                NULL as company_name,
                sr.ticker as main_ticker
            FROM signal_raw sr
            LEFT JOIN signals s ON sr.signal_id = s.id
            WHERE 1=1
            """
        params = []
        
        # Always use ticker filter for now (company_uid may not be populated yet)
        # Resolve tickers to company_uids if provided and column exists
        if tickers and not company_uids and has_company_uid:
            resolved_company_uids = []
            for ticker in tickers:
                try:
                    company_uid = self.resolve_ticker_to_company_uid(ticker)
                    resolved_company_uids.append(company_uid)
                except ValueError:
                    logger.debug(f"Ticker {ticker} not found in Varrock, will use ticker filter")
            if resolved_company_uids and len(resolved_company_uids) == len(tickers):
                company_uids = resolved_company_uids
        
        if company_uids and has_company_uid:
            placeholders = ','.join(['%s'] * len(company_uids))
            query += f" AND (sr.company_uid IN ({placeholders}) OR sr.ticker IN ({','.join(['%s'] * len(tickers))}))"
            params.extend(company_uids)
            params.extend(tickers)
        elif tickers:
            # Fallback to ticker filter (always works)
            placeholders = ','.join(['%s'] * len(tickers))
            query += f" AND sr.ticker IN ({placeholders})"
            params.extend(tickers)
        
        if signal_ids:
            placeholders = ','.join(['%s'] * len(signal_ids))
            query += f" AND sr.signal_id IN ({placeholders})"
            params.extend(signal_ids)
        elif signal_names:
            # Look up signal_ids from signal_names
            signal_id_list = []
            for signal_name in signal_names:
                signal_obj = self.get_signal_by_name(signal_name)
                if signal_obj:
                    signal_id_list.append(signal_obj.id)
            
            if signal_id_list:
                placeholders = ','.join(['%s'] * len(signal_id_list))
                query += f" AND sr.signal_id IN ({placeholders})"
                params.extend(signal_id_list)
            else:
                # Return empty if no signals found
                return pd.DataFrame()
        
        if start_date:
            query += " AND sr.asof_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND sr.asof_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY sr.asof_date, sr.ticker, s.name"
        
        return self.execute_query(query, tuple(params) if params else None)

