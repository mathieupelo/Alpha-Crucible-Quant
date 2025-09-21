"""
API Response Models

Pydantic models for API responses with proper validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from decimal import Decimal


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Success response model."""
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class BacktestResponse(BaseModel):
    """Backtest response model."""
    id: int = Field(..., description="Backtest ID")
    run_id: str = Field(..., description="Unique run identifier")
    name: Optional[str] = Field(None, description="Backtest name")
    start_date: date = Field(..., description="Backtest start date")
    end_date: date = Field(..., description="Backtest end date")
    frequency: str = Field(..., description="Rebalancing frequency")
    universe_id: int = Field(..., description="Universe ID")
    universe_name: str = Field(..., description="Universe name")
    universe: Optional[Dict[str, Any]] = Field(None, description="Universe configuration")
    benchmark: Optional[str] = Field(None, description="Benchmark ticker")
    params: Optional[Dict[str, Any]] = Field(None, description="Backtest parameters")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class BacktestListResponse(BaseModel):
    """Backtest list response model."""
    backtests: List[BacktestResponse] = Field(..., description="List of backtests")
    total: int = Field(..., description="Total number of backtests")
    page: int = Field(1, description="Current page number")
    size: int = Field(50, description="Page size")


class BacktestCreateRequest(BaseModel):
    """Backtest creation request model."""
    start_date: date = Field(..., description="Backtest start date")
    end_date: date = Field(..., description="Backtest end date")
    universe_id: int = Field(..., description="Universe ID to use for backtesting")
    signals: List[str] = Field(..., description="List of signal IDs to use")
    name: Optional[str] = Field(None, description="Backtest name")
    initial_capital: float = Field(10000.0, ge=0, description="Initial capital for backtesting")
    rebalancing_frequency: str = Field("monthly", description="Rebalancing frequency")
    evaluation_period: str = Field("monthly", description="Evaluation period for returns calculation")
    transaction_costs: float = Field(0.001, ge=0, le=1, description="Transaction costs as percentage")
    max_weight: float = Field(0.1, ge=0, le=1, description="Maximum weight for any single stock")
    min_weight: float = Field(0.0, ge=0, description="Minimum weight for any single stock")
    risk_aversion: float = Field(0.5, ge=0, le=1, description="Risk aversion parameter")
    benchmark_ticker: str = Field("SPY", description="Benchmark ticker for comparison")
    use_equal_weight_benchmark: bool = Field(True, description="Use equal-weight portfolio as benchmark")
    min_lookback_days: int = Field(252, ge=1, description="Minimum lookback period for price data")
    max_lookback_days: int = Field(756, ge=1, description="Maximum lookback period for price data")
    signal_weights: Optional[Dict[str, float]] = Field(None, description="Weights for combining signals")
    signal_combination_method: str = Field("equal_weight", description="Method for combining signals")
    forward_fill_signals: bool = Field(True, description="Forward fill missing signal scores")


class PositionResponse(BaseModel):
    """Portfolio position response model."""
    id: int = Field(..., description="Position ID")
    portfolio_id: int = Field(..., description="Associated portfolio ID")
    ticker: str = Field(..., description="Stock ticker")
    weight: float = Field(..., description="Portfolio weight")
    price_used: float = Field(..., description="Price used for calculation")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class PortfolioResponse(BaseModel):
    """Portfolio response model."""
    id: int = Field(..., description="Portfolio ID")
    run_id: str = Field(..., description="Associated backtest run ID")
    asof_date: date = Field(..., description="Portfolio date")
    method: str = Field(..., description="Portfolio optimization method")
    params: Optional[Dict[str, Any]] = Field(None, description="Portfolio parameters")
    cash: float = Field(0.0, description="Cash allocation")
    total_value: Optional[float] = Field(None, description="Total portfolio value")
    notes: Optional[str] = Field(None, description="Portfolio notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    positions: List[PositionResponse] = Field(default=[], description="Portfolio positions")
    
    model_config = {"from_attributes": True}


class PortfolioListResponse(BaseModel):
    """Portfolio list response model."""
    portfolios: List[PortfolioResponse] = Field(..., description="List of portfolios")
    total: int = Field(..., description="Total number of portfolios")
    run_id: str = Field(..., description="Associated backtest run ID")


class SignalResponse(BaseModel):
    """Signal response model."""
    id: int = Field(..., description="Signal ID")
    asof_date: date = Field(..., description="Signal date")
    ticker: str = Field(..., description="Stock ticker")
    signal_name: str = Field(..., description="Signal type (RSI, SMA, MACD)")
    value: float = Field(..., description="Signal value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Signal metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class ScoreResponse(BaseModel):
    """Combined score response model."""
    id: int = Field(..., description="Score ID")
    asof_date: date = Field(..., description="Score date")
    ticker: str = Field(..., description="Stock ticker")
    score: float = Field(..., description="Combined score value")
    method: str = Field(..., description="Combination method")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class NavResponse(BaseModel):
    """NAV response model."""
    id: int = Field(..., description="NAV record ID")
    run_id: str = Field(..., description="Associated backtest run ID")
    nav_date: date = Field(..., description="NAV date")
    portfolio_nav: float = Field(..., description="Portfolio NAV")
    benchmark_nav: Optional[float] = Field(None, description="Benchmark NAV")
    pnl: Optional[float] = Field(None, description="Profit and Loss")
    
    model_config = {"from_attributes": True}


class NavListResponse(BaseModel):
    """NAV list response model."""
    nav_data: List[NavResponse] = Field(..., description="List of NAV records")
    total: int = Field(..., description="Total number of NAV records")
    run_id: str = Field(..., description="Associated backtest run ID")
    start_date: date = Field(..., description="Start date of NAV data")
    end_date: date = Field(..., description="End date of NAV data")


class BacktestMetricsResponse(BaseModel):
    """Backtest performance metrics response model."""
    run_id: str = Field(..., description="Backtest run ID")
    total_return: float = Field(..., description="Total return percentage")
    annualized_return: float = Field(..., description="Annualized return percentage")
    volatility: float = Field(..., description="Volatility percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    alpha: float = Field(..., description="Alpha")
    beta: float = Field(..., description="Beta")
    information_ratio: float = Field(..., description="Information ratio")
    tracking_error: float = Field(..., description="Tracking error")
    num_rebalances: int = Field(..., description="Number of rebalances")
    avg_turnover: float = Field(..., description="Average turnover")
    avg_num_positions: float = Field(..., description="Average number of positions")
    max_concentration: float = Field(..., description="Maximum concentration")
    execution_time_seconds: float = Field(..., description="Execution time in seconds")


class UniverseResponse(BaseModel):
    """Universe response model."""
    id: int = Field(..., description="Universe ID")
    name: str = Field(..., description="Universe name")
    description: Optional[str] = Field(None, description="Universe description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    ticker_count: int = Field(0, description="Number of tickers in universe")
    
    model_config = {"from_attributes": True}


class UniverseListResponse(BaseModel):
    """Universe list response model."""
    universes: List[UniverseResponse] = Field(..., description="List of universes")
    total: int = Field(..., description="Total number of universes")


class UniverseTickerResponse(BaseModel):
    """Universe ticker response model."""
    id: int = Field(..., description="Ticker ID")
    universe_id: int = Field(..., description="Associated universe ID")
    ticker: str = Field(..., description="Stock ticker")
    added_at: datetime = Field(..., description="Addition timestamp")
    
    model_config = {"from_attributes": True}


class UniverseTickerListResponse(BaseModel):
    """Universe ticker list response model."""
    tickers: List[UniverseTickerResponse] = Field(..., description="List of tickers")
    total: int = Field(..., description="Total number of tickers")
    universe_id: int = Field(..., description="Associated universe ID")


class TickerValidationResponse(BaseModel):
    """Ticker validation response model."""
    ticker: str = Field(..., description="Ticker symbol")
    is_valid: bool = Field(..., description="Whether ticker is valid")
    company_name: Optional[str] = Field(None, description="Company name if valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid")


class UniverseCreateRequest(BaseModel):
    """Universe creation request model."""
    name: str = Field(..., description="Universe name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Universe description", max_length=1000)


class UniverseUpdateRequest(BaseModel):
    """Universe update request model."""
    name: Optional[str] = Field(None, description="Universe name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Universe description", max_length=1000)


class UniverseTickerUpdateRequest(BaseModel):
    """Universe ticker update request model."""
    tickers: List[str] = Field(..., description="List of tickers to add/update")
