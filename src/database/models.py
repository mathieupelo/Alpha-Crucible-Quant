"""
Database models for the Quant Project system.

Defines the data structures used throughout the system.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import json


@dataclass
class Signal:
    """Represents a signal definition/metadata."""
    name: str
    description: Optional[str] = None
    enabled: bool = True
    parameters: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class SignalRaw:
    """Represents raw signal data for a specific ticker and date."""
    asof_date: date
    ticker: str
    signal_id: int  # Foreign key to signals.id
    value: float
    signal_name: Optional[str] = None  # Kept for backward compatibility
    metadata: Optional[Dict[str, Any]] = None
    company_uid: Optional[str] = None  # Foreign key to varrock.companies
    created_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class ScoreCombined:
    """Represents combined scores derived from raw signals."""
    asof_date: date
    ticker: str
    score: float
    method: str
    params: Optional[Dict[str, Any]] = None
    company_uid: Optional[str] = None  # Foreign key to varrock.companies
    created_at: Optional[datetime] = None


@dataclass
class Portfolio:
    """Represents a portfolio with metadata."""
    run_id: str
    universe_id: int
    asof_date: date
    method: str
    params: Optional[Dict[str, Any]] = None
    cash: float = 0.0
    total_value: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class PortfolioPosition:
    """Represents a position within a portfolio."""
    portfolio_id: int
    ticker: str
    weight: float
    price_used: float
    company_uid: Optional[str] = None  # Foreign key to varrock.companies
    created_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class BacktestSignal:
    """Represents the relationship between a backtest and a signal."""
    run_id: str
    signal_id: int
    weight: float = 1.0
    created_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class Backtest:
    """Represents a backtest run configuration."""
    run_id: str
    start_date: date
    end_date: date
    frequency: str
    universe_id: int
    name: Optional[str] = None
    universe: Optional[Dict[str, Any]] = None
    benchmark: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class BacktestNav:
    """Represents daily NAV data for a backtest."""
    run_id: str
    date: date
    nav: float
    benchmark_nav: Optional[float] = None
    pnl: Optional[float] = None


@dataclass
class Universe:
    """Represents a universe of tickers."""
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class UniverseTicker:
    """Represents a ticker within a universe."""
    universe_id: int
    ticker: str
    added_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class UniverseCompany:
    """Represents a company within a universe (Varrock schema)."""
    universe_id: int
    company_uid: str
    added_at: Optional[datetime] = None
    id: Optional[int] = None


class DataFrameConverter:
    """Utility class to convert between DataFrames and model objects."""
    
    @staticmethod
    def signals_raw_to_dataframe(signals: List[SignalRaw]) -> pd.DataFrame:
        """Convert list of SignalRaw objects to DataFrame."""
        data = []
        for signal in signals:
            data.append({
                'asof_date': signal.asof_date,
                'ticker': signal.ticker,
                'signal_name': signal.signal_name,
                'value': signal.value,
                'metadata': json.dumps(signal.metadata) if signal.metadata else None,
                'created_at': signal.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_signals_raw(df: pd.DataFrame) -> List[SignalRaw]:
        """Convert DataFrame to list of SignalRaw objects."""
        signals = []
        for _, row in df.iterrows():
            metadata = None
            if row.get('metadata'):
                try:
                    metadata = json.loads(row['metadata'])
                except (json.JSONDecodeError, TypeError):
                    metadata = None
            
            signals.append(SignalRaw(
                asof_date=row['asof_date'],
                ticker=row['ticker'],
                signal_name=row['signal_name'],
                value=row['value'],
                metadata=metadata,
                created_at=row.get('created_at')
            ))
        return signals
    
    @staticmethod
    def scores_combined_to_dataframe(scores: List[ScoreCombined]) -> pd.DataFrame:
        """Convert list of ScoreCombined objects to DataFrame."""
        data = []
        for score in scores:
            data.append({
                'asof_date': score.asof_date,
                'ticker': score.ticker,
                'score': score.score,
                'method': score.method,
                'params': json.dumps(score.params) if score.params else None,
                'created_at': score.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_scores_combined(df: pd.DataFrame) -> List[ScoreCombined]:
        """Convert DataFrame to list of ScoreCombined objects."""
        scores = []
        for _, row in df.iterrows():
            params = None
            if row.get('params'):
                try:
                    params = json.loads(row['params'])
                except (json.JSONDecodeError, TypeError):
                    params = None
            
            scores.append(ScoreCombined(
                asof_date=row['asof_date'],
                ticker=row['ticker'],
                score=row['score'],
                method=row['method'],
                params=params,
                created_at=row.get('created_at')
            ))
        return scores
    
    @staticmethod
    def portfolios_to_dataframe(portfolios: List[Portfolio]) -> pd.DataFrame:
        """Convert list of Portfolio objects to DataFrame."""
        data = []
        for portfolio in portfolios:
            data.append({
                'run_id': portfolio.run_id,
                'asof_date': portfolio.asof_date,
                'method': portfolio.method,
                'params': json.dumps(portfolio.params) if portfolio.params else None,
                'cash': portfolio.cash,
                'notes': portfolio.notes,
                'created_at': portfolio.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_portfolios(df: pd.DataFrame) -> List[Portfolio]:
        """Convert DataFrame to list of Portfolio objects."""
        portfolios = []
        for _, row in df.iterrows():
            params = None
            if row.get('params'):
                try:
                    params = json.loads(row['params'])
                except (json.JSONDecodeError, TypeError):
                    params = None
            
            portfolios.append(Portfolio(
                run_id=row['run_id'],
                asof_date=row['asof_date'],
                method=row['method'],
                params=params,
                cash=row.get('cash', 0.0),
                notes=row.get('notes'),
                created_at=row.get('created_at')
            ))
        return portfolios
    
    @staticmethod
    def portfolio_positions_to_dataframe(positions: List[PortfolioPosition]) -> pd.DataFrame:
        """Convert list of PortfolioPosition objects to DataFrame."""
        data = []
        for position in positions:
            data.append({
                'portfolio_id': position.portfolio_id,
                'ticker': position.ticker,
                'weight': position.weight,
                'price_used': position.price_used,
                'created_at': position.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_portfolio_positions(df: pd.DataFrame) -> List[PortfolioPosition]:
        """Convert DataFrame to list of PortfolioPosition objects."""
        positions = []
        for _, row in df.iterrows():
            positions.append(PortfolioPosition(
                portfolio_id=row['portfolio_id'],
                ticker=row['ticker'],
                weight=row['weight'],
                price_used=row['price_used'],
                created_at=row.get('created_at')
            ))
        return positions
    
    @staticmethod
    def backtests_to_dataframe(backtests: List[Backtest]) -> pd.DataFrame:
        """Convert list of Backtest objects to DataFrame."""
        data = []
        for backtest in backtests:
            data.append({
                'run_id': backtest.run_id,
                'name': backtest.name,
                'start_date': backtest.start_date,
                'end_date': backtest.end_date,
                'frequency': backtest.frequency,
                'universe_id': backtest.universe_id,
                'universe': json.dumps(backtest.universe) if backtest.universe else None,
                'benchmark': backtest.benchmark,
                'params': json.dumps(backtest.params) if backtest.params else None,
                'created_at': backtest.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_backtests(df: pd.DataFrame) -> List[Backtest]:
        """Convert DataFrame to list of Backtest objects."""
        backtests = []
        for _, row in df.iterrows():
            universe = None
            if row.get('universe'):
                try:
                    universe = json.loads(row['universe'])
                except (json.JSONDecodeError, TypeError):
                    universe = None
            
            params = None
            if row.get('params'):
                try:
                    params = json.loads(row['params'])
                except (json.JSONDecodeError, TypeError):
                    params = None
            
            backtests.append(Backtest(
                run_id=row['run_id'],
                name=row.get('name'),
                start_date=row['start_date'],
                end_date=row['end_date'],
                frequency=row['frequency'],
                universe_id=row.get('universe_id'),
                universe=universe,
                benchmark=row.get('benchmark'),
                params=params,
                created_at=row.get('created_at')
            ))
        return backtests
    
    @staticmethod
    def backtest_nav_to_dataframe(nav_data: List[BacktestNav]) -> pd.DataFrame:
        """Convert list of BacktestNav objects to DataFrame."""
        data = []
        for nav in nav_data:
            data.append({
                'run_id': nav.run_id,
                'date': nav.date,
                'nav': nav.nav,
                'benchmark_nav': nav.benchmark_nav,
                'pnl': nav.pnl
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_backtest_nav(df: pd.DataFrame) -> List[BacktestNav]:
        """Convert DataFrame to list of BacktestNav objects."""
        nav_data = []
        for _, row in df.iterrows():
            nav_data.append(BacktestNav(
                run_id=row['run_id'],
                date=row['date'],
                nav=row['nav'],
                benchmark_nav=row.get('benchmark_nav'),
                pnl=row.get('pnl')
            ))
        return nav_data
    
    @staticmethod
    def universes_to_dataframe(universes: List[Universe]) -> pd.DataFrame:
        """Convert list of Universe objects to DataFrame."""
        data = []
        for universe in universes:
            data.append({
                'name': universe.name,
                'description': universe.description,
                'created_at': universe.created_at,
                'updated_at': universe.updated_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_universes(df: pd.DataFrame) -> List[Universe]:
        """Convert DataFrame to list of Universe objects."""
        universes = []
        for _, row in df.iterrows():
            universes.append(Universe(
                id=row.get('id'),
                name=row['name'],
                description=row.get('description'),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at')
            ))
        return universes
    
    @staticmethod
    def universe_tickers_to_dataframe(tickers: List[UniverseTicker]) -> pd.DataFrame:
        """Convert list of UniverseTicker objects to DataFrame."""
        data = []
        for ticker in tickers:
            data.append({
                'universe_id': ticker.universe_id,
                'ticker': ticker.ticker,
                'added_at': ticker.added_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_universe_tickers(df: pd.DataFrame) -> List[UniverseTicker]:
        """Convert DataFrame to list of UniverseTicker objects."""
        tickers = []
        for _, row in df.iterrows():
            tickers.append(UniverseTicker(
                id=row.get('id'),
                universe_id=row['universe_id'],
                ticker=row['ticker'],
                added_at=row.get('added_at')
            ))
        return tickers
