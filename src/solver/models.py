"""
Portfolio models for the Quant Project system.

Defines the Portfolio class and related data structures.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional
import pandas as pd

from .config import SolverConfig


@dataclass
class StockPosition:
    """Represents a stock position in a portfolio."""
    
    ticker: str
    weight: float
    alpha_score: float
    expected_return: Optional[float] = None
    risk_contribution: Optional[float] = None
    
    def __post_init__(self):
        """Validate position parameters."""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {self.weight}")
        
        if not -1 <= self.alpha_score <= 1:
            raise ValueError(f"Alpha score must be between -1 and 1, got {self.alpha_score}")


@dataclass
class Portfolio:
    """Represents an optimized portfolio."""
    
    portfolio_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creation_date: date = field(default_factory=date.today)
    positions: Dict[str, StockPosition] = field(default_factory=dict)
    config: SolverConfig = field(default_factory=SolverConfig)
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def add_position(self, ticker: str, weight: float, alpha_score: float, 
                    expected_return: Optional[float] = None,
                    risk_contribution: Optional[float] = None):
        """
        Add a position to the portfolio.
        
        Args:
            ticker: Stock ticker symbol
            weight: Portfolio weight (0-1)
            alpha_score: Alpha score for the stock
            expected_return: Expected return (optional)
            risk_contribution: Risk contribution (optional)
        """
        position = StockPosition(
            ticker=ticker,
            weight=weight,
            alpha_score=alpha_score,
            expected_return=expected_return,
            risk_contribution=risk_contribution
        )
        self.positions[ticker] = position
    
    def get_weight(self, ticker: str) -> float:
        """
        Get the weight of a specific stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Portfolio weight (0-1)
        """
        return self.positions.get(ticker, StockPosition(ticker, 0.0, 0.0)).weight
    
    def get_weights(self) -> Dict[str, float]:
        """
        Get all portfolio weights.
        
        Returns:
            Dictionary mapping ticker to weight
        """
        return {ticker: pos.weight for ticker, pos in self.positions.items()}
    
    def get_alpha_scores(self) -> Dict[str, float]:
        """
        Get all alpha scores.
        
        Returns:
            Dictionary mapping ticker to alpha score
        """
        return {ticker: pos.alpha_score for ticker, pos in self.positions.items()}
    
    def get_expected_returns(self) -> Dict[str, float]:
        """
        Get all expected returns.
        
        Returns:
            Dictionary mapping ticker to expected return
        """
        return {ticker: pos.expected_return for ticker, pos in self.positions.items() 
                if pos.expected_return is not None}
    
    def get_risk_contributions(self) -> Dict[str, float]:
        """
        Get all risk contributions.
        
        Returns:
            Dictionary mapping ticker to risk contribution
        """
        return {ticker: pos.risk_contribution for ticker, pos in self.positions.items() 
                if pos.risk_contribution is not None}
    
    def get_total_weight(self) -> float:
        """
        Get the total portfolio weight.
        
        Returns:
            Total weight (should be 1.0 for a fully invested portfolio)
        """
        return sum(pos.weight for pos in self.positions.values())
    
    def get_num_positions(self) -> int:
        """
        Get the number of positions in the portfolio.
        
        Returns:
            Number of positions
        """
        return len(self.positions)
    
    def get_active_positions(self) -> Dict[str, StockPosition]:
        """
        Get only positions with non-zero weights.
        
        Returns:
            Dictionary of active positions
        """
        return {ticker: pos for ticker, pos in self.positions.items() if pos.weight > 0}
    
    def get_top_positions(self, n: int = 10) -> List[tuple[str, StockPosition]]:
        """
        Get the top N positions by weight.
        
        Args:
            n: Number of top positions to return
            
        Returns:
            List of (ticker, position) tuples sorted by weight
        """
        sorted_positions = sorted(
            self.positions.items(),
            key=lambda x: x[1].weight,
            reverse=True
        )
        return sorted_positions[:n]
    
    def get_concentration_metrics(self) -> Dict[str, float]:
        """
        Get portfolio concentration metrics.
        
        Returns:
            Dictionary with concentration metrics
        """
        weights = [pos.weight for pos in self.positions.values() if pos.weight > 0]
        
        if not weights:
            return {
                'num_positions': 0,
                'max_weight': 0.0,
                'min_weight': 0.0,
                'weight_std': 0.0,
                'herfindahl_index': 0.0,
                'effective_num_positions': 0.0
            }
        
        import numpy as np
        
        return {
            'num_positions': len(weights),
            'max_weight': max(weights),
            'min_weight': min(weights),
            'weight_std': np.std(weights),
            'herfindahl_index': sum(w**2 for w in weights),
            'effective_num_positions': 1.0 / sum(w**2 for w in weights) if weights else 0.0
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert portfolio to DataFrame.
        
        Returns:
            DataFrame with portfolio positions
        """
        data = []
        for ticker, position in self.positions.items():
            data.append({
                'ticker': ticker,
                'weight': position.weight,
                'alpha_score': position.alpha_score,
                'expected_return': position.expected_return,
                'risk_contribution': position.risk_contribution
            })
        
        return pd.DataFrame(data)
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert portfolio to dictionary.
        
        Returns:
            Dictionary representation of portfolio
        """
        return {
            'portfolio_id': self.portfolio_id,
            'creation_date': self.creation_date,
            'positions': {
                ticker: {
                    'weight': pos.weight,
                    'alpha_score': pos.alpha_score,
                    'expected_return': pos.expected_return,
                    'risk_contribution': pos.risk_contribution
                }
                for ticker, pos in self.positions.items()
            },
            'config': self.config.to_dict(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'Portfolio':
        """
        Create portfolio from dictionary.
        
        Args:
            data: Dictionary representation of portfolio
            
        Returns:
            Portfolio instance
        """
        portfolio = cls(
            portfolio_id=data['portfolio_id'],
            creation_date=data['creation_date'],
            config=SolverConfig.from_dict(data['config']),
            metadata=data.get('metadata', {})
        )
        
        for ticker, pos_data in data['positions'].items():
            portfolio.add_position(
                ticker=ticker,
                weight=pos_data['weight'],
                alpha_score=pos_data['alpha_score'],
                expected_return=pos_data.get('expected_return'),
                risk_contribution=pos_data.get('risk_contribution')
            )
        
        return portfolio
    
    def __str__(self) -> str:
        """String representation of portfolio."""
        return f"Portfolio(id={self.portfolio_id[:8]}..., date={self.creation_date}, positions={len(self.positions)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of portfolio."""
        return f"Portfolio(portfolio_id='{self.portfolio_id}', creation_date={self.creation_date}, positions={len(self.positions)})"
