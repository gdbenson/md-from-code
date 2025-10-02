"""
md-from-code: Convert source code files to MkDocs-compatible markdown pages.

A flexible utility for converting various source code and structured data files
into properly formatted markdown documents suitable for MkDocs documentation sites.
"""

__version__ = "0.1.0"
__author__ = "MAMS Migration System"

from .core import MarkdownGenerator
from .registry import FileTypeRegistry
from .processors import FileProcessor, CodeFileProcessor, StructuredFileProcessor

__all__ = [
    "MarkdownGenerator",
    "FileTypeRegistry",
    "FileProcessor",
    "CodeFileProcessor",
    "StructuredFileProcessor",
]