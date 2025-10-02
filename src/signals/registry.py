"""
Dynamic Signal Registry for Alpha-Crucible-Quant

This registry dynamically reads available signals from the database
instead of using hardcoded values.
"""

from typing import Dict, List, Any, Optional
import logging
import sys
from pathlib import Path

# Add src to path to import database manager
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DatabaseManager

logger = logging.getLogger(__name__)

class SignalRegistry:
    """
    Dynamic signal registry that reads available signals from the database.
    
    This registry queries the signal_raw table to get the actual signal types
    that are available in the database.
    """
    
    def __init__(self):
        """Initialize the signal registry with database connection."""
        self.database_manager = DatabaseManager()
        self._signals = {}
        self._load_signals_from_database()
    
    def _load_signals_from_database(self):
        """Load available signals from the database."""
        try:
            if not self.database_manager.is_connected():
                if not self.database_manager.connect():
                    logger.error("Failed to connect to database for signal registry")
                    return
            
            # Get unique signal names from the database
            query = "SELECT DISTINCT signal_name FROM signal_raw ORDER BY signal_name"
            result = self.database_manager.execute_query(query)
            
            if result is not None and not result.empty:
                for _, row in result.iterrows():
                    signal_name = row['signal_name']
                    # Create signal info based on the signal name
                    signal_info = self._create_signal_info(signal_name)
                    self._signals[signal_name.lower()] = signal_info
                    
                logger.info(f"Loaded {len(self._signals)} signals from database: {list(self._signals.keys())}")
            else:
                logger.warning("No signals found in database")
                
        except Exception as e:
            logger.error(f"Error loading signals from database: {e}")
    
    def _create_signal_info(self, signal_name: str) -> Dict[str, Any]:
        """Create signal information based on signal name."""
        # Map signal names to their display names and parameters
        signal_mappings = {
            'SENTIMENT': {
                'name': 'Default Sentiment',
                'parameters': {
                    'lookback_days': 14,
                    'min_articles': 5,
                    'weight_recent': 0.8
                },
                'min_lookback': 3,
                'max_lookback': 30,
                'description': 'Default sentiment analysis signal'
            },
            'SENTIMENT_YT': {
                'name': 'YouTube Sentiment',
                'parameters': {
                    'lookback_days': 30,
                    'min_comments': 10,
                    'weight_recent': 0.7
                },
                'min_lookback': 7,
                'max_lookback': 90,
                'description': 'YouTube comment sentiment analysis signal'
            }
        }
        
        # Get the mapping or create a default one
        mapping = signal_mappings.get(signal_name, {
            'name': signal_name.replace('_', ' ').title(),
            'parameters': {
                'lookback_days': 14,
                'weight_recent': 0.8
            },
            'min_lookback': 3,
            'max_lookback': 30,
            'description': f'{signal_name.replace("_", " ").title()} signal'
        })
        
        return {
            'signal_id': signal_name.lower(),
            'name': mapping['name'],
            'parameters': mapping['parameters'],
            'min_lookback': mapping['min_lookback'],
            'max_lookback': mapping['max_lookback'],
            'description': mapping['description']
        }
    
    def get_available_signals(self) -> List[str]:
        """
        Get list of available signal IDs.
        
        Returns:
            List of signal IDs
        """
        return list(self._signals.keys())
    
    def get_signal_info(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific signal.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            Signal information dictionary or None if not found
        """
        return self._signals.get(signal_id)
    
    def register_signal(self, signal_id: str, signal_info: Dict[str, Any]) -> bool:
        """
        Register a new signal (not supported in dynamic registry).
        
        Args:
            signal_id: Signal identifier
            signal_info: Signal information
            
        Returns:
            False - signals are read from database only
        """
        logger.warning(f"Signal registration not supported in dynamic registry: {signal_id}")
        return False
    
    def get_all_signals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered signals.
        
        Returns:
            Dictionary of all signals
        """
        return self._signals.copy()
    
    def is_signal_available(self, signal_id: str) -> bool:
        """
        Check if a signal is available.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            True if signal is available
        """
        return signal_id in self._signals
    
    def refresh_signals(self):
        """
        Refresh signals from the database.
        
        This method can be called to reload signals if new ones have been added.
        """
        self._signals = {}
        self._load_signals_from_database()
