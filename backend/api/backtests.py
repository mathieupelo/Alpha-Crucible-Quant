"""
Backtest API Routes

FastAPI routes for backtest-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date
import logging

from models import BacktestResponse, BacktestListResponse, BacktestMetricsResponse, ErrorResponse, BacktestCreateRequest
from services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database service
db_service = DatabaseService()


@router.post("/backtests", response_model=BacktestResponse)
async def create_backtest(request: BacktestCreateRequest):
    """Create a new backtest with universe validation."""
    try:
        # Validate universe exists and has minimum tickers
        universe = db_service.get_universe_by_id(request.universe_id)
        if universe is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Universe with ID {request.universe_id} not found"
            )
        
        # Check ticker count
        tickers = db_service.get_universe_tickers(request.universe_id)
        if len(tickers) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"The selected universe '{universe['name']}' must contain at least 5 tickers. "
                       f"Please add more tickers or choose another universe. "
                       f"Current ticker count: {len(tickers)}"
            )
        
        # Create backtest configuration
        from src.backtest.config import BacktestConfig
        config = BacktestConfig(
            start_date=request.start_date,
            end_date=request.end_date,
            universe_id=request.universe_id,
            initial_capital=request.initial_capital,
            rebalancing_frequency=request.rebalancing_frequency,
            evaluation_period=request.evaluation_period,
            transaction_costs=request.transaction_costs,
            max_weight=request.max_weight,
            min_weight=request.min_weight,
            risk_aversion=request.risk_aversion,
            benchmark_ticker=request.benchmark_ticker,
            use_equal_weight_benchmark=request.use_equal_weight_benchmark,
            min_lookback_days=request.min_lookback_days,
            max_lookback_days=request.max_lookback_days,
            signal_weights=request.signal_weights,
            signal_combination_method=request.signal_combination_method,
            forward_fill_signals=request.forward_fill_signals
        )
        
        # Run the backtest
        from src.backtest.engine import BacktestEngine
        engine = BacktestEngine()
        
        # Get universe tickers
        universe_tickers = [ticker['ticker'] for ticker in tickers]
        
        # Run backtest
        result = engine.run_backtest(
            tickers=universe_tickers,
            signals=request.signals,
            config=config
        )
        
        # Get the created backtest from database
        backtest = db_service.get_backtest_by_run_id(result.run_id)
        if backtest is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve created backtest")
        
        return BacktestResponse(**backtest)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests", response_model=BacktestListResponse)
async def get_backtests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size")
):
    """Get all backtests with pagination."""
    try:
        result = db_service.get_all_backtests(page=page, size=size)
        return BacktestListResponse(**result)
    except Exception as e:
        logger.error(f"Error getting backtests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}", response_model=BacktestResponse)
async def get_backtest(run_id: str):
    """Get specific backtest by run ID."""
    try:
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        return BacktestResponse(**backtest)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backtest {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/metrics", response_model=BacktestMetricsResponse)
async def get_backtest_metrics(run_id: str):
    """Get performance metrics for a backtest."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        metrics = db_service.get_backtest_metrics(run_id)
        if metrics is None:
            raise HTTPException(status_code=404, detail=f"No metrics available for backtest {run_id}")
        
        return BacktestMetricsResponse(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/portfolios")
async def get_backtest_portfolios(run_id: str):
    """Get all portfolios for a backtest."""
    try:
        portfolios = db_service.get_backtest_portfolios(run_id)
        return {
            "portfolios": portfolios,
            "total": len(portfolios),
            "run_id": run_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolios for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/signals")
async def get_backtest_signals(
    run_id: str,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get raw signals for a backtest period."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        signals = db_service.get_backtest_signals(run_id, start_date, end_date)
        return {
            "signals": signals,
            "total": len(signals),
            "run_id": run_id,
            "start_date": start_date,
            "end_date": end_date
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signals for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtests/{run_id}/scores")
async def get_backtest_scores(
    run_id: str,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """Get combined scores for a backtest period."""
    try:
        # Check if backtest exists
        backtest = db_service.get_backtest_by_run_id(run_id)
        if backtest is None:
            raise HTTPException(status_code=404, detail=f"Backtest {run_id} not found")
        
        scores = db_service.get_backtest_scores(run_id, start_date, end_date)
        return {
            "scores": scores,
            "total": len(scores),
            "run_id": run_id,
            "start_date": start_date,
            "end_date": end_date
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scores for {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

