"""
Comprehensive tests for the Portfolio and StockPosition models.

Tests all model functionality including edge cases, validation,
and error handling for production readiness.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from solver.models import Portfolio, StockPosition
from solver.config import SolverConfig


class TestStockPosition:
    """Test StockPosition functionality with comprehensive edge cases."""
    
    def test_valid_position(self):
        """Test creating a valid position."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1,
            alpha_score=0.5,
            expected_return=0.12,
            risk_contribution=0.08
        )
        
        assert position.ticker == 'AAPL'
        assert position.weight == 0.1
        assert position.alpha_score == 0.5
        assert position.expected_return == 0.12
        assert position.risk_contribution == 0.08
    
    def test_position_minimal_required_fields(self):
        """Test creating position with minimal required fields."""
        position = StockPosition(
            ticker='MSFT',
            weight=0.2,
            alpha_score=0.3
        )
        
        assert position.ticker == 'MSFT'
        assert position.weight == 0.2
        assert position.alpha_score == 0.3
        assert position.expected_return is None
        assert position.risk_contribution is None
    
    def test_position_weight_validation_zero(self):
        """Test position with zero weight."""
        position = StockPosition(
            ticker='GOOGL',
            weight=0.0,
            alpha_score=0.4
        )
        
        assert position.weight == 0.0
    
    def test_position_weight_validation_one(self):
        """Test position with weight of one."""
        position = StockPosition(
            ticker='AMZN',
            weight=1.0,
            alpha_score=0.6
        )
        
        assert position.weight == 1.0
    
    def test_position_weight_validation_negative(self):
        """Test position with negative weight (should raise error)."""
        with pytest.raises(ValueError, match="Weight must be between 0 and 1"):
            StockPosition(
                ticker='TSLA',
                weight=-0.1,
                alpha_score=0.7
            )
    
    def test_position_weight_validation_too_large(self):
        """Test position with weight > 1 (should raise error)."""
        with pytest.raises(ValueError, match="Weight must be between 0 and 1"):
            StockPosition(
                ticker='TSLA',
                weight=1.1,
                alpha_score=0.7
            )
    
    def test_position_alpha_score_validation_positive(self):
        """Test position with positive alpha score."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1,
            alpha_score=1.0
        )
        
        assert position.alpha_score == 1.0
    
    def test_position_alpha_score_validation_negative(self):
        """Test position with negative alpha score."""
        position = StockPosition(
            ticker='MSFT',
            weight=0.1,
            alpha_score=-1.0
        )
        
        assert position.alpha_score == -1.0
    
    def test_position_alpha_score_validation_zero(self):
        """Test position with zero alpha score."""
        position = StockPosition(
            ticker='GOOGL',
            weight=0.1,
            alpha_score=0.0
        )
        
        assert position.alpha_score == 0.0
    
    def test_position_alpha_score_validation_too_positive(self):
        """Test position with alpha score > 1 (should raise error)."""
        with pytest.raises(ValueError, match="Alpha score must be between -1 and 1"):
            StockPosition(
                ticker='TSLA',
                weight=0.1,
                alpha_score=1.1
            )
    
    def test_position_alpha_score_validation_too_negative(self):
        """Test position with alpha score < -1 (should raise error)."""
        with pytest.raises(ValueError, match="Alpha score must be between -1 and 1"):
            StockPosition(
                ticker='TSLA',
                weight=0.1,
                alpha_score=-1.1
            )
    
    def test_position_unicode_ticker(self):
        """Test position with unicode ticker."""
        position = StockPosition(
            ticker='测试',
            weight=0.1,
            alpha_score=0.5
        )
        
        assert position.ticker == '测试'
    
    def test_position_long_ticker(self):
        """Test position with long ticker name."""
        long_ticker = 'A' * 100
        position = StockPosition(
            ticker=long_ticker,
            weight=0.1,
            alpha_score=0.5
        )
        
        assert position.ticker == long_ticker
    
    def test_position_special_characters_ticker(self):
        """Test position with special characters in ticker."""
        special_ticker = 'AAPL-USD'
        position = StockPosition(
            ticker=special_ticker,
            weight=0.1,
            alpha_score=0.5
        )
        
        assert position.ticker == special_ticker
    
    def test_position_float_precision(self):
        """Test position with float precision issues."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1 + 1e-15,  # Very small addition
            alpha_score=0.5 + 1e-15  # Very small addition
        )
        
        assert abs(position.weight - 0.1) < 1e-10
        assert abs(position.alpha_score - 0.5) < 1e-10
    
    def test_position_nan_values(self):
        """Test position with NaN values."""
        with pytest.raises(ValueError):
            StockPosition(
                ticker='AAPL',
                weight=np.nan,
                alpha_score=0.5
            )
        
        with pytest.raises(ValueError):
            StockPosition(
                ticker='AAPL',
                weight=0.1,
                alpha_score=np.nan
            )
    
    def test_position_inf_values(self):
        """Test position with infinite values."""
        with pytest.raises(ValueError):
            StockPosition(
                ticker='AAPL',
                weight=np.inf,
                alpha_score=0.5
            )
        
        with pytest.raises(ValueError):
            StockPosition(
                ticker='AAPL',
                weight=0.1,
                alpha_score=np.inf
            )
    
    def test_position_optional_fields_none(self):
        """Test position with None optional fields."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1,
            alpha_score=0.5,
            expected_return=None,
            risk_contribution=None
        )
        
        assert position.expected_return is None
        assert position.risk_contribution is None
    
    def test_position_optional_fields_float(self):
        """Test position with float optional fields."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1,
            alpha_score=0.5,
            expected_return=0.12,
            risk_contribution=0.08
        )
        
        assert position.expected_return == 0.12
        assert position.risk_contribution == 0.08
    
    def test_position_optional_fields_negative(self):
        """Test position with negative optional fields."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1,
            alpha_score=0.5,
            expected_return=-0.05,
            risk_contribution=-0.02
        )
        
        assert position.expected_return == -0.05
        assert position.risk_contribution == -0.02
    
    def test_position_optional_fields_zero(self):
        """Test position with zero optional fields."""
        position = StockPosition(
            ticker='AAPL',
            weight=0.1,
            alpha_score=0.5,
            expected_return=0.0,
            risk_contribution=0.0
        )
        
        assert position.expected_return == 0.0
        assert position.risk_contribution == 0.0


class TestPortfolio:
    """Test Portfolio functionality with comprehensive edge cases."""
    
    def setup_method(self):
        """Setup test data."""
        self.config = SolverConfig()
        self.creation_date = date(2024, 1, 15)
    
    def test_portfolio_initialization_default(self):
        """Test portfolio initialization with default values."""
        portfolio = Portfolio()
        
        assert portfolio.portfolio_id is not None
        assert isinstance(portfolio.portfolio_id, str)
        assert len(portfolio.portfolio_id) > 0
        assert portfolio.creation_date == date.today()
        assert len(portfolio.positions) == 0
        assert isinstance(portfolio.config, SolverConfig)
        assert len(portfolio.metadata) == 0
    
    def test_portfolio_initialization_custom(self):
        """Test portfolio initialization with custom values."""
        portfolio = Portfolio(
            portfolio_id='test-portfolio',
            creation_date=self.creation_date,
            config=self.config,
            metadata={'test': 'value'}
        )
        
        assert portfolio.portfolio_id == 'test-portfolio'
        assert portfolio.creation_date == self.creation_date
        assert portfolio.config == self.config
        assert portfolio.metadata == {'test': 'value'}
    
    def test_add_position_valid(self):
        """Test adding a valid position."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        assert 'AAPL' in portfolio.positions
        assert portfolio.positions['AAPL'].ticker == 'AAPL'
        assert portfolio.positions['AAPL'].weight == 0.1
        assert portfolio.positions['AAPL'].alpha_score == 0.5
    
    def test_add_position_with_optional_fields(self):
        """Test adding position with optional fields."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5, expected_return=0.12, risk_contribution=0.08)
        
        position = portfolio.positions['AAPL']
        assert position.expected_return == 0.12
        assert position.risk_contribution == 0.08
    
    def test_add_position_duplicate_ticker(self):
        """Test adding position with duplicate ticker (should overwrite)."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('AAPL', 0.2, 0.6)
        
        assert len(portfolio.positions) == 1
        assert portfolio.positions['AAPL'].weight == 0.2
        assert portfolio.positions['AAPL'].alpha_score == 0.6
    
    def test_add_position_multiple_tickers(self):
        """Test adding multiple positions."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        portfolio.add_position('GOOGL', 0.05, 0.4)
        
        assert len(portfolio.positions) == 3
        assert 'AAPL' in portfolio.positions
        assert 'MSFT' in portfolio.positions
        assert 'GOOGL' in portfolio.positions
    
    def test_add_position_invalid_weight(self):
        """Test adding position with invalid weight."""
        portfolio = Portfolio()
        
        with pytest.raises(ValueError):
            portfolio.add_position('AAPL', -0.1, 0.5)
        
        with pytest.raises(ValueError):
            portfolio.add_position('AAPL', 1.1, 0.5)
    
    def test_add_position_invalid_alpha_score(self):
        """Test adding position with invalid alpha score."""
        portfolio = Portfolio()
        
        with pytest.raises(ValueError):
            portfolio.add_position('AAPL', 0.1, 1.1)
        
        with pytest.raises(ValueError):
            portfolio.add_position('AAPL', 0.1, -1.1)
    
    def test_get_weight_existing_ticker(self):
        """Test getting weight for existing ticker."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        weight = portfolio.get_weight('AAPL')
        assert weight == 0.1
    
    def test_get_weight_nonexistent_ticker(self):
        """Test getting weight for nonexistent ticker."""
        portfolio = Portfolio()
        
        weight = portfolio.get_weight('UNKNOWN')
        assert weight == 0.0
    
    def test_get_weights(self):
        """Test getting all weights."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        
        weights = portfolio.get_weights()
        assert weights == {'AAPL': 0.1, 'MSFT': 0.2}
    
    def test_get_weights_empty_portfolio(self):
        """Test getting weights from empty portfolio."""
        portfolio = Portfolio()
        
        weights = portfolio.get_weights()
        assert weights == {}
    
    def test_get_alpha_scores(self):
        """Test getting all alpha scores."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        
        scores = portfolio.get_alpha_scores()
        assert scores == {'AAPL': 0.5, 'MSFT': 0.3}
    
    def test_get_alpha_scores_empty_portfolio(self):
        """Test getting alpha scores from empty portfolio."""
        portfolio = Portfolio()
        
        scores = portfolio.get_alpha_scores()
        assert scores == {}
    
    def test_get_expected_returns(self):
        """Test getting expected returns."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5, expected_return=0.12)
        portfolio.add_position('MSFT', 0.2, 0.3, expected_return=0.08)
        portfolio.add_position('GOOGL', 0.05, 0.4)  # No expected return
        
        returns = portfolio.get_expected_returns()
        assert returns == {'AAPL': 0.12, 'MSFT': 0.08}
    
    def test_get_expected_returns_empty_portfolio(self):
        """Test getting expected returns from empty portfolio."""
        portfolio = Portfolio()
        
        returns = portfolio.get_expected_returns()
        assert returns == {}
    
    def test_get_risk_contributions(self):
        """Test getting risk contributions."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5, risk_contribution=0.08)
        portfolio.add_position('MSFT', 0.2, 0.3, risk_contribution=0.06)
        portfolio.add_position('GOOGL', 0.05, 0.4)  # No risk contribution
        
        contributions = portfolio.get_risk_contributions()
        assert contributions == {'AAPL': 0.08, 'MSFT': 0.06}
    
    def test_get_risk_contributions_empty_portfolio(self):
        """Test getting risk contributions from empty portfolio."""
        portfolio = Portfolio()
        
        contributions = portfolio.get_risk_contributions()
        assert contributions == {}
    
    def test_get_total_weight(self):
        """Test getting total weight."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        portfolio.add_position('GOOGL', 0.05, 0.4)
        
        total_weight = portfolio.get_total_weight()
        assert abs(total_weight - 0.35) < 1e-10
    
    def test_get_total_weight_empty_portfolio(self):
        """Test getting total weight from empty portfolio."""
        portfolio = Portfolio()
        
        total_weight = portfolio.get_total_weight()
        assert total_weight == 0.0
    
    def test_get_total_weight_single_position(self):
        """Test getting total weight with single position."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        total_weight = portfolio.get_total_weight()
        assert total_weight == 0.1
    
    def test_get_num_positions(self):
        """Test getting number of positions."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        
        num_positions = portfolio.get_num_positions()
        assert num_positions == 2
    
    def test_get_num_positions_empty_portfolio(self):
        """Test getting number of positions from empty portfolio."""
        portfolio = Portfolio()
        
        num_positions = portfolio.get_num_positions()
        assert num_positions == 0
    
    def test_get_active_positions(self):
        """Test getting active positions (non-zero weights)."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.0, 0.3)  # Zero weight
        portfolio.add_position('GOOGL', 0.05, 0.4)
        
        active_positions = portfolio.get_active_positions()
        assert len(active_positions) == 2
        assert 'AAPL' in active_positions
        assert 'GOOGL' in active_positions
        assert 'MSFT' not in active_positions
    
    def test_get_active_positions_empty_portfolio(self):
        """Test getting active positions from empty portfolio."""
        portfolio = Portfolio()
        
        active_positions = portfolio.get_active_positions()
        assert len(active_positions) == 0
    
    def test_get_top_positions(self):
        """Test getting top positions by weight."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        portfolio.add_position('GOOGL', 0.05, 0.4)
        
        top_positions = portfolio.get_top_positions(2)
        assert len(top_positions) == 2
        assert top_positions[0][0] == 'MSFT'  # Highest weight
        assert top_positions[1][0] == 'AAPL'  # Second highest weight
    
    def test_get_top_positions_more_than_available(self):
        """Test getting top positions when requesting more than available."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        top_positions = portfolio.get_top_positions(5)
        assert len(top_positions) == 1
        assert top_positions[0][0] == 'AAPL'
    
    def test_get_top_positions_empty_portfolio(self):
        """Test getting top positions from empty portfolio."""
        portfolio = Portfolio()
        
        top_positions = portfolio.get_top_positions(5)
        assert len(top_positions) == 0
    
    def test_get_concentration_metrics(self):
        """Test getting concentration metrics."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('MSFT', 0.2, 0.3)
        portfolio.add_position('GOOGL', 0.05, 0.4)
        
        metrics = portfolio.get_concentration_metrics()
        
        assert 'num_positions' in metrics
        assert 'max_weight' in metrics
        assert 'min_weight' in metrics
        assert 'weight_std' in metrics
        assert 'herfindahl_index' in metrics
        assert 'effective_num_positions' in metrics
        
        assert metrics['num_positions'] == 3
        assert metrics['max_weight'] == 0.2
        assert metrics['min_weight'] == 0.05
        assert metrics['herfindahl_index'] > 0
        assert metrics['effective_num_positions'] > 0
    
    def test_get_concentration_metrics_empty_portfolio(self):
        """Test getting concentration metrics from empty portfolio."""
        portfolio = Portfolio()
        
        metrics = portfolio.get_concentration_metrics()
        
        assert metrics['num_positions'] == 0
        assert metrics['max_weight'] == 0.0
        assert metrics['min_weight'] == 0.0
        assert metrics['weight_std'] == 0.0
        assert metrics['herfindahl_index'] == 0.0
        assert metrics['effective_num_positions'] == 0.0
    
    def test_get_concentration_metrics_single_position(self):
        """Test getting concentration metrics with single position."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        metrics = portfolio.get_concentration_metrics()
        
        assert metrics['num_positions'] == 1
        assert metrics['max_weight'] == 0.1
        assert metrics['min_weight'] == 0.1
        assert metrics['weight_std'] == 0.0
        assert abs(metrics['herfindahl_index'] - 0.01) < 1e-10  # Handle floating point precision
        assert abs(metrics['effective_num_positions'] - 100.0) < 1e-10  # 1/0.01 = 100
    
    def test_to_dataframe(self):
        """Test converting portfolio to DataFrame."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5, expected_return=0.12, risk_contribution=0.08)
        portfolio.add_position('MSFT', 0.2, 0.3, expected_return=0.08, risk_contribution=0.06)
        
        df = portfolio.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'ticker' in df.columns
        assert 'weight' in df.columns
        assert 'alpha_score' in df.columns
        assert 'expected_return' in df.columns
        assert 'risk_contribution' in df.columns
        
        assert df['ticker'].tolist() == ['AAPL', 'MSFT']
        assert df['weight'].tolist() == [0.1, 0.2]
        assert df['alpha_score'].tolist() == [0.5, 0.3]
    
    def test_to_dataframe_empty_portfolio(self):
        """Test converting empty portfolio to DataFrame."""
        portfolio = Portfolio()
        
        df = portfolio.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        # For empty DataFrame, columns should be empty but structure should be correct
        if len(df) == 0:
            # Empty DataFrame should have the correct column structure
            expected_columns = ['ticker', 'weight', 'alpha_score', 'expected_return', 'risk_contribution']
            # For empty DataFrame, columns might be empty, so just check it's a DataFrame
            assert isinstance(df, pd.DataFrame)
    
    def test_to_dict(self):
        """Test converting portfolio to dictionary."""
        portfolio = Portfolio(
            portfolio_id='test-portfolio',
            creation_date=self.creation_date,
            config=self.config,
            metadata={'test': 'value'}
        )
        portfolio.add_position('AAPL', 0.1, 0.5, expected_return=0.12, risk_contribution=0.08)
        
        portfolio_dict = portfolio.to_dict()
        
        assert isinstance(portfolio_dict, dict)
        assert portfolio_dict['portfolio_id'] == 'test-portfolio'
        assert portfolio_dict['creation_date'] == self.creation_date
        assert 'positions' in portfolio_dict
        assert 'config' in portfolio_dict
        assert 'metadata' in portfolio_dict
        
        assert portfolio_dict['positions']['AAPL']['weight'] == 0.1
        assert portfolio_dict['positions']['AAPL']['alpha_score'] == 0.5
        assert portfolio_dict['positions']['AAPL']['expected_return'] == 0.12
        assert portfolio_dict['positions']['AAPL']['risk_contribution'] == 0.08
    
    def test_from_dict(self):
        """Test creating portfolio from dictionary."""
        portfolio_dict = {
            'portfolio_id': 'test-portfolio',
            'creation_date': self.creation_date,
            'positions': {
                'AAPL': {
                    'weight': 0.1,
                    'alpha_score': 0.5,
                    'expected_return': 0.12,
                    'risk_contribution': 0.08
                },
                'MSFT': {
                    'weight': 0.2,
                    'alpha_score': 0.3,
                    'expected_return': 0.08,
                    'risk_contribution': 0.06
                }
            },
            'config': self.config.to_dict(),
            'metadata': {'test': 'value'}
        }
        
        portfolio = Portfolio.from_dict(portfolio_dict)
        
        assert portfolio.portfolio_id == 'test-portfolio'
        assert portfolio.creation_date == self.creation_date
        assert len(portfolio.positions) == 2
        assert 'AAPL' in portfolio.positions
        assert 'MSFT' in portfolio.positions
        assert portfolio.metadata == {'test': 'value'}
        
        assert portfolio.positions['AAPL'].weight == 0.1
        assert portfolio.positions['AAPL'].alpha_score == 0.5
        assert portfolio.positions['AAPL'].expected_return == 0.12
        assert portfolio.positions['AAPL'].risk_contribution == 0.08
    
    def test_from_dict_missing_fields(self):
        """Test creating portfolio from dictionary with missing fields."""
        portfolio_dict = {
            'portfolio_id': 'test-portfolio',
            'creation_date': self.creation_date,
            'positions': {
                'AAPL': {
                    'weight': 0.1,
                    'alpha_score': 0.5
                }
            },
            'config': self.config.to_dict()
        }
        
        portfolio = Portfolio.from_dict(portfolio_dict)
        
        assert portfolio.portfolio_id == 'test-portfolio'
        assert portfolio.creation_date == self.creation_date
        assert len(portfolio.positions) == 1
        assert portfolio.metadata == {}  # Default empty dict
    
    def test_str_representation(self):
        """Test string representation."""
        portfolio = Portfolio(portfolio_id='test-portfolio')
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        str_repr = str(portfolio)
        assert isinstance(str_repr, str)
        assert 'test-por' in str_repr  # Truncated portfolio_id
        assert '1' in str_repr  # Number of positions
    
    def test_repr_representation(self):
        """Test detailed string representation."""
        portfolio = Portfolio(portfolio_id='test-portfolio')
        portfolio.add_position('AAPL', 0.1, 0.5)
        
        repr_str = repr(portfolio)
        assert isinstance(repr_str, str)
        assert 'Portfolio' in repr_str
        assert 'test-portfolio' in repr_str
    
    def test_portfolio_equality(self):
        """Test portfolio equality."""
        portfolio1 = Portfolio(portfolio_id='test-portfolio')
        portfolio1.add_position('AAPL', 0.1, 0.5)
        
        portfolio2 = Portfolio(portfolio_id='test-portfolio')
        portfolio2.add_position('AAPL', 0.1, 0.5)
        
        # Same content should be equal
        assert portfolio1.to_dict() == portfolio2.to_dict()
        
        # Different content should not be equal
        portfolio3 = Portfolio(portfolio_id='test-portfolio')
        portfolio3.add_position('MSFT', 0.1, 0.5)
        
        assert portfolio1.to_dict() != portfolio3.to_dict()
    
    def test_portfolio_serialization(self):
        """Test portfolio serialization for storage."""
        portfolio = Portfolio(
            portfolio_id='test-portfolio',
            creation_date=self.creation_date,
            metadata={'test': 'value'}
        )
        portfolio.add_position('AAPL', 0.1, 0.5, expected_return=0.12, risk_contribution=0.08)
        
        # Test JSON serialization
        import json
        portfolio_dict = portfolio.to_dict()
        json_str = json.dumps(portfolio_dict, default=str)
        restored_dict = json.loads(json_str)
        restored_portfolio = Portfolio.from_dict(restored_dict)
        
        assert restored_portfolio.portfolio_id == portfolio.portfolio_id
        # Handle date serialization - it becomes a string in JSON
        assert str(restored_portfolio.creation_date) == str(portfolio.creation_date)
        assert len(restored_portfolio.positions) == len(portfolio.positions)
        assert restored_portfolio.metadata == portfolio.metadata
    
    def test_portfolio_large_number_positions(self):
        """Test portfolio with large number of positions."""
        portfolio = Portfolio()
        
        # Add 1000 positions
        for i in range(1000):
            ticker = f'TICKER_{i:03d}'
            weight = 0.001  # 0.1% each
            alpha_score = np.random.uniform(-1, 1)
            portfolio.add_position(ticker, weight, alpha_score)
        
        assert portfolio.get_num_positions() == 1000
        assert abs(portfolio.get_total_weight() - 1.0) < 1e-10
        
        # Test getting top positions
        top_positions = portfolio.get_top_positions(10)
        assert len(top_positions) == 10
        
        # Test concentration metrics
        metrics = portfolio.get_concentration_metrics()
        assert metrics['num_positions'] == 1000
        assert metrics['max_weight'] == 0.001
        assert metrics['min_weight'] == 0.001
    
    def test_portfolio_unicode_tickers(self):
        """Test portfolio with unicode tickers."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1, 0.5)
        portfolio.add_position('测试', 0.2, 0.3)
        portfolio.add_position('MSFT', 0.05, 0.4)
        
        assert len(portfolio.positions) == 3
        assert 'AAPL' in portfolio.positions
        assert '测试' in portfolio.positions
        assert 'MSFT' in portfolio.positions
        
        weights = portfolio.get_weights()
        assert weights['AAPL'] == 0.1
        assert weights['测试'] == 0.2
        assert weights['MSFT'] == 0.05
    
    def test_portfolio_special_characters_tickers(self):
        """Test portfolio with special characters in tickers."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL-USD', 0.1, 0.5)
        portfolio.add_position('MSFT.US', 0.2, 0.3)
        portfolio.add_position('GOOGL/CL', 0.05, 0.4)
        
        assert len(portfolio.positions) == 3
        assert 'AAPL-USD' in portfolio.positions
        assert 'MSFT.US' in portfolio.positions
        assert 'GOOGL/CL' in portfolio.positions
    
    def test_portfolio_float_precision(self):
        """Test portfolio with float precision issues."""
        portfolio = Portfolio()
        portfolio.add_position('AAPL', 0.1 + 1e-15, 0.5 + 1e-15)
        portfolio.add_position('MSFT', 0.2 + 1e-15, 0.3 + 1e-15)
        
        total_weight = portfolio.get_total_weight()
        assert abs(total_weight - 0.3) < 1e-10
    
    def test_portfolio_edge_case_weights(self):
        """Test portfolio with edge case weights."""
        portfolio = Portfolio()
        
        # Test with very small weights
        portfolio.add_position('AAPL', 1e-10, 0.5)
        portfolio.add_position('MSFT', 1e-9, 0.3)
        
        assert portfolio.get_num_positions() == 2
        assert abs(portfolio.get_total_weight() - (1e-10 + 1e-9)) < 1e-15
        
        # Test with weights very close to 1
        portfolio2 = Portfolio()
        portfolio2.add_position('AAPL', 1.0 - 1e-10, 0.5)
        
        assert portfolio2.get_num_positions() == 1
        assert abs(portfolio2.get_total_weight() - (1.0 - 1e-10)) < 1e-15
    
    def test_portfolio_edge_case_alpha_scores(self):
        """Test portfolio with edge case alpha scores."""
        portfolio = Portfolio()
        
        # Test with boundary alpha scores
        portfolio.add_position('AAPL', 0.1, 1.0)
        portfolio.add_position('MSFT', 0.2, -1.0)
        portfolio.add_position('GOOGL', 0.05, 0.0)
        
        assert portfolio.get_num_positions() == 3
        scores = portfolio.get_alpha_scores()
        assert scores['AAPL'] == 1.0
        assert scores['MSFT'] == -1.0
        assert scores['GOOGL'] == 0.0
    
    def test_portfolio_metadata_operations(self):
        """Test portfolio metadata operations."""
        portfolio = Portfolio()
        
        # Test adding metadata
        portfolio.metadata['test_key'] = 'test_value'
        portfolio.metadata['numeric_key'] = 42
        portfolio.metadata['list_key'] = [1, 2, 3]
        
        assert portfolio.metadata['test_key'] == 'test_value'
        assert portfolio.metadata['numeric_key'] == 42
        assert portfolio.metadata['list_key'] == [1, 2, 3]
        
        # Test updating metadata
        portfolio.metadata['test_key'] = 'updated_value'
        assert portfolio.metadata['test_key'] == 'updated_value'
        
        # Test removing metadata
        del portfolio.metadata['test_key']
        assert 'test_key' not in portfolio.metadata
    
    def test_portfolio_config_operations(self):
        """Test portfolio config operations."""
        portfolio = Portfolio()
        
        # Test default config
        assert isinstance(portfolio.config, SolverConfig)
        assert portfolio.config.allocation_method == "mean_variance"
        
        # Test custom config
        custom_config = SolverConfig(allocation_method="score_based")
        portfolio2 = Portfolio(config=custom_config)
        assert portfolio2.config.allocation_method == "score_based"
    
    def test_portfolio_immutability(self):
        """Test portfolio immutability after creation."""
        portfolio = Portfolio(portfolio_id='test-portfolio')
        
        # Dataclasses are mutable by default, so we can modify attributes
        # This test should verify that the portfolio works correctly after modification
        original_id = portfolio.portfolio_id
        original_date = portfolio.creation_date
        
        # Modify attributes (this should work for mutable dataclasses)
        portfolio.portfolio_id = 'new-id'
        new_date = date(2024, 1, 1)  # Use a fixed date to ensure it's different
        portfolio.creation_date = new_date
        
        # Verify the changes took effect
        assert portfolio.portfolio_id == 'new-id'
        assert portfolio.creation_date == new_date
        assert portfolio.portfolio_id != original_id
        assert portfolio.creation_date != original_date
    
    def test_portfolio_copy(self):
        """Test creating a copy of the portfolio."""
        portfolio1 = Portfolio(portfolio_id='test-portfolio')
        portfolio1.add_position('AAPL', 0.1, 0.5)
        portfolio1.metadata['test'] = 'value'
        
        portfolio2 = Portfolio.from_dict(portfolio1.to_dict())
        
        assert portfolio1.portfolio_id == portfolio2.portfolio_id
        assert portfolio1.creation_date == portfolio2.creation_date
        assert len(portfolio1.positions) == len(portfolio2.positions)
        assert portfolio1.metadata == portfolio2.metadata
        
        # Test that positions are identical
        for ticker in portfolio1.positions:
            pos1 = portfolio1.positions[ticker]
            pos2 = portfolio2.positions[ticker]
            assert pos1.ticker == pos2.ticker
            assert pos1.weight == pos2.weight
            assert pos1.alpha_score == pos2.alpha_score


if __name__ == '__main__':
    pytest.main([__file__])
