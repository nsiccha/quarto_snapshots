"""Top-level package for Quarto Snapshots."""

__author__ = """Nikolas Siccha"""
__email__ = 'nikolassiccha@gmail.com'
__version__ = '0.1.0'

from .quarto_snapshots import *

__all__ = [
    "find_and_copy_snapshots",
    "generate",
    "get_parser",
    "handle_args",
    "main"
]