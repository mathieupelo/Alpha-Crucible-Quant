"""
Signal registry for managing available signals.

Provides a centralized way to register and retrieve signal implementations.
"""

from typing import Dict, List, Type, Optional
import logging

from .base import SignalBase
from .sentiment import SentimentSignal
from .sentiment_yt import SentimentSignalYT

logger = logging.getLogger(__name__)


class SignalRegistry:
    """Registry for managing signal implementations."""
    
    def __init__(self):
        """Initialize the signal registry."""
        self._signals: Dict[str, Type[SignalBase]] = {}
        self._register_default_signals()
    
    def _register_default_signals(self):
        """Register default signal implementations."""
        self.register_signal(SentimentSignal)
        self.register_signal(SentimentSignalYT)
        logger.info("Registered default signals: SENTIMENT, SENTIMENT_YT")
    
    def register_signal(self, signal_class: Type[SignalBase]):
        """
        Register a signal class.
        
        Args:
            signal_class: Signal class to register
        """
        signal_id = signal_class().signal_id
        self._signals[signal_id] = signal_class
        logger.info(f"Registered signal: {signal_id}")
    
    def get_signal(self, signal_id: str, **kwargs) -> Optional[SignalBase]:
        """
        Get a signal instance by ID.
        
        Args:
            signal_id: Signal identifier
            **kwargs: Parameters to pass to signal constructor
            
        Returns:
            Signal instance or None if not found
        """
        if signal_id not in self._signals:
            logger.warning(f"Signal not found: {signal_id}")
            return None
        
        try:
            signal_class = self._signals[signal_id]
            return signal_class(**kwargs)
        except Exception as e:
            logger.error(f"Error creating signal {signal_id}: {e}")
            return None
    
    def get_available_signals(self) -> List[str]:
        """
        Get list of available signal IDs.
        
        Returns:
            List of signal IDs
        """
        return list(self._signals.keys())
    
    def get_signal_info(self, signal_id: str) -> Optional[Dict[str, any]]:
        """
        Get information about a signal.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            Dictionary with signal information or None if not found
        """
        if signal_id not in self._signals:
            return None
        
        try:
            signal_instance = self._signals[signal_id]()
            return {
                'signal_id': signal_instance.signal_id,
                'name': signal_instance.name,
                'parameters': signal_instance.parameters,
                'min_lookback': signal_instance.get_min_lookback_period(),
                'max_lookback': signal_instance.get_max_lookback_period()
            }
        except Exception as e:
            logger.error(f"Error getting signal info for {signal_id}: {e}")
            return None
    
    def get_all_signals_info(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about all available signals.
        
        Returns:
            Dictionary mapping signal IDs to their information
        """
        info = {}
        for signal_id in self._signals:
            signal_info = self.get_signal_info(signal_id)
            if signal_info:
                info[signal_id] = signal_info
        return info
    
    def is_signal_available(self, signal_id: str) -> bool:
        """
        Check if a signal is available.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            True if signal is available, False otherwise
        """
        return signal_id in self._signals
    
    def unregister_signal(self, signal_id: str) -> bool:
        """
        Unregister a signal.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            True if signal was unregistered, False if not found
        """
        if signal_id in self._signals:
            del self._signals[signal_id]
            logger.info(f"Unregistered signal: {signal_id}")
            return True
        return False
    
    def clear_registry(self):
        """Clear all registered signals."""
        self._signals.clear()
        logger.info("Cleared signal registry")
    
    def __len__(self) -> int:
        """Get number of registered signals."""
        return len(self._signals)
    
    def __contains__(self, signal_id: str) -> bool:
        """Check if signal is registered."""
        return signal_id in self._signals
    
    def __iter__(self):
        """Iterate over signal IDs."""
        return iter(self._signals.keys())


# Global signal registry instance
signal_registry = SignalRegistry()
