"""
Code file processor for programming languages and scripts.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base import FileProcessor


class CodeFileProcessor(FileProcessor):
    """Processor for programming language files."""

    def process(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Process a code file.

        Args:
            file_path: Path to the code file
            **kwargs: Processing options including:
                - max_lines: Maximum lines to include
                - include_line_numbers: Whether to include line numbers
                - encoding: File encoding override

        Returns:
            Dictionary with processed content and metadata
        """
        # Extract basic metadata
        metadata = self.extract_metadata(file_path)

        # Read file content
        try:
            content, detected_encoding = self.read_file_content(
                file_path, kwargs.get('encoding')
            )
        except (IOError, ValueError) as e:
            return {
                **metadata,
                'content': '',
                'error': str(e),
                'encoding': 'unknown',
                'line_stats': {'total_lines': 0, 'blank_lines': 0, 'non_blank_lines': 0},
                'language_stats': {},
                'was_truncated': False
            }

        # Sanitize content for markdown
        sanitized_content = self._sanitize_content_for_markdown(content)

        # Truncate if needed
        max_lines = kwargs.get('max_lines')
        final_content, was_truncated = self._truncate_content(sanitized_content, max_lines)

        # Calculate line statistics
        line_stats = self.count_lines(content)

        # Extract language-specific information
        language_stats = self._analyze_code_structure(content, file_path.suffix)

        return {
            **metadata,
            'content': final_content,
            'original_content_length': len(content),
            'processed_content_length': len(final_content),
            'encoding': detected_encoding,
            'line_stats': line_stats,
            'language_stats': language_stats,
            'was_truncated': was_truncated,
            'truncated_at_line': max_lines if was_truncated else None,
        }

    def _analyze_code_structure(self, content: str, extension: str) -> Dict[str, Any]:
        """Analyze code structure for language-specific insights."""
        lines = content.splitlines()
        stats = {
            'comment_lines': 0,
            'import_statements': 0,
            'function_definitions': 0,
            'class_definitions': 0,
            'docstring_blocks': 0,
        }

        # Define patterns based on file extension
        patterns = self._get_language_patterns(extension.lower())

        # Count occurrences
        in_multiline_comment = False
        multiline_comment_start = patterns.get('multiline_comment_start')
        multiline_comment_end = patterns.get('multiline_comment_end')

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # Handle multiline comments
            if multiline_comment_start and multiline_comment_end:
                if multiline_comment_start in stripped_line:
                    in_multiline_comment = True
                if in_multiline_comment:
                    stats['comment_lines'] += 1
                if multiline_comment_end in stripped_line:
                    in_multiline_comment = False
                    continue

            if in_multiline_comment:
                continue

            # Single line comments
            if patterns.get('single_line_comment') and any(
                stripped_line.startswith(comment)
                for comment in patterns['single_line_comment']
            ):
                stats['comment_lines'] += 1
                continue

            # Import statements
            if patterns.get('import_patterns'):
                for pattern in patterns['import_patterns']:
                    if re.match(pattern, stripped_line):
                        stats['import_statements'] += 1
                        break

            # Function definitions
            if patterns.get('function_patterns'):
                for pattern in patterns['function_patterns']:
                    if re.match(pattern, stripped_line):
                        stats['function_definitions'] += 1
                        break

            # Class definitions
            if patterns.get('class_patterns'):
                for pattern in patterns['class_patterns']:
                    if re.match(pattern, stripped_line):
                        stats['class_definitions'] += 1
                        break

            # Docstrings (Python-specific for now)
            if extension.lower() == '.py' and ('"""' in stripped_line or "'''" in stripped_line):
                stats['docstring_blocks'] += 1

        # Calculate percentages
        total_content_lines = stats['comment_lines'] + len([
            line for line in lines
            if line.strip() and not self._is_comment_line(line.strip(), patterns)
        ])

        if total_content_lines > 0:
            stats['comment_percentage'] = round((stats['comment_lines'] / total_content_lines) * 100, 1)
        else:
            stats['comment_percentage'] = 0.0

        return stats

    def _get_language_patterns(self, extension: str) -> Dict[str, Any]:
        """Get regex patterns for different programming languages."""

        patterns_map = {
            '.py': {
                'single_line_comment': ['#'],
                'multiline_comment_start': '"""',
                'multiline_comment_end': '"""',
                'import_patterns': [r'^(import\s+\w+|from\s+\w+\s+import)'],
                'function_patterns': [r'^def\s+\w+\s*\('],
                'class_patterns': [r'^class\s+\w+'],
            },
            '.java': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^import\s+[\w.]+;'],
                'function_patterns': [r'^\s*(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\('],
                'class_patterns': [r'^(public\s+)?(abstract\s+)?class\s+\w+'],
            },
            '.js': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^(import\s+.*from|const\s+.*=\s*require)'],
                'function_patterns': [r'^(function\s+\w+|const\s+\w+\s*=.*=>|\w+\s*:\s*function)'],
                'class_patterns': [r'^class\s+\w+'],
            },
            '.ts': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^import\s+.*from'],
                'function_patterns': [r'^(function\s+\w+|const\s+\w+\s*=.*=>|\w+\s*:\s*\(.*\)\s*=>)'],
                'class_patterns': [r'^(export\s+)?(abstract\s+)?class\s+\w+'],
            },
            '.c': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^#include\s*[<"]'],
                'function_patterns': [r'^\w+\s+\w+\s*\(.*\)\s*{?$'],
                'class_patterns': [],  # C doesn't have classes
            },
            '.cpp': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^#include\s*[<"]'],
                'function_patterns': [r'^\w+\s+\w+\s*\(.*\)\s*{?$'],
                'class_patterns': [r'^class\s+\w+'],
            },
            '.go': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^import\s+[(".]'],
                'function_patterns': [r'^func\s+(\w+\s+)?\w+\s*\('],
                'class_patterns': [r'^type\s+\w+\s+struct'],
            },
            '.rs': {
                'single_line_comment': ['//'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [r'^use\s+[\w:]+'],
                'function_patterns': [r'^(pub\s+)?fn\s+\w+'],
                'class_patterns': [r'^(pub\s+)?struct\s+\w+'],
            },
            '.sh': {
                'single_line_comment': ['#'],
                'import_patterns': [r'^(source\s+|\.?\s+)'],
                'function_patterns': [r'^\w+\s*\(\s*\)\s*{'],
                'class_patterns': [],
            },
            '.sql': {
                'single_line_comment': ['--'],
                'multiline_comment_start': '/*',
                'multiline_comment_end': '*/',
                'import_patterns': [],
                'function_patterns': [r'^(CREATE\s+)?(FUNCTION|PROCEDURE)\s+\w+'],
                'class_patterns': [],  # SQL doesn't have classes
            },
        }

        return patterns_map.get(extension, {
            'single_line_comment': ['#', '//', '--'],
            'import_patterns': [],
            'function_patterns': [],
            'class_patterns': [],
        })

    def _is_comment_line(self, line: str, patterns: Dict[str, Any]) -> bool:
        """Check if a line is a comment."""
        if not patterns.get('single_line_comment'):
            return False

        return any(line.startswith(comment) for comment in patterns['single_line_comment'])