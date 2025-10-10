"""
Core markdown generation functionality.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template

from .registry import FileTypeRegistry
from .processors import CodeFileProcessor, StructuredFileProcessor


class MarkdownGenerator:
    """Main class for generating markdown from source files."""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the markdown generator.

        Args:
            template_dir: Directory containing Jinja2 templates (optional)
        """
        self.registry = FileTypeRegistry()
        self.code_processor = CodeFileProcessor()
        self.structured_processor = StructuredFileProcessor()

        # Set up template environment
        if template_dir and template_dir.exists():
            self.template_env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            # Use built-in templates
            template_path = Path(__file__).parent / "templates"
            self.template_env = Environment(loader=FileSystemLoader(str(template_path)))

        # Set up default template
        self.default_template_name = "default.md.j2"

    def generate_markdown(
        self,
        file_path: Path,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> str:
        """
        Generate markdown for a source file.

        Args:
            file_path: Path to the source file
            output_path: Optional output path for saving markdown
            **kwargs: Additional options including:
                - format_override: Force specific format (e.g., 'json' for .slp files)
                - template: Custom template name
                - title: Custom title override
                - description: Custom description
                - tags: List of tags
                - max_lines: Maximum lines to include
                - include_metadata: Include file metadata (default: True)
                - include_stats: Include code/structure statistics (default: True)

        Returns:
            Generated markdown content as string
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file type information
        format_override = kwargs.get('format_override')
        type_info = self.registry.get_type_info(file_path.suffix, format_override)

        # Select appropriate processor
        if type_info.processor_type == 'structured':
            processor = self.structured_processor
        else:
            processor = self.code_processor

        # Process the file
        processed_data = processor.process(file_path, **kwargs)

        # Prepare template context
        context = self._build_template_context(
            file_path, type_info, processed_data, **kwargs
        )

        # Load and render template
        template_name = kwargs.get('template', self.default_template_name)
        try:
            template = self.template_env.get_template(template_name)
        except Exception:
            # Fallback to default template
            template = self.template_env.get_template(self.default_template_name)

        markdown_content = template.render(context)

        # Save to file if output path specified
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown_content, encoding='utf-8')

        return markdown_content

    def _build_template_context(
        self,
        file_path: Path,
        type_info,
        processed_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Build context dictionary for template rendering."""

        # Base context
        context = {
            'file_path': file_path,
            'file_name': file_path.name,
            'type_info': type_info,
            'processed_data': processed_data,
            'generation_timestamp': self._get_timestamp(),
        }

        # Customizable fields
        context.update({
            'title': kwargs.get('title', self._generate_title(file_path, type_info)),
            'description': kwargs.get('description', self._generate_description(file_path, type_info)),
            'tags': kwargs.get('tags', self._generate_tags(file_path, type_info)),
            'include_metadata': kwargs.get('include_metadata', True),
            'include_stats': kwargs.get('include_stats', True),
            'include_toc': kwargs.get('include_toc', True),
            'linenums': kwargs.get('linenums', True),
            'custom_css_classes': kwargs.get('custom_css_classes', []),
        })

        # MkDocs-specific frontmatter
        context['frontmatter'] = self._build_frontmatter(context, **kwargs)

        return context

    def _build_frontmatter(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Build YAML frontmatter for MkDocs."""
        frontmatter = {
            'title': context['title'],
            'description': context['description'],
        }

        # Add tags if provided
        if context['tags']:
            frontmatter['tags'] = context['tags']

        # Add custom frontmatter fields
        custom_frontmatter = kwargs.get('frontmatter', {})
        frontmatter.update(custom_frontmatter)

        return frontmatter

    def _generate_title(self, file_path: Path, type_info) -> str:
        """Generate a default title for the file."""
        base_name = file_path.stem
        # Clean up common prefixes and make title-case
        clean_name = base_name.replace('_', ' ').replace('-', ' ')
        return f"{clean_name.title()} ({type_info.name})"

    def _generate_description(self, file_path: Path, type_info) -> str:
        """Generate a default description for the file."""
        return f"{type_info.description or type_info.name} - {file_path.name}"

    def _generate_tags(self, file_path: Path, type_info) -> list[str]:
        """Generate default tags for the file."""
        tags = [type_info.name.lower()]

        # Add extension-based tag
        if file_path.suffix:
            ext_tag = file_path.suffix[1:].lower()  # Remove dot
            if ext_tag not in tags:
                tags.append(ext_tag)

        # Add processor type tag
        if type_info.processor_type not in tags:
            tags.append(type_info.processor_type)

        return tags

    def _get_timestamp(self) -> str:
        """Get current timestamp for generation metadata."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_supported_formats(self) -> Dict[str, str]:
        """Get mapping of supported file extensions to format names."""
        return {
            ext: info.name
            for ext, info in self.registry._registry.items()
        }

    def register_custom_type(self, extension: str, type_info) -> None:
        """Register a custom file type."""
        self.registry.register_type(extension, type_info)