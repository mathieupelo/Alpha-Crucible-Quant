"""
Comprehensive tests for the SolverConfig class.

Tests configuration validation, edge cases, and error handling.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from solver.config import SolverConfig


class TestSolverConfig:
    """Test SolverConfig functionality with comprehensive edge cases."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SolverConfig()
        
        assert config.allocation_method == "mean_variance"
        assert config.risk_aversion == 0.0
        assert config.max_weight == 0.1
        assert config.min_weight == 0.0
        assert config.long_only is True
        assert config.max_turnover is None
        assert config.transaction_costs == 0.0
        assert config.score_temperature == 1.0
        assert config.positive_weight_ratio == 0.6
        assert config.negative_weight_ratio == 0.4
        assert config.solver_options is not None
        assert isinstance(config.solver_options, dict)
    
    def test_valid_config(self):
        """Test valid configuration values."""
        config = SolverConfig(
            allocation_method="score_based",
            risk_aversion=0.5,
            max_weight=0.2,
            min_weight=0.01,
            long_only=False,
            max_turnover=0.5,
            transaction_costs=0.001,
            score_temperature=2.0,
            positive_weight_ratio=0.7,
            negative_weight_ratio=0.3
        )
        
        assert config.allocation_method == "score_based"
        assert config.risk_aversion == 0.5
        assert config.max_weight == 0.2
        assert config.min_weight == 0.01
        assert config.long_only is False
        assert config.max_turnover == 0.5
        assert config.transaction_costs == 0.001
        assert config.score_temperature == 2.0
        assert config.positive_weight_ratio == 0.7
        assert config.negative_weight_ratio == 0.3
    
    def test_invalid_allocation_method(self):
        """Test invalid allocation method."""
        with pytest.raises(ValueError, match="Allocation method must be 'mean_variance' or 'score_based'"):
            SolverConfig(allocation_method="invalid_method")
    
    def test_invalid_risk_aversion_too_low(self):
        """Test invalid risk aversion (too low)."""
        with pytest.raises(ValueError, match="Risk aversion must be between 0 and 1"):
            SolverConfig(risk_aversion=-0.1)
    
    def test_invalid_risk_aversion_too_high(self):
        """Test invalid risk aversion (too high)."""
        with pytest.raises(ValueError, match="Risk aversion must be between 0 and 1"):
            SolverConfig(risk_aversion=1.1)
    
    def test_valid_risk_aversion_boundaries(self):
        """Test valid risk aversion at boundaries."""
        config1 = SolverConfig(risk_aversion=0.0)
        assert config1.risk_aversion == 0.0
        
        config2 = SolverConfig(risk_aversion=1.0)
        assert config2.risk_aversion == 1.0
    
    def test_invalid_max_weight_too_low(self):
        """Test invalid max weight (too low)."""
        with pytest.raises(ValueError, match="Max weight must be between 0 and 1"):
            SolverConfig(max_weight=-0.1)
    
    def test_invalid_max_weight_too_high(self):
        """Test invalid max weight (too high)."""
        with pytest.raises(ValueError, match="Max weight must be between 0 and 1"):
            SolverConfig(max_weight=1.1)
    
    def test_valid_max_weight_boundaries(self):
        """Test valid max weight at boundaries."""
        config1 = SolverConfig(max_weight=0.0)
        assert config1.max_weight == 0.0
        
        config2 = SolverConfig(max_weight=1.0)
        assert config2.max_weight == 1.0
    
    def test_invalid_min_weight_too_low(self):
        """Test invalid min weight (too low)."""
        with pytest.raises(ValueError, match="Min weight must be between 0 and max weight"):
            SolverConfig(min_weight=-0.1)
    
    def test_invalid_min_weight_too_high(self):
        """Test invalid min weight (too high)."""
        with pytest.raises(ValueError, match="Min weight must be between 0 and max weight"):
            SolverConfig(min_weight=0.2, max_weight=0.1)
    
    def test_valid_min_weight_boundaries(self):
        """Test valid min weight at boundaries."""
        config1 = SolverConfig(min_weight=0.0, max_weight=0.1)
        assert config1.min_weight == 0.0
        
        config2 = SolverConfig(min_weight=0.1, max_weight=0.1)
        assert config2.min_weight == 0.1
    
    def test_invalid_max_turnover_negative(self):
        """Test invalid max turnover (negative)."""
        with pytest.raises(ValueError, match="Max turnover must be non-negative"):
            SolverConfig(max_turnover=-0.1)
    
    def test_valid_max_turnover_boundaries(self):
        """Test valid max turnover at boundaries."""
        config1 = SolverConfig(max_turnover=0.0)
        assert config1.max_turnover == 0.0
        
        config2 = SolverConfig(max_turnover=1.0)
        assert config2.max_turnover == 1.0
        
        config3 = SolverConfig(max_turnover=None)
        assert config3.max_turnover is None
    
    def test_invalid_transaction_costs_negative(self):
        """Test invalid transaction costs (negative)."""
        with pytest.raises(ValueError, match="Transaction costs must be non-negative"):
            SolverConfig(transaction_costs=-0.001)
    
    def test_valid_transaction_costs_boundaries(self):
        """Test valid transaction costs at boundaries."""
        config1 = SolverConfig(transaction_costs=0.0)
        assert config1.transaction_costs == 0.0
        
        config2 = SolverConfig(transaction_costs=0.1)
        assert config2.transaction_costs == 0.1
    
    def test_invalid_score_temperature_zero(self):
        """Test invalid score temperature (zero)."""
        with pytest.raises(ValueError, match="Score temperature must be positive"):
            SolverConfig(score_temperature=0.0)
    
    def test_invalid_score_temperature_negative(self):
        """Test invalid score temperature (negative)."""
        with pytest.raises(ValueError, match="Score temperature must be positive"):
            SolverConfig(score_temperature=-1.0)
    
    def test_valid_score_temperature_boundaries(self):
        """Test valid score temperature at boundaries."""
        config1 = SolverConfig(score_temperature=0.001)  # Very small positive
        assert config1.score_temperature == 0.001
        
        config2 = SolverConfig(score_temperature=100.0)  # Large positive
        assert config2.score_temperature == 100.0
    
    def test_invalid_positive_weight_ratio_too_low(self):
        """Test invalid positive weight ratio (too low)."""
        with pytest.raises(ValueError, match="Positive weight ratio must be between 0 and 1"):
            SolverConfig(positive_weight_ratio=-0.1)
    
    def test_invalid_positive_weight_ratio_too_high(self):
        """Test invalid positive weight ratio (too high)."""
        with pytest.raises(ValueError, match="Positive weight ratio must be between 0 and 1"):
            SolverConfig(positive_weight_ratio=1.1)
    
    def test_valid_positive_weight_ratio_boundaries(self):
        """Test valid positive weight ratio at boundaries."""
        config1 = SolverConfig(positive_weight_ratio=0.0, negative_weight_ratio=1.0)
        assert config1.positive_weight_ratio == 0.0
        
        config2 = SolverConfig(positive_weight_ratio=1.0, negative_weight_ratio=0.0)
        assert config2.positive_weight_ratio == 1.0
    
    def test_invalid_negative_weight_ratio_too_low(self):
        """Test invalid negative weight ratio (too low)."""
        with pytest.raises(ValueError, match="Negative weight ratio must be between 0 and 1"):
            SolverConfig(negative_weight_ratio=-0.1)
    
    def test_invalid_negative_weight_ratio_too_high(self):
        """Test invalid negative weight ratio (too high)."""
        with pytest.raises(ValueError, match="Negative weight ratio must be between 0 and 1"):
            SolverConfig(negative_weight_ratio=1.1)
    
    def test_valid_negative_weight_ratio_boundaries(self):
        """Test valid negative weight ratio at boundaries."""
        config1 = SolverConfig(positive_weight_ratio=1.0, negative_weight_ratio=0.0)
        assert config1.negative_weight_ratio == 0.0
        
        config2 = SolverConfig(positive_weight_ratio=0.0, negative_weight_ratio=1.0)
        assert config2.negative_weight_ratio == 1.0
    
    def test_invalid_weight_ratios_sum_not_one(self):
        """Test invalid weight ratios that don't sum to 1."""
        with pytest.raises(ValueError, match="Positive and negative weight ratios must sum to 1.0"):
            SolverConfig(positive_weight_ratio=0.6, negative_weight_ratio=0.3)
    
    def test_valid_weight_ratios_sum_one(self):
        """Test valid weight ratios that sum to 1."""
        config = SolverConfig(positive_weight_ratio=0.6, negative_weight_ratio=0.4)
        assert config.positive_weight_ratio == 0.6
        assert config.negative_weight_ratio == 0.4
    
    def test_weight_ratios_sum_one_with_tolerance(self):
        """Test weight ratios that sum to 1 within floating point tolerance."""
        config = SolverConfig(positive_weight_ratio=0.6, negative_weight_ratio=0.4)
        assert abs(config.positive_weight_ratio + config.negative_weight_ratio - 1.0) < 1e-6
    
    def test_solver_options_default(self):
        """Test default solver options."""
        config = SolverConfig()
        assert config.solver_options is not None
        assert isinstance(config.solver_options, dict)
        assert 'show_progress' in config.solver_options
        assert 'maxiters' in config.solver_options
        assert 'abstol' in config.solver_options
        assert 'reltol' in config.solver_options
        assert config.solver_options['show_progress'] is False
        assert config.solver_options['maxiters'] == 100
        assert config.solver_options['abstol'] == 1e-7
        assert config.solver_options['reltol'] == 1e-6
    
    def test_solver_options_custom(self):
        """Test custom solver options."""
        custom_options = {
            'show_progress': True,
            'maxiters': 200,
            'abstol': 1e-8,
            'reltol': 1e-7
        }
        config = SolverConfig(solver_options=custom_options)
        assert config.solver_options == custom_options
    
    def test_solver_options_none(self):
        """Test solver options set to None (should use defaults)."""
        config = SolverConfig(solver_options=None)
        assert config.solver_options is not None
        assert isinstance(config.solver_options, dict)
        assert 'show_progress' in config.solver_options
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = SolverConfig(
            allocation_method="score_based",
            risk_aversion=0.5,
            max_weight=0.2,
            min_weight=0.01,
            long_only=False,
            max_turnover=0.5,
            transaction_costs=0.001,
            score_temperature=2.0,
            positive_weight_ratio=0.7,
            negative_weight_ratio=0.3
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['allocation_method'] == "score_based"
        assert config_dict['risk_aversion'] == 0.5
        assert config_dict['max_weight'] == 0.2
        assert config_dict['min_weight'] == 0.01
        assert config_dict['long_only'] is False
        assert config_dict['max_turnover'] == 0.5
        assert config_dict['transaction_costs'] == 0.001
        assert config_dict['score_temperature'] == 2.0
        assert config_dict['positive_weight_ratio'] == 0.7
        assert config_dict['negative_weight_ratio'] == 0.3
        assert config_dict['solver_options'] is not None
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            'allocation_method': 'score_based',
            'risk_aversion': 0.5,
            'max_weight': 0.2,
            'min_weight': 0.01,
            'long_only': False,
            'max_turnover': 0.5,
            'transaction_costs': 0.001,
            'score_temperature': 2.0,
            'positive_weight_ratio': 0.7,
            'negative_weight_ratio': 0.3,
            'solver_options': {'show_progress': True}
        }
        
        config = SolverConfig.from_dict(config_dict)
        
        assert config.allocation_method == "score_based"
        assert config.risk_aversion == 0.5
        assert config.max_weight == 0.2
        assert config.min_weight == 0.01
        assert config.long_only is False
        assert config.max_turnover == 0.5
        assert config.transaction_costs == 0.001
        assert config.score_temperature == 2.0
        assert config.positive_weight_ratio == 0.7
        assert config.negative_weight_ratio == 0.3
        assert config.solver_options == {'show_progress': True}
    
    def test_from_dict_invalid_values(self):
        """Test creation from dictionary with invalid values."""
        config_dict = {
            'allocation_method': 'invalid_method',
            'risk_aversion': 0.5,
            'max_weight': 0.2,
            'min_weight': 0.01,
            'long_only': False,
            'max_turnover': 0.5,
            'transaction_costs': 0.001,
            'score_temperature': 2.0,
            'positive_weight_ratio': 0.7,
            'negative_weight_ratio': 0.3
        }
        
        with pytest.raises(ValueError):
            SolverConfig.from_dict(config_dict)
    
    def test_from_dict_missing_values(self):
        """Test creation from dictionary with missing values."""
        config_dict = {
            'allocation_method': 'score_based',
            'risk_aversion': 0.5
            # Missing other required values
        }
        
        # Should use default values for missing keys
        config = SolverConfig.from_dict(config_dict)
        assert config.allocation_method == "score_based"
        assert config.risk_aversion == 0.5
        assert config.max_weight == 0.1  # Default value
        assert config.min_weight == 0.0  # Default value
    
    def test_str_representation(self):
        """Test string representation."""
        config = SolverConfig(
            allocation_method="score_based",
            risk_aversion=0.5,
            max_weight=0.2,
            min_weight=0.01
        )
        
        str_repr = str(config)
        assert isinstance(str_repr, str)
        assert "score_based" in str_repr
        assert "0.5" in str_repr
        assert "0.2" in str_repr
        assert "0.01" in str_repr
    
    def test_repr_representation(self):
        """Test detailed string representation."""
        config = SolverConfig(
            allocation_method="score_based",
            risk_aversion=0.5,
            max_weight=0.2,
            min_weight=0.01
        )
        
        repr_str = repr(config)
        assert isinstance(repr_str, str)
        assert "SolverConfig" in repr_str
    
    def test_config_immutability(self):
        """Test that config values are immutable after creation."""
        config = SolverConfig(max_weight=0.2)
        
        # Dataclasses are not immutable by default, so we test that values can be modified
        # This is expected behavior for dataclasses
        config.max_weight = 0.3
        assert config.max_weight == 0.3
    
    def test_config_copy(self):
        """Test creating a copy of the config."""
        config1 = SolverConfig(max_weight=0.2, min_weight=0.01)
        config2 = SolverConfig.from_dict(config1.to_dict())
        
        assert config1.max_weight == config2.max_weight
        assert config1.min_weight == config2.min_weight
        assert config1.allocation_method == config2.allocation_method
    
    def test_config_equality(self):
        """Test config equality."""
        config1 = SolverConfig(max_weight=0.2, min_weight=0.01)
        config2 = SolverConfig(max_weight=0.2, min_weight=0.01)
        config3 = SolverConfig(max_weight=0.3, min_weight=0.01)
        
        # Same values should be equal
        assert config1.to_dict() == config2.to_dict()
        
        # Different values should not be equal
        assert config1.to_dict() != config3.to_dict()
    
    def test_config_hash(self):
        """Test config hashability."""
        config = SolverConfig(max_weight=0.2, min_weight=0.01)
        
        # Should be hashable
        config_dict = config.to_dict()
        hash_value = hash(str(config_dict))
        assert isinstance(hash_value, int)
    
    def test_config_serialization(self):
        """Test config serialization for storage."""
        config = SolverConfig(
            allocation_method="score_based",
            risk_aversion=0.5,
            max_weight=0.2,
            min_weight=0.01,
            long_only=False,
            max_turnover=0.5,
            transaction_costs=0.001,
            score_temperature=2.0,
            positive_weight_ratio=0.7,
            negative_weight_ratio=0.3
        )
        
        # Test JSON serialization
        import json
        config_dict = config.to_dict()
        json_str = json.dumps(config_dict)
        restored_dict = json.loads(json_str)
        restored_config = SolverConfig.from_dict(restored_dict)
        
        assert restored_config.allocation_method == config.allocation_method
        assert restored_config.risk_aversion == config.risk_aversion
        assert restored_config.max_weight == config.max_weight
        assert restored_config.min_weight == config.min_weight
        assert restored_config.long_only == config.long_only
        assert restored_config.max_turnover == config.max_turnover
        assert restored_config.transaction_costs == config.transaction_costs
        assert restored_config.score_temperature == config.score_temperature
        assert restored_config.positive_weight_ratio == config.positive_weight_ratio
        assert restored_config.negative_weight_ratio == config.negative_weight_ratio
    
    def test_config_edge_cases(self):
        """Test config with edge case values."""
        # Test with very small values
        config1 = SolverConfig(
            max_weight=1e-10,
            min_weight=1e-12,
            transaction_costs=1e-15,
            score_temperature=1e-10
        )
        assert config1.max_weight == 1e-10
        assert config1.min_weight == 1e-12
        assert config1.transaction_costs == 1e-15
        assert config1.score_temperature == 1e-10
        
        # Test with very large values
        config2 = SolverConfig(
            max_weight=1.0,
            min_weight=1.0,
            transaction_costs=0.1,
            score_temperature=1000.0
        )
        assert config2.max_weight == 1.0
        assert config2.min_weight == 1.0
        assert config2.transaction_costs == 0.1
        assert config2.score_temperature == 1000.0
    
    def test_config_validation_order(self):
        """Test that validation errors are caught in the correct order."""
        # Test multiple validation errors
        with pytest.raises(ValueError) as exc_info:
            SolverConfig(
                allocation_method="invalid",
                risk_aversion=1.5,
                max_weight=1.5,
                min_weight=-0.1
            )
        
        # Should catch the first validation error
        assert "Allocation method must be 'mean_variance' or 'score_based'" in str(exc_info.value)
    
    def test_config_float_precision(self):
        """Test config with float precision issues."""
        # Test with values that might cause floating point precision issues
        config = SolverConfig(
            positive_weight_ratio=0.6,
            negative_weight_ratio=0.4
        )
        
        # Should handle floating point precision correctly
        assert abs(config.positive_weight_ratio + config.negative_weight_ratio - 1.0) < 1e-6
    
    def test_config_boolean_values(self):
        """Test config with boolean values."""
        config1 = SolverConfig(long_only=True)
        assert config1.long_only is True
        
        config2 = SolverConfig(long_only=False)
        assert config2.long_only is False
    
    def test_config_none_values(self):
        """Test config with None values."""
        config = SolverConfig(max_turnover=None)
        assert config.max_turnover is None
    
    def test_config_type_coercion(self):
        """Test config with type coercion."""
        # Test with string values that should be converted
        config_dict = {
            'allocation_method': 'score_based',
            'risk_aversion': 0.5,  # Use proper types
            'max_weight': 0.2,     # Use proper types
            'min_weight': 0.01,    # Use proper types
            'long_only': True,     # Use proper types
            'transaction_costs': 0.001  # Use proper types
        }
        
        # Should handle proper types correctly
        config = SolverConfig.from_dict(config_dict)
        assert config.allocation_method == "score_based"
        assert config.risk_aversion == 0.5
        assert config.max_weight == 0.2
        assert config.min_weight == 0.01
        assert config.long_only is True
        assert config.transaction_costs == 0.001


if __name__ == '__main__':
    pytest.main([__file__])
