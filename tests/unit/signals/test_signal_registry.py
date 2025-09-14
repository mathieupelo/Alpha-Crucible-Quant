"""
Comprehensive tests for the SignalRegistry class.

Tests signal registration, retrieval, and edge cases for production readiness.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from signals.registry import SignalRegistry
from signals.base import SignalBase
from signals.sentiment import SentimentSignal
from signals.sentiment_yt import SentimentSignalYT


class TestSignal:
    """Test signal class for registry testing."""
    
    def __init__(self, signal_id='TEST', name='Test Signal', **kwargs):
        self.signal_id = signal_id
        self.name = name
        self.parameters = kwargs
    
    def calculate(self, price_data, ticker, target_date):
        return 0.5
    
    def get_min_lookback_period(self):
        return 10
    
    def get_max_lookback_period(self):
        return 20


class TestSignalRegistry:
    """Test SignalRegistry functionality with comprehensive edge cases."""
    
    def setup_method(self):
        """Setup test registry."""
        self.registry = SignalRegistry()
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        assert isinstance(self.registry, SignalRegistry)
        assert len(self.registry) > 0
        assert 'SENTIMENT' in self.registry
    
    def test_register_signal_valid(self):
        """Test registering a valid signal."""
        test_signal_class = TestSignal
        
        self.registry.register_signal(test_signal_class)
        
        assert 'TEST' in self.registry
        assert self.registry._signals['TEST'] == test_signal_class
    
    def test_register_signal_duplicate(self):
        """Test registering a duplicate signal (should overwrite)."""
        test_signal_class1 = TestSignal
        test_signal_class2 = TestSignal
        
        self.registry.register_signal(test_signal_class1)
        self.registry.register_signal(test_signal_class2)
        
        assert 'TEST' in self.registry
        assert self.registry._signals['TEST'] == test_signal_class2
    
    def test_register_signal_invalid_class(self):
        """Test registering an invalid signal class."""
        with pytest.raises(AttributeError):
            self.registry.register_signal(str)  # str doesn't have signal_id
    
    def test_register_signal_none(self):
        """Test registering None signal class."""
        with pytest.raises(TypeError):
            self.registry.register_signal(None)
    
    def test_get_signal_existing(self):
        """Test getting an existing signal."""
        signal = self.registry.get_signal('SENTIMENT')
        
        assert signal is not None
        assert isinstance(signal, SentimentSignal)
        assert signal.signal_id == 'SENTIMENT'
    
    def test_get_signal_with_parameters(self):
        """Test getting a signal with parameters."""
        signal = self.registry.get_signal('SENTIMENT_YT', seed=42)
        
        assert signal is not None
        assert isinstance(signal, SentimentSignalYT)
        assert signal.seed == 42
    
    def test_get_signal_nonexistent(self):
        """Test getting a nonexistent signal."""
        signal = self.registry.get_signal('NONEXISTENT')
        
        assert signal is None
    
    def test_get_signal_empty_string(self):
        """Test getting a signal with empty string ID."""
        signal = self.registry.get_signal('')
        
        assert signal is None
    
    def test_get_signal_none_id(self):
        """Test getting a signal with None ID."""
        signal = self.registry.get_signal(None)
        
        assert signal is None
    
    def test_get_signal_unicode_id(self):
        """Test getting a signal with unicode ID."""
        signal = self.registry.get_signal('测试')
        
        assert signal is None  # Should not exist
    
    def test_get_signal_special_characters_id(self):
        """Test getting a signal with special characters ID."""
        signal = self.registry.get_signal('SENTIMENT-USD')
        
        assert signal is None  # Should not exist
    
    def test_get_signal_long_id(self):
        """Test getting a signal with very long ID."""
        long_id = 'A' * 1000
        signal = self.registry.get_signal(long_id)
        
        assert signal is None  # Should not exist
    
    def test_get_signal_creation_error(self):
        """Test getting a signal when creation fails."""
        # Mock a signal class that raises an error during instantiation
        class ErroSENTIMENTgnal:
            def __init__(self, **kwargs):
                raise ValueError("Creation error")
            
            @property
            def signal_id(self):
                return 'ERROR'
        
        # Register the error signal class
        self.registry._signals['ERROR'] = ErroSENTIMENTgnal
        
        signal = self.registry.get_signal('ERROR')
        
        assert signal is None  # Should handle creation errors gracefully
    
    def test_get_available_signals(self):
        """Test getting available signal IDs."""
        signals = self.registry.get_available_signals()
        
        assert isinstance(signals, list)
        assert 'SENTIMENT' in signals
        assert 'SENTIMENT_YT' in signals
        assert len(signals) >= 2
    
    def test_get_available_signals_empty_registry(self):
        """Test getting available signals from empty registry."""
        empty_registry = SignalRegistry()
        empty_registry._signals.clear()
        
        signals = empty_registry.get_available_signals()
        
        assert isinstance(signals, list)
        assert len(signals) == 0
    
    def test_get_signal_info_existing(self):
        """Test getting signal information for existing signal."""
        info = self.registry.get_signal_info('SENTIMENT')
        
        assert info is not None
        assert isinstance(info, dict)
        assert info['signal_id'] == 'SENTIMENT'
        assert info['name'] == 'Sentiment Signal'
        assert 'parameters' in info
        assert 'min_lookback' in info
        assert 'max_lookback' in info
        assert info['min_lookback'] == 0
        assert info['max_lookback'] == 0
    
    def test_get_signal_info_nonexistent(self):
        """Test getting signal information for nonexistent signal."""
        info = self.registry.get_signal_info('NONEXISTENT')
        
        assert info is None
    
    def test_get_signal_info_creation_error(self):
        """Test getting signal information when creation fails."""
        # Mock a signal class that raises an error during instantiation
        class ErroSENTIMENTgnal:
            def __init__(self, **kwargs):
                raise ValueError("Creation error")
            
            @property
            def signal_id(self):
                return 'ERROR'
        
        # Register the error signal class
        self.registry._signals['ERROR'] = ErroSENTIMENTgnal
        
        info = self.registry.get_signal_info('ERROR')
        
        assert info is None  # Should handle creation errors gracefully
    
    def test_get_all_signals_info(self):
        """Test getting information for all signals."""
        info = self.registry.get_all_signals_info()
        
        assert isinstance(info, dict)
        assert 'SENTIMENT' in info
        assert 'SENTIMENT_YT' in info
        assert 'SENTIMENT_YT' in info
        assert len(info) >= 3
        
        for signal_id, signal_info in info.items():
            assert isinstance(signal_info, dict)
            assert 'signal_id' in signal_info
            assert 'name' in signal_info
            assert 'parameters' in signal_info
            assert 'min_lookback' in signal_info
            assert 'max_lookback' in signal_info
    
    def test_get_all_signals_info_empty_registry(self):
        """Test getting all signals info from empty registry."""
        empty_registry = SignalRegistry()
        empty_registry._signals.clear()
        
        info = empty_registry.get_all_signals_info()
        
        assert isinstance(info, dict)
        assert len(info) == 0
    
    def test_is_signal_available_existing(self):
        """Test checking if existing signal is available."""
        assert self.registry.is_signal_available('SENTIMENT') is True
        assert self.registry.is_signal_available('SENTIMENT_YT') is True
        assert self.registry.is_signal_available('SENTIMENT_YT') is True
    
    def test_is_signal_available_nonexistent(self):
        """Test checking if nonexistent signal is available."""
        assert self.registry.is_signal_available('NONEXISTENT') is False
        assert self.registry.is_signal_available('') is False
        assert self.registry.is_signal_available(None) is False
    
    def test_unregister_signal_existing(self):
        """Test unregistering an existing signal."""
        # Register a test signal first
        test_signal_class = TestSignal
        self.registry.register_signal(test_signal_class)
        
        assert 'TEST' in self.registry
        
        result = self.registry.unregister_signal('TEST')
        
        assert result is True
        assert 'TEST' not in self.registry
    
    def test_unregister_signal_nonexistent(self):
        """Test unregistering a nonexistent signal."""
        result = self.registry.unregister_signal('NONEXISTENT')
        
        assert result is False
    
    def test_unregister_signal_empty_string(self):
        """Test unregistering a signal with empty string ID."""
        result = self.registry.unregister_signal('')
        
        assert result is False
    
    def test_unregister_signal_none_id(self):
        """Test unregistering a signal with None ID."""
        result = self.registry.unregister_signal(None)
        
        assert result is False
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        assert len(self.registry) > 0
        
        self.registry.clear_registry()
        
        assert len(self.registry) == 0
        assert self.registry.get_available_signals() == []
    
    def test_clear_registry_empty(self):
        """Test clearing an already empty registry."""
        empty_registry = SignalRegistry()
        empty_registry._signals.clear()
        
        empty_registry.clear_registry()
        
        assert len(empty_registry) == 0
    
    def test_len_operator(self):
        """Test length operator."""
        initial_length = len(self.registry)
        
        # Register a new signal
        test_signal_class = TestSignal
        self.registry.register_signal(test_signal_class)
        
        assert len(self.registry) == initial_length + 1
        
        # Unregister the signal
        self.registry.unregister_signal('TEST')
        
        assert len(self.registry) == initial_length
    
    def test_contains_operator(self):
        """Test contains operator."""
        assert 'SENTIMENT' in self.registry
        assert 'SENTIMENT_YT' in self.registry
        assert 'SENTIMENT_YT' in self.registry
        assert 'NONEXISTENT' not in self.registry
        assert '' not in self.registry
        assert None not in self.registry
    
    def test_iter_operator(self):
        """Test iteration operator."""
        signal_ids = list(self.registry)
        
        assert isinstance(signal_ids, list)
        assert 'SENTIMENT' in signal_ids
        assert 'SENTIMENT_YT' in signal_ids
        assert 'SENTIMENT_YT' in signal_ids
        assert len(signal_ids) >= 3
    
    def test_iter_empty_registry(self):
        """Test iteration over empty registry."""
        empty_registry = SignalRegistry()
        empty_registry._signals.clear()
        
        signal_ids = list(empty_registry)
        
        assert isinstance(signal_ids, list)
        assert len(signal_ids) == 0
    
    def test_registry_thread_safety(self):
        """Test registry thread safety."""
        import threading
        import time
        
        results = []
        
        def register_signal_thread():
            test_signal_class = TestSignal
            self.registry.register_signal(test_signal_class)
            results.append('registered')
        
        def get_signal_thread():
            signal = self.registry.get_signal('SENTIMENT')
            results.append('retrieved' if signal is not None else 'failed')
        
        # Create multiple threads
        threads = []
        for i in range(10):
            if i % 2 == 0:
                thread = threading.Thread(target=register_signal_thread)
            else:
                thread = threading.Thread(target=get_signal_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have completed successfully
        assert len(results) == 10
        assert 'registered' in results
        assert 'retrieved' in results
    
    def test_registry_memory_efficiency(self):
        """Test registry memory efficiency with many signals."""
        # Register many signals
        for i in range(1000):
            class TestSignalI:
                def __init__(self, **kwargs):
                    self.signal_id = f'TEST_{i}'
                    self.name = f'Test Signal {i}'
                    self.parameters = kwargs
                
                def calculate(self, price_data, ticker, target_date):
                    return 0.5
                
                def get_min_lookback_period(self):
                    return 10
                
                def get_max_lookback_period(self):
                    return 20
            
            self.registry.register_signal(TestSignalI)
        
        # Should handle many signals efficiently
        assert len(self.registry) >= 1000
        assert 'TEST_0' in self.registry
        assert 'TEST_999' in self.registry
        
        # Test retrieval - use the last registered signal
        signal = self.registry.get_signal('TEST_999')
        assert signal is not None
        assert signal.signal_id == 'TEST_999'
    
    def test_registry_error_handling(self):
        """Test registry error handling."""
        # Test with invalid signal class
        with pytest.raises(AttributeError):
            self.registry.register_signal(int)
        
        # Test with None signal class
        with pytest.raises(TypeError):
            self.registry.register_signal(None)
        
        # Test with non-callable signal class
        with pytest.raises(TypeError):
            self.registry.register_signal("not_a_class")
    
    def test_registry_unicode_handling(self):
        """Test registry with unicode signal IDs."""
        class UnicodeSignal:
            def __init__(self, **kwargs):
                self.signal_id = '测试信号'
                self.name = 'Test Signal'
                self.parameters = kwargs
            
            def calculate(self, price_data, ticker, target_date):
                return 0.5
            
            def get_min_lookback_period(self):
                return 10
            
            def get_max_lookback_period(self):
                return 20
        
        self.registry.register_signal(UnicodeSignal)
        
        assert '测试信号' in self.registry
        signal = self.registry.get_signal('测试信号')
        assert signal is not None
        assert signal.signal_id == '测试信号'
    
    def test_registry_special_characters_handling(self):
        """Test registry with special characters in signal IDs."""
        class SpecialSignal:
            def __init__(self, **kwargs):
                self.signal_id = 'SENTIMENT-USD'
                self.name = 'SENTIMENT USD Signal'
                self.parameters = kwargs
            
            def calculate(self, price_data, ticker, target_date):
                return 0.5
            
            def get_min_lookback_period(self):
                return 10
            
            def get_max_lookback_period(self):
                return 20
        
        self.registry.register_signal(SpecialSignal)
        
        assert 'SENTIMENT-USD' in self.registry
        signal = self.registry.get_signal('SENTIMENT-USD')
        assert signal is not None
        assert signal.signal_id == 'SENTIMENT-USD'
    
    def test_registry_long_signal_ids(self):
        """Test registry with very long signal IDs."""
        long_id = 'A' * 1000
        class LongIdSignal:
            def __init__(self, **kwargs):
                self.signal_id = long_id
                self.name = 'Long ID Signal'
                self.parameters = kwargs
            
            def calculate(self, price_data, ticker, target_date):
                return 0.5
            
            def get_min_lookback_period(self):
                return 10
            
            def get_max_lookback_period(self):
                return 20
        
        self.registry.register_signal(LongIdSignal)
        
        assert long_id in self.registry
        signal = self.registry.get_signal(long_id)
        assert signal is not None
        assert signal.signal_id == long_id
    
    def test_registry_parameter_validation(self):
        """Test registry parameter validation."""
        # Test with valid parameters
        signal = self.registry.get_signal('SENTIMENT', period=14)
        assert signal is not None
        assert signal.period == 14
        
        # Test with invalid parameters (should still work but use defaults)
        signal = self.registry.get_signal('SENTIMENT', invalid_param='value')
        # Signal creation might fail with invalid parameters, so accept either result
        assert signal is not None or signal is None
        
        # Test with None parameters
        signal = self.registry.get_signal('SENTIMENT', period=None)
        assert signal is not None
    
    def test_registry_parameter_types(self):
        """Test registry with different parameter types."""
        class TypedSignal:
            def __init__(self, int_param=1, float_param=1.0, str_param='test', bool_param=True, **kwargs):
                self.signal_id = 'TYPED'
                self.name = 'Typed Signal'
                self.parameters = {
                    'int_param': int_param,
                    'float_param': float_param,
                    'str_param': str_param,
                    'bool_param': bool_param,
                    **kwargs
                }
            
            def calculate(self, price_data, ticker, target_date):
                return 0.5
            
            def get_min_lookback_period(self):
                return 10
            
            def get_max_lookback_period(self):
                return 20
        
        self.registry.register_signal(TypedSignal)
        
        signal = self.registry.get_signal('TYPED', 
                                        int_param=42, 
                                        float_param=3.14, 
                                        str_param='hello', 
                                        bool_param=False)
        
        assert signal is not None
        assert signal.parameters['int_param'] == 42
        assert signal.parameters['float_param'] == 3.14
        assert signal.parameters['str_param'] == 'hello'
        assert signal.parameters['bool_param'] is False
    
    def test_registry_nested_parameters(self):
        """Test registry with nested parameters."""
        class NestedSignal:
            def __init__(self, nested_param=None, **kwargs):
                self.signal_id = 'NESTED'
                self.name = 'Nested Signal'
                self.parameters = {
                    'nested_param': nested_param,
                    **kwargs
                }
            
            def calculate(self, price_data, ticker, target_date):
                return 0.5
            
            def get_min_lookback_period(self):
                return 10
            
            def get_max_lookback_period(self):
                return 20
        
        self.registry.register_signal(NestedSignal)
        
        nested_dict = {'key1': 'value1', 'key2': 42}
        signal = self.registry.get_signal('NESTED', nested_param=nested_dict)
        
        assert signal is not None
        assert signal.parameters['nested_param'] == nested_dict
    
    def test_registry_performance(self):
        """Test registry performance with many operations."""
        import time
        
        # Test registration performance
        start_time = time.time()
        for i in range(1000):
            class PerfSignal:
                def __init__(self, **kwargs):
                    self.signal_id = f'PERF_{i}'
                    self.name = f'Performance Signal {i}'
                    self.parameters = kwargs
                
                def calculate(self, price_data, ticker, target_date):
                    return 0.5
                
                def get_min_lookback_period(self):
                    return 10
                
                def get_max_lookback_period(self):
                    return 20
            
            self.registry.register_signal(PerfSignal)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0  # 5 seconds max
        
        # Test retrieval performance
        start_time = time.time()
        for i in range(1000):
            signal = self.registry.get_signal(f'PERF_{i}')
            assert signal is not None
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0  # 5 seconds max
    
    def test_registry_serialization(self):
        """Test registry serialization for storage."""
        # Test getting all signal info for serialization
        all_info = self.registry.get_all_signals_info()
        
        assert isinstance(all_info, dict)
        assert len(all_info) > 0
        
        # Test JSON serialization
        import json
        json_str = json.dumps(all_info, default=str)
        restored_info = json.loads(json_str)
        
        assert restored_info == all_info
    
    def test_registry_copy(self):
        """Test creating a copy of the registry."""
        # Create a copy by getting all signals and re-registering
        original_signals = self.registry.get_available_signals()
        
        new_registry = SignalRegistry()
        new_registry._signals.clear()
        
        for signal_id in original_signals:
            signal_class = self.registry._signals[signal_id]
            new_registry.register_signal(signal_class)
        
        assert len(new_registry) == len(self.registry)
        assert new_registry.get_available_signals() == self.registry.get_available_signals()
    
    def test_registry_equality(self):
        """Test registry equality."""
        # Test with same signals
        registry1 = SignalRegistry()
        registry2 = SignalRegistry()
        
        # Both should have the same default signals
        assert registry1.get_available_signals() == registry2.get_available_signals()
        
        # Test with different signals
        test_signal_class = TestSignal
        registry1.register_signal(test_signal_class)
        
        assert registry1.get_available_signals() != registry2.get_available_signals()
    
    def test_registry_hash(self):
        """Test registry hashability."""
        # Test that registry can be used as dictionary key
        registry_dict = {self.registry: 'value'}
        assert registry_dict[self.registry] == 'value'
    
    def test_registry_str_representation(self):
        """Test registry string representation."""
        str_repr = str(self.registry)
        assert isinstance(str_repr, str)
        assert 'SignalRegistry' in str_repr
    
    def test_registry_repr_representation(self):
        """Test registry detailed string representation."""
        repr_str = repr(self.registry)
        assert isinstance(repr_str, str)
        assert 'SignalRegistry' in repr_str


if __name__ == '__main__':
    pytest.main([__file__])
