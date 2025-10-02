"""
File type registry for mapping file extensions to processors and metadata.
"""

from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class FileTypeInfo:
    """Information about a file type including processor and display metadata."""
    name: str
    icon: str
    highlight_lang: str
    processor_type: str
    mime_type: Optional[str] = None
    description: Optional[str] = None


class FileTypeRegistry:
    """Registry for mapping file extensions to processing information."""

    def __init__(self):
        self._registry: Dict[str, FileTypeInfo] = {}
        self._initialize_default_types()

    def _initialize_default_types(self) -> None:
        """Initialize the registry with default file type mappings."""

        # Programming languages
        programming_languages = {
            ".py": FileTypeInfo("Python", "🐍", "python", "code", "text/x-python", "Python source code"),
            ".java": FileTypeInfo("Java", "☕", "java", "code", "text/x-java-source", "Java source code"),
            ".js": FileTypeInfo("JavaScript", "🟨", "javascript", "code", "text/javascript", "JavaScript source code"),
            ".ts": FileTypeInfo("TypeScript", "🔷", "typescript", "code", "text/typescript", "TypeScript source code"),
            ".jsx": FileTypeInfo("JSX", "⚛️", "jsx", "code", "text/jsx", "JSX React component"),
            ".tsx": FileTypeInfo("TSX", "⚛️", "tsx", "code", "text/tsx", "TSX React component"),
            ".c": FileTypeInfo("C", "🔧", "c", "code", "text/x-c", "C source code"),
            ".cpp": FileTypeInfo("C++", "🔧", "cpp", "code", "text/x-c++", "C++ source code"),
            ".cc": FileTypeInfo("C++", "🔧", "cpp", "code", "text/x-c++", "C++ source code"),
            ".cxx": FileTypeInfo("C++", "🔧", "cpp", "code", "text/x-c++", "C++ source code"),
            ".h": FileTypeInfo("C Header", "📋", "c", "code", "text/x-c", "C header file"),
            ".hpp": FileTypeInfo("C++ Header", "📋", "cpp", "code", "text/x-c++", "C++ header file"),
            ".cs": FileTypeInfo("C#", "💎", "csharp", "code", "text/x-csharp", "C# source code"),
            ".go": FileTypeInfo("Go", "🐹", "go", "code", "text/x-go", "Go source code"),
            ".rs": FileTypeInfo("Rust", "🦀", "rust", "code", "text/x-rust", "Rust source code"),
            ".php": FileTypeInfo("PHP", "🐘", "php", "code", "text/x-php", "PHP source code"),
            ".rb": FileTypeInfo("Ruby", "💎", "ruby", "code", "text/x-ruby", "Ruby source code"),
            ".swift": FileTypeInfo("Swift", "🦉", "swift", "code", "text/x-swift", "Swift source code"),
            ".kt": FileTypeInfo("Kotlin", "🎯", "kotlin", "code", "text/x-kotlin", "Kotlin source code"),
            ".scala": FileTypeInfo("Scala", "🎼", "scala", "code", "text/x-scala", "Scala source code"),
            ".r": FileTypeInfo("R", "📊", "r", "code", "text/x-r", "R source code"),
            ".m": FileTypeInfo("MATLAB", "🧮", "matlab", "code", "text/x-matlab", "MATLAB source code"),
            ".pl": FileTypeInfo("Perl", "🐪", "perl", "code", "text/x-perl", "Perl source code"),
            ".lua": FileTypeInfo("Lua", "🌙", "lua", "code", "text/x-lua", "Lua source code"),
            ".sh": FileTypeInfo("Shell", "🐚", "bash", "code", "text/x-shellscript", "Shell script"),
            ".bash": FileTypeInfo("Bash", "🐚", "bash", "code", "text/x-shellscript", "Bash script"),
            ".zsh": FileTypeInfo("Zsh", "🐚", "zsh", "code", "text/x-shellscript", "Zsh script"),
            ".fish": FileTypeInfo("Fish", "🐠", "fish", "code", "text/x-shellscript", "Fish shell script"),
            ".ps1": FileTypeInfo("PowerShell", "🔵", "powershell", "code", "text/x-powershell", "PowerShell script"),
            ".sql": FileTypeInfo("SQL", "🗃️", "sql", "code", "text/x-sql", "SQL script"),
            ".vim": FileTypeInfo("Vim Script", "📝", "vim", "code", "text/x-vim", "Vim script"),
            ".el": FileTypeInfo("Emacs Lisp", "📝", "elisp", "code", "text/x-elisp", "Emacs Lisp"),
        }

        # Web technologies
        web_technologies = {
            ".html": FileTypeInfo("HTML", "🌐", "html", "code", "text/html", "HTML document"),
            ".htm": FileTypeInfo("HTML", "🌐", "html", "code", "text/html", "HTML document"),
            ".css": FileTypeInfo("CSS", "🎨", "css", "code", "text/css", "CSS stylesheet"),
            ".scss": FileTypeInfo("SCSS", "🎨", "scss", "code", "text/x-scss", "SCSS stylesheet"),
            ".sass": FileTypeInfo("Sass", "🎨", "sass", "code", "text/x-sass", "Sass stylesheet"),
            ".less": FileTypeInfo("Less", "🎨", "less", "code", "text/x-less", "Less stylesheet"),
            ".vue": FileTypeInfo("Vue", "💚", "vue", "code", "text/x-vue", "Vue component"),
            ".svelte": FileTypeInfo("Svelte", "🧡", "svelte", "code", "text/x-svelte", "Svelte component"),
        }

        # Structured data formats
        structured_formats = {
            ".json": FileTypeInfo("JSON", "📄", "json", "structured", "application/json", "JSON data"),
            ".xml": FileTypeInfo("XML", "📜", "xml", "structured", "application/xml", "XML document"),
            ".yaml": FileTypeInfo("YAML", "📋", "yaml", "structured", "text/yaml", "YAML configuration"),
            ".yml": FileTypeInfo("YAML", "📋", "yaml", "structured", "text/yaml", "YAML configuration"),
            ".toml": FileTypeInfo("TOML", "📋", "toml", "structured", "text/x-toml", "TOML configuration"),
            ".ini": FileTypeInfo("INI", "⚙️", "ini", "structured", "text/plain", "INI configuration"),
            ".cfg": FileTypeInfo("Config", "⚙️", "ini", "structured", "text/plain", "Configuration file"),
            ".conf": FileTypeInfo("Config", "⚙️", "apache", "structured", "text/plain", "Configuration file"),
            ".properties": FileTypeInfo("Properties", "⚙️", "properties", "structured", "text/plain", "Properties file"),
        }

        # Documentation and markup
        documentation = {
            ".md": FileTypeInfo("Markdown", "📝", "markdown", "code", "text/markdown", "Markdown document"),
            ".rst": FileTypeInfo("reStructuredText", "📝", "rst", "code", "text/x-rst", "reStructuredText document"),
            ".tex": FileTypeInfo("LaTeX", "📄", "latex", "code", "text/x-latex", "LaTeX document"),
            ".adoc": FileTypeInfo("AsciiDoc", "📝", "asciidoc", "code", "text/x-asciidoc", "AsciiDoc document"),
            ".org": FileTypeInfo("Org Mode", "📝", "org", "code", "text/x-org", "Org mode document"),
        }

        # Expression and template languages
        expressions = {
            ".expr": FileTypeInfo("Expression", "📝", "python", "code", "text/plain", "Expression library"),
            ".j2": FileTypeInfo("Jinja2", "🏷️", "jinja2", "code", "text/x-jinja2", "Jinja2 template"),
            ".jinja": FileTypeInfo("Jinja2", "🏷️", "jinja2", "code", "text/x-jinja2", "Jinja2 template"),
            ".hbs": FileTypeInfo("Handlebars", "🏷️", "handlebars", "code", "text/x-handlebars", "Handlebars template"),
            ".mustache": FileTypeInfo("Mustache", "🏷️", "mustache", "code", "text/x-mustache", "Mustache template"),
        }

        # Build and configuration files
        build_files = {
            ".dockerfile": FileTypeInfo("Dockerfile", "🐳", "dockerfile", "code", "text/x-dockerfile", "Docker configuration"),
            ".makefile": FileTypeInfo("Makefile", "🔨", "makefile", "code", "text/x-makefile", "Make configuration"),
            ".cmake": FileTypeInfo("CMake", "🔨", "cmake", "code", "text/x-cmake", "CMake configuration"),
            ".gradle": FileTypeInfo("Gradle", "🐘", "gradle", "code", "text/x-gradle", "Gradle build script"),
            ".pom": FileTypeInfo("Maven POM", "📦", "xml", "structured", "application/xml", "Maven POM file"),
        }

        # Combine all mappings
        all_types = {
            **programming_languages,
            **web_technologies,
            **structured_formats,
            **documentation,
            **expressions,
            **build_files
        }

        self._registry.update(all_types)

    def register_type(self, extension: str, type_info: FileTypeInfo) -> None:
        """Register a new file type or override an existing one."""
        if not extension.startswith('.'):
            extension = '.' + extension
        self._registry[extension.lower()] = type_info

    def get_type_info(self, extension: str, format_override: Optional[str] = None) -> FileTypeInfo:
        """
        Get file type information for an extension.

        Args:
            extension: File extension (with or without leading dot)
            format_override: Optional format override (e.g., 'json' for .slp files)

        Returns:
            FileTypeInfo object with processing metadata
        """
        if not extension.startswith('.'):
            extension = '.' + extension

        # Handle format override
        if format_override:
            override_ext = f".{format_override}" if not format_override.startswith('.') else format_override
            if override_ext in self._registry:
                base_info = self._registry[override_ext]
                # Create a copy with the original extension noted
                return FileTypeInfo(
                    name=f"{base_info.name} ({extension})",
                    icon=base_info.icon,
                    highlight_lang=base_info.highlight_lang,
                    processor_type=base_info.processor_type,
                    mime_type=base_info.mime_type,
                    description=f"{base_info.description} (format override)"
                )

        # Return registered type or default
        return self._registry.get(
            extension.lower(),
            FileTypeInfo(
                name="Text File",
                icon="📄",
                highlight_lang="text",
                processor_type="code",
                mime_type="text/plain",
                description=f"Plain text file ({extension})"
            )
        )

    def get_supported_extensions(self) -> list[str]:
        """Get list of all supported file extensions."""
        return sorted(self._registry.keys())

    def get_processor_types(self) -> list[str]:
        """Get list of available processor types."""
        return list(set(info.processor_type for info in self._registry.values()))

    def search_by_name(self, name: str) -> list[Tuple[str, FileTypeInfo]]:
        """Search for file types by name (case-insensitive)."""
        name_lower = name.lower()
        return [
            (ext, info) for ext, info in self._registry.items()
            if name_lower in info.name.lower()
        ]