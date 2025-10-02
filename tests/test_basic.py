"""
Basic tests for md-from-code functionality.
"""

import tempfile
from pathlib import Path
import pytest

from md_from_code import MarkdownGenerator, FileTypeRegistry


class TestFileTypeRegistry:
    """Test the file type registry."""

    def test_basic_registration(self):
        registry = FileTypeRegistry()
        extensions = registry.get_supported_extensions()
        assert '.py' in extensions
        assert '.json' in extensions
        assert '.xml' in extensions

    def test_type_info_retrieval(self):
        registry = FileTypeRegistry()

        # Test Python file
        py_info = registry.get_type_info('.py')
        assert py_info.name == 'Python'
        assert py_info.highlight_lang == 'python'
        assert py_info.processor_type == 'code'

        # Test JSON file
        json_info = registry.get_type_info('.json')
        assert json_info.name == 'JSON'
        assert json_info.highlight_lang == 'json'
        assert json_info.processor_type == 'structured'

    def test_format_override(self):
        registry = FileTypeRegistry()

        # Test .slp file with JSON override
        slp_info = registry.get_type_info('.slp', 'json')
        assert 'JSON' in slp_info.name
        assert slp_info.highlight_lang == 'json'
        assert slp_info.processor_type == 'structured'

    def test_unknown_extension(self):
        registry = FileTypeRegistry()
        unknown_info = registry.get_type_info('.unknown')
        assert unknown_info.name == 'Text File'
        assert unknown_info.highlight_lang == 'text'


class TestMarkdownGenerator:
    """Test the markdown generator."""

    def test_initialization(self):
        generator = MarkdownGenerator()
        assert generator.registry is not None
        assert generator.code_processor is not None
        assert generator.structured_processor is not None

    def test_generate_python_markdown(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("Hello, world!")\n')
            f.flush()

            try:
                generator = MarkdownGenerator()
                result = generator.generate_markdown(Path(f.name))

                assert '# ' in result  # Has title
                assert 'python' in result  # Has syntax highlighting
                assert 'Hello, world!' in result  # Has content
                assert '---' in result  # Has frontmatter

            finally:
                Path(f.name).unlink()

    def test_generate_json_markdown(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value", "number": 42}\n')
            f.flush()

            try:
                generator = MarkdownGenerator()
                result = generator.generate_markdown(Path(f.name))

                assert '# ' in result
                assert 'json' in result
                assert '"key"' in result
                assert '"value"' in result

            finally:
                Path(f.name).unlink()

    def test_format_override(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.slp', delete=False) as f:
            f.write('{"pipeline": "test"}\n')
            f.flush()

            try:
                generator = MarkdownGenerator()
                result = generator.generate_markdown(
                    Path(f.name),
                    format_override='json'
                )

                assert 'json' in result.lower()
                assert 'pipeline' in result

            finally:
                Path(f.name).unlink()

    def test_custom_title_and_description(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# Test script\nprint("test")\n')
            f.flush()

            try:
                generator = MarkdownGenerator()
                result = generator.generate_markdown(
                    Path(f.name),
                    title="Custom Title",
                    description="Custom description"
                )

                assert 'Custom Title' in result
                assert 'Custom description' in result

            finally:
                Path(f.name).unlink()

    def test_file_not_found(self):
        generator = MarkdownGenerator()

        with pytest.raises(FileNotFoundError):
            generator.generate_markdown(Path('/nonexistent/file.py'))


if __name__ == '__main__':
    pytest.main([__file__])