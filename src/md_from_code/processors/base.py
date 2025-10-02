"""
Base file processor class and common utilities.
"""

import os
import stat
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import chardet


class FileProcessor(ABC):
    """Base class for file processors."""

    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 10MB default
        self.max_file_size = max_file_size

    @abstractmethod
    def process(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Process a file and return content and metadata.

        Args:
            file_path: Path to the file to process
            **kwargs: Additional processing options

        Returns:
            Dictionary containing processed content and metadata
        """
        pass

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata."""
        try:
            file_stat = file_path.stat()

            # Get file permissions
            permissions = stat.filemode(file_stat.st_mode)

            # Format timestamps
            created_time = datetime.fromtimestamp(file_stat.st_ctime)
            modified_time = datetime.fromtimestamp(file_stat.st_mtime)

            return {
                "file_name": file_path.name,
                "file_size": file_stat.st_size,
                "file_size_human": self._format_file_size(file_stat.st_size),
                "permissions": permissions,
                "created": created_time.isoformat(),
                "modified": modified_time.isoformat(),
                "created_human": created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "modified_human": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                "extension": file_path.suffix.lower(),
                "absolute_path": str(file_path.absolute()),
                "relative_path": str(file_path),
                "parent_dir": file_path.parent.name,
            }
        except (OSError, IOError) as e:
            return {
                "file_name": file_path.name,
                "error": f"Could not extract metadata: {str(e)}",
                "file_size": 0,
                "file_size_human": "Unknown",
                "extension": file_path.suffix.lower(),
                "absolute_path": str(file_path.absolute()),
                "relative_path": str(file_path),
            }

    def read_file_content(self, file_path: Path, encoding: Optional[str] = None) -> tuple[str, str]:
        """
        Read file content with encoding detection.

        Returns:
            Tuple of (content, detected_encoding)
        """
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(
                    f"File size ({self._format_file_size(file_size)}) exceeds "
                    f"maximum allowed size ({self._format_file_size(self.max_file_size)})"
                )
        except OSError as e:
            raise IOError(f"Cannot access file: {str(e)}")

        # Detect encoding if not provided
        detected_encoding = encoding
        if not detected_encoding:
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(min(8192, file_size))  # Read up to 8KB for detection
                result = chardet.detect(raw_data)
                detected_encoding = result.get('encoding', 'utf-8')
                if not detected_encoding:
                    detected_encoding = 'utf-8'
            except (OSError, IOError):
                detected_encoding = 'utf-8'

        # Read file content
        try:
            with open(file_path, 'r', encoding=detected_encoding, errors='replace') as f:
                content = f.read()
            return content, detected_encoding
        except UnicodeDecodeError:
            # Fallback to utf-8 with error replacement
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                return content, 'utf-8 (with errors replaced)'
            except (OSError, IOError) as e:
                raise IOError(f"Cannot read file content: {str(e)}")

    def count_lines(self, content: str) -> Dict[str, int]:
        """Count various line statistics."""
        lines = content.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        non_blank_lines = total_lines - blank_lines

        return {
            "total_lines": total_lines,
            "blank_lines": blank_lines,
            "non_blank_lines": non_blank_lines,
        }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _sanitize_content_for_markdown(self, content: str) -> str:
        """Sanitize content to be safe for markdown inclusion."""
        # Escape backticks and other markdown special characters within code blocks
        # This is handled by the template, but we can do basic sanitization here

        # Replace any existing triple backticks to prevent markdown injection
        content = content.replace('```', '``\\`')

        return content

    def _truncate_content(self, content: str, max_lines: Optional[int] = None) -> tuple[str, bool]:
        """
        Truncate content if it exceeds maximum lines.

        Returns:
            Tuple of (possibly_truncated_content, was_truncated)
        """
        if max_lines is None:
            return content, False

        lines = content.splitlines()
        if len(lines) <= max_lines:
            return content, False

        truncated_content = '\n'.join(lines[:max_lines])
        return truncated_content, True