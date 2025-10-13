"""
Command-line interface for md-from-code.
"""

import sys
from pathlib import Path
from typing import List, Optional
from fnmatch import fnmatch
import click
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table

from .core import MarkdownGenerator
from .registry import FileTypeInfo


console = Console()


@click.command()
@click.argument('input_files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('-o', '--output', help='Output file (for single input) or directory (for multiple inputs)')
@click.option('--output-dir', help='Output directory for all files')
@click.option('-r', '--recursive', is_flag=True, help='Recursively discover files in directories')
@click.option('--exclude', default='*.md', help='Comma-separated patterns to exclude (default: *.md when using --recursive)')
@click.option('--format', 'format_override', help='Override file format detection (e.g., json, xml, yaml)')
@click.option('--template', help='Custom Jinja2 template file')
@click.option('--template-dir', help='Directory containing custom templates')
@click.option('--title', help='Custom title for the document')
@click.option('--description', help='Custom description for the document')
@click.option('--tags', help='Comma-separated list of tags')
@click.option('--max-lines', type=int, help='Maximum number of lines to include in output')
@click.option('--max-file-size', type=int, default=10*1024*1024, help='Maximum file size in bytes (default: 10MB)')
@click.option('--encoding', help='Force specific file encoding')
@click.option('--indent', type=int, default=2, help='Indentation for structured data pretty-printing')
@click.option('--no-metadata', is_flag=True, help='Exclude file metadata from output')
@click.option('--no-stats', is_flag=True, help='Exclude code/structure statistics from output')
@click.option('--no-toc', is_flag=True, help='Exclude table of contents from output')
@click.option('--no-line-numbers', is_flag=True, help='Exclude line numbers from code blocks')
@click.option('--frontmatter', help='Additional YAML frontmatter as JSON string')
@click.option('--list-formats', is_flag=True, help='List all supported file formats and exit')
@click.option('--validate-only', is_flag=True, help='Only validate files without generating output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-error output')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(
    input_files: tuple[str, ...],
    output: Optional[str],
    output_dir: Optional[str],
    recursive: bool,
    exclude: str,
    format_override: Optional[str],
    template: Optional[str],
    template_dir: Optional[str],
    title: Optional[str],
    description: Optional[str],
    tags: Optional[str],
    max_lines: Optional[int],
    max_file_size: int,
    encoding: Optional[str],
    indent: int,
    no_metadata: bool,
    no_stats: bool,
    no_toc: bool,
    no_line_numbers: bool,
    frontmatter: Optional[str],
    list_formats: bool,
    validate_only: bool,
    quiet: bool,
    verbose: bool,
) -> None:
    """
    Convert source code files to MkDocs-compatible markdown pages.

    INPUT_FILES can be one or more file paths, glob patterns, or directories.
    Use --recursive to process all files in directories recursively.
    """
    try:
        # Handle special commands first
        if list_formats:
            _list_supported_formats()
            return

        # Initialize generator
        template_path = Path(template_dir) if template_dir else None
        generator = MarkdownGenerator(template_path)

        # Set processor options
        generator.code_processor.max_file_size = max_file_size
        generator.structured_processor.max_file_size = max_file_size

        # Process files
        input_paths = [Path(f) for f in input_files]
        _process_files(
            generator, input_paths, output, output_dir, recursive, exclude,
            format_override, template, title, description, tags, max_lines,
            encoding, indent, no_metadata, no_stats, no_toc, no_line_numbers,
            frontmatter, validate_only, quiet, verbose
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


def _discover_files(
    input_paths: List[Path],
    recursive: bool,
    exclude_patterns: List[str],
    verbose: bool = False
) -> List[Path]:
    """
    Discover files from input paths, applying recursive search and exclusions.

    Args:
        input_paths: List of file or directory paths
        recursive: Whether to recursively search directories
        exclude_patterns: List of patterns to exclude (e.g., ['*.md', '*.pyc'])
        verbose: Enable verbose output

    Returns:
        List of discovered file paths
    """
    discovered_files = []

    for input_path in input_paths:
        if input_path.is_file():
            # Single file - check if it matches exclusion patterns
            if not _should_exclude(input_path, exclude_patterns):
                discovered_files.append(input_path)
            elif verbose:
                console.print(f"[yellow]Excluded:[/yellow] {input_path}")

        elif input_path.is_dir():
            if recursive:
                # Recursively walk directory
                for file_path in input_path.rglob('*'):
                    if file_path.is_file() and not _should_exclude(file_path, exclude_patterns):
                        discovered_files.append(file_path)
                    elif verbose and file_path.is_file():
                        console.print(f"[yellow]Excluded:[/yellow] {file_path}")
            else:
                # Only process files directly in the directory
                for file_path in input_path.iterdir():
                    if file_path.is_file() and not _should_exclude(file_path, exclude_patterns):
                        discovered_files.append(file_path)
                    elif verbose and file_path.is_file():
                        console.print(f"[yellow]Excluded:[/yellow] {file_path}")

    return discovered_files


def _should_exclude(file_path: Path, exclude_patterns: List[str]) -> bool:
    """
    Check if a file should be excluded based on patterns.

    Args:
        file_path: Path to check
        exclude_patterns: List of patterns to match against

    Returns:
        True if file should be excluded, False otherwise
    """
    file_name = file_path.name
    file_relative = str(file_path)

    for pattern in exclude_patterns:
        # Match against filename and full path
        if fnmatch(file_name, pattern) or fnmatch(file_relative, pattern):
            return True

    return False


def _list_supported_formats() -> None:
    """List all supported file formats."""
    generator = MarkdownGenerator()
    formats = generator.get_supported_formats()

    table = Table(title="Supported File Formats")
    table.add_column("Extension", style="cyan")
    table.add_column("Format Name", style="green")
    table.add_column("Processor", style="yellow")

    # Group by processor type
    grouped_formats = {}
    for ext, name in formats.items():
        type_info = generator.registry.get_type_info(ext)
        processor_type = type_info.processor_type
        if processor_type not in grouped_formats:
            grouped_formats[processor_type] = []
        grouped_formats[processor_type].append((ext, name, type_info.icon))

    # Add rows grouped by processor type
    for processor_type in sorted(grouped_formats.keys()):
        table.add_section()
        for ext, name, icon in sorted(grouped_formats[processor_type]):
            table.add_row(ext, f"{icon} {name}", processor_type.title())

    console.print(table)
    console.print(f"\n[green]Total: {len(formats)} supported formats[/green]")
    console.print("\n[yellow]Note:[/yellow] Use --format to override detection for non-standard extensions")
    console.print("[yellow]Example:[/yellow] md-from-code pipeline.slp --format json")


def _process_files(
    generator: MarkdownGenerator,
    input_paths: List[Path],
    output: Optional[str],
    output_dir: Optional[str],
    recursive: bool,
    exclude: str,
    format_override: Optional[str],
    template: Optional[str],
    title: Optional[str],
    description: Optional[str],
    tags: Optional[str],
    max_lines: Optional[int],
    encoding: Optional[str],
    indent: int,
    no_metadata: bool,
    no_stats: bool,
    no_toc: bool,
    no_line_numbers: bool,
    frontmatter: Optional[str],
    validate_only: bool,
    quiet: bool,
    verbose: bool,
) -> None:
    """Process input files and generate markdown."""

    # Parse exclude patterns
    exclude_patterns = [p.strip() for p in exclude.split(',') if p.strip()] if exclude else []

    # Discover files if recursive mode is enabled or if we have directories
    has_directories = any(p.is_dir() for p in input_paths)
    if recursive or has_directories:
        if not quiet and verbose:
            console.print(f"[cyan]Discovering files (recursive={recursive})...[/cyan]")
        input_paths = _discover_files(input_paths, recursive, exclude_patterns, verbose)
        if not quiet:
            console.print(f"[cyan]Found {len(input_paths)} file(s) to process[/cyan]")

    # If no files found, exit early
    if not input_paths:
        if not quiet:
            console.print("[yellow]No files found to process[/yellow]")
        return

    # Parse additional options
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else None
    frontmatter_dict = {}
    if frontmatter:
        import json
        try:
            frontmatter_dict = json.loads(frontmatter)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid frontmatter JSON: {e}")

    # Build kwargs for processing
    kwargs = {
        'format_override': format_override,
        'template': template,
        'title': title,
        'description': description,
        'tags': tag_list,
        'max_lines': max_lines,
        'encoding': encoding,
        'indent': indent,
        'include_metadata': not no_metadata,
        'include_stats': not no_stats,
        'include_toc': not no_toc,
        'linenums': not no_line_numbers,
        'frontmatter': frontmatter_dict,
    }

    # Determine output strategy
    single_file = len(input_paths) == 1 and output and not output_dir
    use_output_dir = output_dir or (len(input_paths) > 1 and output)

    if use_output_dir:
        output_path = Path(output_dir or output)
        output_path.mkdir(parents=True, exist_ok=True)
    elif single_file:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = None

    # Process files
    success_count = 0
    error_count = 0

    with Progress(console=console, disable=quiet) as progress:
        task = progress.add_task("Processing files...", total=len(input_paths))

        for input_path in input_paths:
            try:
                if not quiet:
                    progress.console.print(f"Processing: {input_path}")

                # Determine output file path
                if single_file:
                    output_file = output_path
                elif use_output_dir:
                    output_file = output_path / f"{input_path.name}.md"
                else:
                    output_file = input_path.parent / f"{input_path.name}.md"

                # Generate markdown
                if validate_only:
                    # Just validate without generating output
                    generator.generate_markdown(input_path, **kwargs)
                    if verbose:
                        console.print(f"[green]✓[/green] Valid: {input_path}")
                else:
                    markdown_content = generator.generate_markdown(
                        input_path, output_file, **kwargs
                    )

                    if not quiet:
                        if output_file:
                            console.print(f"[green]→[/green] Generated: {output_file}")
                        else:
                            console.print(f"[green]✓[/green] Processed: {input_path}")

                success_count += 1

            except Exception as e:
                error_count += 1
                console.print(f"[red]✗[/red] Error processing {input_path}: {str(e)}")
                if verbose:
                    console.print_exception()

            progress.advance(task)

    # Summary
    if not quiet:
        if validate_only:
            console.print(f"\n[green]Validation complete:[/green] {success_count} valid, {error_count} errors")
        else:
            console.print(f"\n[green]Processing complete:[/green] {success_count} generated, {error_count} errors")

    if error_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()