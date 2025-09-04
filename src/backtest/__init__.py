"""
Backtesting engine for the Quant Project system.

Provides comprehensive backtesting capabilities for quantitative strategies.
"""

from .engine import BacktestEngine
from .config import BacktestConfig
from .models import BacktestResult

__all__ = ['BacktestEngine', 'BacktestConfig', 'BacktestResult']
