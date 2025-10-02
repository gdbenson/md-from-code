# md-from-code

Convert source code files to MkDocs-compatible markdown pages with syntax highlighting, metadata extraction, and flexible templating.

## Features

- **40+ Programming Languages** - Support for Python, Java, JavaScript, TypeScript, Go, Rust, C/C++, and many more
- **Structured Data Formats** - JSON, XML, YAML, TOML, INI with pretty-printing and validation
- **Format Override** - Handle non-standard extensions (e.g., `.slp` files as JSON)
- **Rich Metadata** - File statistics, code analysis, and structure information
- **Flexible Templates** - Jinja2-based templates with built-in options (default, minimal, detailed)
- **MkDocs Integration** - YAML frontmatter and MkDocs Material theme compatibility
- **Batch Processing** - Process multiple files with progress indicators
- **Content Safety** - File size limits, encoding detection, and content sanitization

## Installation

### Using UV (Recommended)

```bash
# Install from source
git clone <repository-url>
cd md-from-code
uv install .

# Install in development mode
uv install -e ".[dev]"
```

### Using pip

```bash
pip install md-from-code
```

## Quick Start

### Basic Usage

```bash
# Convert a Python file
md-from-code script.py -o script.md

# Convert with format override (for .slp files)
md-from-code pipeline.slp --format json -o pipeline.md

# Batch processing
md-from-code src/*.py --output-dir docs/code/

# Custom template and metadata
md-from-code app.js --template detailed --title "Main Application" --tags "javascript,frontend"
```

### Common Examples

```bash
# SnapLogic pipeline (.slp as JSON)
md-from-code pipeline.slp --format json --title "Data Pipeline" -o docs/pipeline.md

# Python package with statistics
md-from-code *.py --output-dir docs/api/ --template detailed

# Configuration files
md-from-code config.yaml settings.json --output-dir docs/config/

# Limit large files
md-from-code large_file.py --max-lines 500 -o docs/large_file.md
```

## CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `-o, --output` | Output file (single input) or directory | `-o output.md` |
| `--output-dir` | Output directory for all files | `--output-dir docs/` |
| `--format` | Override file format detection | `--format json` |
| `--template` | Custom template (default, minimal, detailed) | `--template detailed` |
| `--title` | Custom document title | `--title "My Script"` |
| `--description` | Custom description | `--description "Main app"` |
| `--tags` | Comma-separated tags | `--tags "python,api"` |
| `--max-lines` | Limit output lines | `--max-lines 1000` |
| `--max-file-size` | File size limit in bytes | `--max-file-size 5242880` |
| `--encoding` | Force file encoding | `--encoding utf-8` |
| `--no-metadata` | Exclude file metadata | `--no-metadata` |
| `--no-stats` | Exclude code statistics | `--no-stats` |
| `--line-numbers` | Include line numbers | `--line-numbers` |
| `--list-formats` | Show supported formats | `--list-formats` |
| `--validate-only` | Validate without output | `--validate-only` |
| `-v, --verbose` | Verbose output | `-v` |

## Supported File Types

### Programming Languages
- **Python** (`.py`) - Functions, classes, imports, docstrings
- **JavaScript/TypeScript** (`.js`, `.ts`, `.jsx`, `.tsx`) - ES6+, React components
- **Java** (`.java`) - Classes, methods, packages
- **C/C++** (`.c`, `.cpp`, `.h`, `.hpp`) - Functions, includes
- **Go** (`.go`) - Functions, structs, packages
- **Rust** (`.rs`) - Functions, structs, modules
- **Shell Scripts** (`.sh`, `.bash`, `.zsh`) - Functions, variables
- **SQL** (`.sql`) - Queries, functions, procedures
- **And many more...**

### Structured Data
- **JSON** (`.json`) - Pretty-printing, validation, structure analysis
- **XML** (`.xml`) - Pretty-printing, namespace extraction
- **YAML** (`.yaml`, `.yml`) - Multi-document support
- **TOML** (`.toml`) - Configuration files
- **INI/Config** (`.ini`, `.cfg`, `.conf`) - Section analysis

### Documentation
- **Markdown** (`.md`) - Preprocessed markdown
- **reStructuredText** (`.rst`) - Sphinx documentation
- **LaTeX** (`.tex`) - Mathematical documents

## Templates

### Built-in Templates

1. **default** - Balanced view with metadata and statistics
2. **minimal** - Just code with basic frontmatter
3. **detailed** - Comprehensive analysis and metadata

### Custom Templates

Create Jinja2 templates in a directory and use `--template-dir`:

```jinja2
---
title: {{ title }}
tags: {{ tags }}
---

# {{ title }}

{{ description }}

```{{ type_info.highlight_lang }}
{{ processed_data.content }}
```
```

Available template variables:
- `title`, `description`, `tags` - Document metadata
- `file_path`, `file_name` - File information
- `type_info` - File type information (name, icon, highlight_lang)
- `processed_data` - Processed content and statistics
- `frontmatter` - YAML frontmatter dictionary

## Integration Examples

### MkDocs Integration

Add to your `mkdocs.yml`:

```yaml
nav:
  - Code Documentation:
    - API: api/
    - Utilities: utils/

plugins:
  - search
  - tags

markdown_extensions:
  - pymdownx.highlight:
      linenums: true
  - pymdownx.superfences
  - attr_list
  - md_in_html
```

Generate documentation:

```bash
# Generate all Python files
md-from-code src/**/*.py --output-dir docs/api/ --line-numbers

# Generate config files
md-from-code config/*.yaml --output-dir docs/config/ --template detailed

# Build MkDocs site
mkdocs build
```

### GitHub Actions

```yaml
name: Generate Code Documentation

on: [push]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install md-from-code
        run: pip install md-from-code

      - name: Generate documentation
        run: |
          md-from-code src/**/*.py --output-dir docs/api/
          md-from-code config/*.json --format json --output-dir docs/config/

      - name: Build MkDocs
        run: |
          pip install mkdocs-material
          mkdocs build
```

## API Usage

```python
from pathlib import Path
from md_from_code import MarkdownGenerator

# Initialize generator
generator = MarkdownGenerator()

# Generate markdown for a file
markdown_content = generator.generate_markdown(
    Path("script.py"),
    title="My Script",
    tags=["python", "utility"],
    max_lines=500
)

# Save to file
output_path = Path("docs/script.md")
generator.generate_markdown(
    Path("script.py"),
    output_path=output_path,
    template="detailed"
)

# Custom format override
markdown_content = generator.generate_markdown(
    Path("pipeline.slp"),
    format_override="json",
    title="Data Pipeline"
)
```

## Configuration

Create a `.md-from-code.json` configuration file:

```json
{
  "default_template": "detailed",
  "max_file_size": 10485760,
  "include_metadata": true,
  "include_stats": true,
  "line_numbers": true,
  "custom_tags": {
    "*.py": ["python", "backend"],
    "*.js": ["javascript", "frontend"],
    "*.slp": ["snaplogic", "pipeline"]
  }
}
```

## Development

### Setup

```bash
git clone <repository-url>
cd md-from-code
uv install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=md_from_code

# Run specific test
pytest tests/test_basic.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Key Considerations

### Performance
- **File Size Limits** - Default 10MB limit, configurable
- **Memory Efficient** - Streaming for large files
- **Batch Processing** - Progress indicators for multiple files

### Security
- **Content Sanitization** - Safe markdown generation
- **Path Validation** - Secure file access
- **Encoding Detection** - Handles various text encodings

### Reliability
- **Error Handling** - Graceful handling of malformed files
- **Format Validation** - Structure validation for JSON/XML/YAML
- **Fallback Options** - Default processors for unknown types

### Extensibility
- **Custom Templates** - Jinja2-based template system
- **Plugin Architecture** - Easy to add new file type processors
- **Configuration** - Flexible options via CLI and config files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Run quality checks (`black`, `isort`, `mypy`, `flake8`)
5. Run tests (`pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [MkDocs](https://www.mkdocs.org/) - Documentation site generator
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) - Material theme for MkDocs
- [Pygments](https://pygments.org/) - Syntax highlighting library