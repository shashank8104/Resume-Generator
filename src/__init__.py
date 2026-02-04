"""
Resume Intelligence System

A production-grade ML-driven resume intelligence system.
"""

__version__ = "1.0.0"
__author__ = "Resume Intelligence Team"

from .utils.config_loader import load_config
from .utils.logging_utils import get_logger

__all__ = ["load_config", "get_logger"]