"""
Solver configuration for portfolio optimization.

Defines configuration parameters for the portfolio solver.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SolverConfig:
    """Configuration for portfolio optimization solver."""
    
    allocation_method: str = "mean_variance"
    """Allocation method: 'mean_variance' or 'score_based'"""
    
    risk_aversion: float = 0.0
    """Risk aversion parameter (0 = no risk aversion, 1 = maximum risk aversion)"""
    
    max_weight: float = 0.1
    """Maximum weight for any single stock (default: 10%)"""
    
    min_weight: float = 0.0
    """Minimum weight for any single stock (default: 0%)"""
    
    long_only: bool = True
    """Whether to allow only long positions (no short selling)"""
    
    max_turnover: Optional[float] = None
    """Maximum turnover constraint (optional)"""
    
    transaction_costs: float = 0.0
    """Transaction costs as a percentage (default: 0%)"""
    
    score_temperature: float = 1.0
    """Temperature parameter for score-based allocation (higher = more concentrated)"""
    
    positive_weight_ratio: float = 0.6
    """Ratio of total weight allocated to positive scores (0.6 = 60%)"""
    
    negative_weight_ratio: float = 0.4
    """Ratio of total weight allocated to negative scores (0.4 = 40%)"""
    
    solver_options: Optional[dict] = None
    """Additional solver options for CVXOPT"""
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.allocation_method not in ["mean_variance", "score_based"]:
            raise ValueError("Allocation method must be 'mean_variance' or 'score_based'")
        
        if not 0 <= self.risk_aversion <= 1:
            raise ValueError("Risk aversion must be between 0 and 1")
        
        if not 0 <= self.max_weight <= 1:
            raise ValueError("Max weight must be between 0 and 1")
        
        if not 0 <= self.min_weight <= self.max_weight:
            raise ValueError("Min weight must be between 0 and max weight")
        
        if self.max_turnover is not None and self.max_turnover < 0:
            raise ValueError("Max turnover must be non-negative")
        
        if self.transaction_costs < 0:
            raise ValueError("Transaction costs must be non-negative")
        
        if self.score_temperature <= 0:
            raise ValueError("Score temperature must be positive")
        
        if not 0 <= self.positive_weight_ratio <= 1:
            raise ValueError("Positive weight ratio must be between 0 and 1")
        
        if not 0 <= self.negative_weight_ratio <= 1:
            raise ValueError("Negative weight ratio must be between 0 and 1")
        
        if abs(self.positive_weight_ratio + self.negative_weight_ratio - 1.0) > 1e-6:
            raise ValueError("Positive and negative weight ratios must sum to 1.0")
        
        if self.solver_options is None:
            self.solver_options = {
                'show_progress': False,
                'maxiters': 100,
                'abstol': 1e-7,
                'reltol': 1e-6
            }
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'allocation_method': self.allocation_method,
            'risk_aversion': self.risk_aversion,
            'max_weight': self.max_weight,
            'min_weight': self.min_weight,
            'long_only': self.long_only,
            'max_turnover': self.max_turnover,
            'transaction_costs': self.transaction_costs,
            'score_temperature': self.score_temperature,
            'positive_weight_ratio': self.positive_weight_ratio,
            'negative_weight_ratio': self.negative_weight_ratio,
            'solver_options': self.solver_options
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'SolverConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"SolverConfig(method={self.allocation_method}, risk_aversion={self.risk_aversion}, max_weight={self.max_weight}, min_weight={self.min_weight})"
