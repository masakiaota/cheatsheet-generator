"""Tests for command line interface."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from cheatsheet_generator.cli import main


class TestCLI:
    """Test command line interface."""

    def create_temp_yaml(self, content: str) -> Path:
        """Create a temporary YAML file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Generate a cheat sheet PDF" in result.output
        assert "--output" in result.output
        assert "--validate" in result.output

    def test_cli_validate_valid_file(self):
        """Test validation of valid YAML file."""
        yaml_content = """
title: "Test Sheet"
sections:
  Test:
    "key": "description"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(yaml_file), "--validate"])

            assert result.exit_code == 0
            assert "✓ YAML file is valid" in result.output
        finally:
            yaml_file.unlink()

    def test_cli_validate_invalid_file(self):
        """Test validation of invalid YAML file."""
        yaml_content = """
title: "Test Sheet"
# Missing sections
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(yaml_file), "--validate"])

            assert result.exit_code == 1
            assert "YAML validation errors:" in result.output
        finally:
            yaml_file.unlink()

    def test_cli_estimate_pages(self):
        """Test page estimation."""
        yaml_content = """
title: "Test Sheet"
sections:
  Test:
    "key1": "description1"
    "key2": "description2"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(yaml_file), "--estimate-pages"])

            assert result.exit_code == 0
            assert "Estimated pages:" in result.output
        finally:
            yaml_file.unlink()

    def test_cli_generate_pdf_default_output(self):
        """Test PDF generation with default output path."""
        yaml_content = """
title: "Test Sheet"
sections:
  Test:
    "key": "description"
"""
        yaml_file = self.create_temp_yaml(yaml_content)
        expected_pdf = yaml_file.with_suffix(".pdf")

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(yaml_file)])

            assert result.exit_code == 0
            assert "✓ Generated cheat sheet:" in result.output
            assert str(expected_pdf) in result.output
            assert "Title: Test Sheet" in result.output
            assert "Hotkeys: 1" in result.output

            # Check that PDF file was created
            assert expected_pdf.exists()

        finally:
            yaml_file.unlink()
            if expected_pdf.exists():
                expected_pdf.unlink()

    def test_cli_generate_pdf_custom_output(self):
        """Test PDF generation with custom output path."""
        yaml_content = """
title: "Test Sheet"
sections:
  Test:
    "key": "description"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            custom_output = Path(temp_pdf.name)

        try:
            runner = CliRunner()
            result = runner.invoke(
                main, [str(yaml_file), "--output", str(custom_output)]
            )

            assert result.exit_code == 0
            assert str(custom_output) in result.output
            assert custom_output.exists()

        finally:
            yaml_file.unlink()
            if custom_output.exists():
                custom_output.unlink()

    def test_cli_nonexistent_file(self):
        """Test CLI with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["/nonexistent/file.yaml"])

        assert result.exit_code == 2

    def test_cli_parse_error(self):
        """Test CLI with file that causes parsing error."""
        yaml_content = """
invalid: yaml: structure
sections: not_a_dict
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            runner = CliRunner()
            result = runner.invoke(main, [str(yaml_file)])

            assert result.exit_code == 1
            assert "YAML validation errors:" in result.output
        finally:
            yaml_file.unlink()
