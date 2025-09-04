"""
Database models for the Quant Project system.

Defines the data structures used throughout the system.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional
import pandas as pd


@dataclass
class SignalScore:
    """Represents a signal score for a specific ticker and date."""
    ticker: str
    signal_id: str
    date: date
    score: float
    created_at: Optional[datetime] = None


@dataclass
class Portfolio:
    """Represents a portfolio with weights and metadata."""
    portfolio_id: str
    creation_date: date
    weights: Dict[str, float]  # ticker -> weight
    signal_weights: Dict[str, float]  # signal_id -> weight
    risk_aversion: float
    max_weight: float
    created_at: Optional[datetime] = None


@dataclass
class BacktestResult:
    """Represents the results of a backtest."""
    backtest_id: str
    start_date: date
    end_date: date
    tickers: List[str]
    signals: List[str]
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    alpha: float
    information_ratio: float
    execution_time_seconds: float
    created_at: Optional[datetime] = None


@dataclass
class SignalDefinition:
    """Represents a signal definition with parameters."""
    signal_id: str
    name: str
    parameters: Dict[str, any]
    enabled: bool = True
    created_at: Optional[datetime] = None


class DataFrameConverter:
    """Utility class to convert between DataFrames and model objects."""
    
    @staticmethod
    def signal_scores_to_dataframe(scores: List[SignalScore]) -> pd.DataFrame:
        """Convert list of SignalScore objects to DataFrame."""
        data = []
        for score in scores:
            data.append({
                'ticker': score.ticker,
                'signal_id': score.signal_id,
                'date': score.date,
                'score': score.score,
                'created_at': score.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def dataframe_to_signal_scores(df: pd.DataFrame) -> List[SignalScore]:
        """Convert DataFrame to list of SignalScore objects."""
        scores = []
        for _, row in df.iterrows():
            scores.append(SignalScore(
                ticker=row['ticker'],
                signal_id=row['signal_id'],
                date=row['date'],
                score=row['score'],
                created_at=row.get('created_at')
            ))
        return scores
    
    @staticmethod
    def portfolios_to_dataframe(portfolios: List[Portfolio]) -> pd.DataFrame:
        """Convert list of Portfolio objects to DataFrame."""
        data = []
        for portfolio in portfolios:
            data.append({
                'portfolio_id': portfolio.portfolio_id,
                'creation_date': portfolio.creation_date,
                'weights': portfolio.weights,
                'signal_weights': portfolio.signal_weights,
                'risk_aversion': portfolio.risk_aversion,
                'max_weight': portfolio.max_weight,
                'created_at': portfolio.created_at
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def backtest_results_to_dataframe(results: List[BacktestResult]) -> pd.DataFrame:
        """Convert list of BacktestResult objects to DataFrame."""
        data = []
        for result in results:
            data.append({
                'backtest_id': result.backtest_id,
                'start_date': result.start_date,
                'end_date': result.end_date,
                'tickers': ','.join(result.tickers),
                'signals': ','.join(result.signals),
                'total_return': result.total_return,
                'annualized_return': result.annualized_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'volatility': result.volatility,
                'alpha': result.alpha,
                'information_ratio': result.information_ratio,
                'execution_time_seconds': result.execution_time_seconds,
                'created_at': result.created_at
            })
        return pd.DataFrame(data)
