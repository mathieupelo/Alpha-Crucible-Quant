"""
Signal reading system for the Quant Project.

Provides read-only access to computed signals stored in signal_forge.signal_raw.
Signal computation is handled by the separate signals repository.
"""

from .reader import SignalReader
from .registry import SignalRegistry

__all__ = [
    'SignalReader',
    'SignalRegistry'
]
