"""
TickTick Linux Widget

A modern desktop widget for displaying TickTick tasks on Linux desktops.
"""

__version__ = "0.1.0"
__author__ = "abdullah"
__email__ = "dev@devosmic.com"

from .backend import api
from .config import settings

__all__ = ["api", "settings"] 