"""
Structured file processor for JSON, XML, YAML, and other data formats.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from .base import FileProcessor


class StructuredFileProcessor(FileProcessor):
    """Processor for structured data files like JSON, XML, YAML."""

    def process(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Process a structured data file.

        Args:
            file_path: Path to the structured file
            **kwargs: Processing options including:
                - max_lines: Maximum lines to include
                - indent: Indentation for pretty-printing (default: 2)
                - encoding: File encoding override
                - validate_structure: Whether to validate file structure

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
                'structure_info': {},
                'was_truncated': False,
                'is_valid': False
            }

        # Process based on file type
        extension = file_path.suffix.lower()
        processed_result = self._process_by_type(
            content, extension, kwargs.get('indent', 2)
        )

        # Truncate if needed
        max_lines = kwargs.get('max_lines')
        final_content, was_truncated = self._truncate_content(
            processed_result['content'], max_lines
        )

        # Calculate line statistics
        line_stats = self.count_lines(content)

        return {
            **metadata,
            'content': final_content,
            'original_content_length': len(content),
            'processed_content_length': len(final_content),
            'encoding': detected_encoding,
            'line_stats': line_stats,
            'structure_info': processed_result['structure_info'],
            'was_truncated': was_truncated,
            'truncated_at_line': max_lines if was_truncated else None,
            'is_valid': processed_result['is_valid'],
            'parsing_error': processed_result.get('parsing_error'),
        }

    def _process_by_type(self, content: str, extension: str, indent: int) -> Dict[str, Any]:
        """Process content based on its type."""

        if extension in ['.json', '.slp']:  # Include .slp as JSON
            return self._process_json(content, indent)
        elif extension in ['.xml']:
            return self._process_xml(content, indent)
        elif extension in ['.yaml', '.yml']:
            return self._process_yaml(content, indent)
        elif extension in ['.toml']:
            return self._process_toml(content)
        elif extension in ['.ini', '.cfg', '.conf', '.properties']:
            return self._process_ini_like(content)
        else:
            # Fallback: treat as plain text but try to detect structure
            return self._process_unknown_structured(content)

    def _process_json(self, content: str, indent: int) -> Dict[str, Any]:
        """Process JSON content with pretty-printing and validation."""
        try:
            # Parse JSON
            parsed_data = json.loads(content)

            # Pretty-print with specified indentation
            pretty_content = json.dumps(parsed_data, indent=indent, ensure_ascii=False, sort_keys=True)

            # Analyze structure
            structure_info = self._analyze_json_structure(parsed_data)

            return {
                'content': pretty_content,
                'structure_info': structure_info,
                'is_valid': True
            }

        except json.JSONDecodeError as e:
            return {
                'content': content,  # Return original content if parsing fails
                'structure_info': {'error': 'Invalid JSON'},
                'is_valid': False,
                'parsing_error': f"JSON parsing error at line {e.lineno}, column {e.colno}: {e.msg}"
            }

    def _process_xml(self, content: str, indent: int) -> Dict[str, Any]:
        """Process XML content with pretty-printing and validation."""
        try:
            # Parse XML
            root = ET.fromstring(content)

            # Pretty-print XML
            self._indent_xml(root, 0, ' ' * indent)
            pretty_content = ET.tostring(root, encoding='unicode', method='xml')

            # Add XML declaration if not present
            if not pretty_content.startswith('<?xml'):
                pretty_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_content

            # Analyze structure
            structure_info = self._analyze_xml_structure(root)

            return {
                'content': pretty_content,
                'structure_info': structure_info,
                'is_valid': True
            }

        except ET.ParseError as e:
            return {
                'content': content,
                'structure_info': {'error': 'Invalid XML'},
                'is_valid': False,
                'parsing_error': f"XML parsing error: {str(e)}"
            }

    def _process_yaml(self, content: str, indent: int) -> Dict[str, Any]:
        """Process YAML content with validation."""
        try:
            # Parse YAML (can handle multiple documents)
            parsed_data = list(yaml.safe_load_all(content))

            # If single document, extract it
            if len(parsed_data) == 1:
                parsed_data = parsed_data[0]

            # Re-dump with consistent formatting
            if isinstance(parsed_data, list) and len(parsed_data) > 1:
                # Multiple documents
                pretty_content = '\n---\n'.join(
                    yaml.dump(doc, default_flow_style=False, indent=indent, sort_keys=True)
                    for doc in parsed_data
                )
            else:
                # Single document
                pretty_content = yaml.dump(
                    parsed_data, default_flow_style=False, indent=indent, sort_keys=True
                )

            # Analyze structure
            structure_info = self._analyze_yaml_structure(parsed_data)

            return {
                'content': pretty_content,
                'structure_info': structure_info,
                'is_valid': True
            }

        except yaml.YAMLError as e:
            return {
                'content': content,
                'structure_info': {'error': 'Invalid YAML'},
                'is_valid': False,
                'parsing_error': f"YAML parsing error: {str(e)}"
            }

    def _process_toml(self, content: str) -> Dict[str, Any]:
        """Process TOML content (basic support)."""
        try:
            import tomllib  # Python 3.11+
            parsed_data = tomllib.loads(content)
            structure_info = self._analyze_dict_structure(parsed_data, 'TOML')
            return {
                'content': content,  # Keep original formatting for TOML
                'structure_info': structure_info,
                'is_valid': True
            }
        except ImportError:
            # Fallback for older Python versions
            return {
                'content': content,
                'structure_info': {'note': 'TOML parsing requires Python 3.11+ or toml library'},
                'is_valid': False,  # Can't validate without parser
                'parsing_error': 'TOML parser not available'
            }
        except Exception as e:
            return {
                'content': content,
                'structure_info': {'error': 'Invalid TOML'},
                'is_valid': False,
                'parsing_error': f"TOML parsing error: {str(e)}"
            }

    def _process_ini_like(self, content: str) -> Dict[str, Any]:
        """Process INI-like configuration files."""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read_string(content)

            # Analyze structure
            structure_info = {
                'type': 'Configuration File',
                'sections': list(config.sections()),
                'section_count': len(config.sections()),
                'total_options': sum(len(config.options(section)) for section in config.sections())
            }

            return {
                'content': content,  # Keep original formatting
                'structure_info': structure_info,
                'is_valid': True
            }

        except Exception as e:
            return {
                'content': content,
                'structure_info': {'error': 'Invalid configuration format'},
                'is_valid': False,
                'parsing_error': f"Configuration parsing error: {str(e)}"
            }

    def _process_unknown_structured(self, content: str) -> Dict[str, Any]:
        """Process unknown structured content with basic analysis."""
        # Try to detect structure patterns
        structure_info = {
            'type': 'Unknown Structured Data',
            'patterns_detected': []
        }

        # Check for common patterns
        if '{' in content and '}' in content:
            structure_info['patterns_detected'].append('JSON-like braces')
        if '<' in content and '>' in content:
            structure_info['patterns_detected'].append('XML-like tags')
        if ':' in content and '\n' in content:
            structure_info['patterns_detected'].append('Key-value pairs')

        return {
            'content': content,
            'structure_info': structure_info,
            'is_valid': None  # Unknown
        }

    def _analyze_json_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze JSON data structure."""
        def analyze_value(value, depth=0):
            if isinstance(value, dict):
                return {
                    'type': 'object',
                    'keys': len(value),
                    'depth': depth,
                    'nested_types': {k: analyze_value(v, depth + 1)['type'] for k, v in value.items()}
                }
            elif isinstance(value, list):
                return {
                    'type': 'array',
                    'length': len(value),
                    'depth': depth,
                    'item_types': [analyze_value(item, depth + 1)['type'] for item in value[:5]]  # Sample first 5
                }
            elif isinstance(value, str):
                return {'type': 'string', 'length': len(value)}
            elif isinstance(value, (int, float)):
                return {'type': 'number', 'value': value}
            elif isinstance(value, bool):
                return {'type': 'boolean', 'value': value}
            elif value is None:
                return {'type': 'null'}
            else:
                return {'type': str(type(value).__name__)}

        analysis = analyze_value(data)
        analysis['format'] = 'JSON'
        return analysis

    def _analyze_xml_structure(self, root: ET.Element) -> Dict[str, Any]:
        """Analyze XML structure."""
        def count_elements(element):
            count = 1  # Count current element
            for child in element:
                count += count_elements(child)
            return count

        def get_depth(element, current_depth=0):
            if not list(element):
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in element)

        return {
            'format': 'XML',
            'root_tag': root.tag,
            'total_elements': count_elements(root),
            'max_depth': get_depth(root),
            'root_attributes': len(root.attrib),
            'namespaces': self._extract_xml_namespaces(root)
        }

    def _analyze_yaml_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze YAML structure."""
        if isinstance(data, list) and len(data) > 1:
            # Multiple documents
            return {
                'format': 'YAML',
                'type': 'multi-document',
                'document_count': len(data),
                'document_types': [str(type(doc).__name__) for doc in data]
            }
        else:
            # Single document
            analysis = self._analyze_dict_structure(data, 'YAML')
            return analysis

    def _analyze_dict_structure(self, data: Any, format_name: str) -> Dict[str, Any]:
        """Analyze dictionary-like data structure."""
        def analyze_depth(obj, current_depth=0):
            if isinstance(obj, dict):
                if not obj:
                    return current_depth
                return max(analyze_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return current_depth
                return max(analyze_depth(item, current_depth + 1) for item in obj)
            else:
                return current_depth

        if isinstance(data, dict):
            return {
                'format': format_name,
                'type': 'object',
                'keys': len(data),
                'max_depth': analyze_depth(data),
                'top_level_keys': list(data.keys())[:10]  # First 10 keys
            }
        elif isinstance(data, list):
            return {
                'format': format_name,
                'type': 'array',
                'length': len(data),
                'max_depth': analyze_depth(data),
                'item_types': [str(type(item).__name__) for item in data[:5]]
            }
        else:
            return {
                'format': format_name,
                'type': str(type(data).__name__),
                'value': str(data)[:100] if isinstance(data, str) else data
            }

    def _indent_xml(self, elem: ET.Element, level: int = 0, indent_str: str = "  ") -> None:
        """Add pretty-printing indentation to XML element."""
        i = "\n" + level * indent_str
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + indent_str
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1, indent_str)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _extract_xml_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """Extract XML namespaces from root element."""
        namespaces = {}
        for key, value in root.attrib.items():
            if key.startswith('xmlns'):
                prefix = key.split(':', 1)[1] if ':' in key else 'default'
                namespaces[prefix] = value
        return namespaces