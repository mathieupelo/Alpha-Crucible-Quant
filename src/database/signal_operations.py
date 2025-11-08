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
        INSERT INTO signal_raw (asof_date, ticker, signal_id, signal_name, value, metadata, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (asof_date, ticker, signal_id) DO UPDATE SET 
            value = EXCLUDED.value,
            metadata = EXCLUDED.metadata,
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
            
            params_list.append((
                signal.asof_date,
                signal.ticker,
                signal_id,
                signal_name,
                signal.value,
                metadata_json,
                signal.created_at or datetime.now()
            ))
        
        return self.execute_many(query, params_list)
    
    def get_signals_raw(self, tickers: Optional[List[str]] = None,
                       signal_names: Optional[List[str]] = None,
                       signal_ids: Optional[List[int]] = None,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """Retrieve raw signals from the database."""
        query = """
        SELECT sr.*, s.name as signal_name_display, s.description as signal_description
        FROM signal_raw sr
        LEFT JOIN signals s ON sr.signal_id = s.id
        WHERE 1=1
        """
        params = []
        
        if tickers:
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

