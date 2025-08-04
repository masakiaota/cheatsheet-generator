"""Command line interface for cheat sheet generator."""

import sys
from pathlib import Path

import click

from cheatsheet_generator.generator import PDFGenerator
from cheatsheet_generator.parser import YAMLParser


@click.command()
@click.argument("yaml_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output PDF file path (default: same name as input with .pdf extension)",
)
@click.option(
    "--validate",
    "-v",
    is_flag=True,
    help="Only validate the YAML file without generating PDF",
)
@click.option(
    "--estimate-pages", "-e", is_flag=True, help="Estimate number of pages and exit"
)
def main(yaml_file: Path, output: Path, validate: bool, estimate_pages: bool):
    """Generate a cheat sheet PDF from a YAML hotkey definition file.

    YAML_FILE: Path to the YAML file containing hotkey definitions.
    """
    try:
        errors = YAMLParser.validate_yaml(yaml_file)
        if errors:
            click.echo("YAML validation errors:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)

        if validate:
            click.echo("✓ YAML file is valid")
            return

        cheat_sheet = YAMLParser.parse_file(yaml_file)
        click.echo(f"Parsed {len(cheat_sheet.hotkeys)} hotkeys from {yaml_file}")

        if estimate_pages:
            generator = PDFGenerator(cheat_sheet)
            pages = generator.estimate_pages()
            click.echo(f"Estimated pages: {pages}")
            return

        if output is None:
            output = yaml_file.with_suffix(".pdf")

        generator = PDFGenerator(cheat_sheet)
        generator.generate(output)

        pages = generator.estimate_pages()
        click.echo(f"✓ Generated cheat sheet: {output}")
        click.echo(f"  - Title: {cheat_sheet.title}")
        click.echo(f"  - Hotkeys: {len(cheat_sheet.hotkeys)}")
        click.echo(f"  - Estimated pages: {pages}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
