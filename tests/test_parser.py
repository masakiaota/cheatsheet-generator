"""Tests for YAML parser."""

import tempfile
from pathlib import Path

import pytest

from cheatsheet_generator.parser import YAMLParser


class TestYAMLParser:
    """Test YAML parser functionality."""

    def create_temp_yaml(self, content: str) -> Path:
        """Create a temporary YAML file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    def test_parse_simple_yaml(self):
        """Test parsing a simple YAML file."""
        yaml_content = """
title: "Test Cheat Sheet"
sections:
  Edit:
    "Ctrl+C": "Copy"
    "Ctrl+V": "Paste"
  File:
    "Ctrl+S": "Save"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            sheet = YAMLParser.parse_file(yaml_file)
            assert sheet.title == "Test Cheat Sheet"
            assert len(sheet.hotkeys) == 3

            # Check specific hotkeys
            hotkeys_dict = {h.key: h for h in sheet.hotkeys}
            assert "Ctrl+C" in hotkeys_dict
            assert hotkeys_dict["Ctrl+C"].description == "Copy"
            assert hotkeys_dict["Ctrl+C"].section == "Edit"
        finally:
            yaml_file.unlink()

    def test_parse_yaml_with_subsections(self):
        """Test parsing YAML with subsections."""
        yaml_content = """
title: "Test Cheat Sheet"
sections:
  Edit:
    Clipboard:
      "Ctrl+C": "Copy"
      "Ctrl+V": "Paste"
    "Ctrl+Z": "Undo"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            sheet = YAMLParser.parse_file(yaml_file)
            assert len(sheet.hotkeys) == 3

            # Find clipboard hotkeys
            clipboard_hotkeys = [
                h for h in sheet.hotkeys if h.subsection == "Clipboard"
            ]
            assert len(clipboard_hotkeys) == 2

            # Find general hotkeys
            general_hotkeys = [h for h in sheet.hotkeys if h.subsection == ""]
            assert len(general_hotkeys) == 1
            assert general_hotkeys[0].key == "Ctrl+Z"
        finally:
            yaml_file.unlink()

    def test_parse_yaml_with_config(self):
        """Test parsing YAML with configuration."""
        yaml_content = """
title: "Custom Sheet"
config:
  font_size: 12
  columns: 2
sections:
  Test:
    "key": "description"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            sheet = YAMLParser.parse_file(yaml_file)
            assert sheet.config.font_size == 12
            assert sheet.config.columns == 2
            assert sheet.config.title == "Custom Sheet"
        finally:
            yaml_file.unlink()

    def test_validate_yaml_valid(self):
        """Test validation of valid YAML."""
        yaml_content = """
title: "Test"
sections:
  Test:
    "key": "description"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            errors = YAMLParser.validate_yaml(yaml_file)
            assert len(errors) == 0
        finally:
            yaml_file.unlink()

    def test_validate_yaml_missing_sections(self):
        """Test validation with missing sections."""
        yaml_content = """
title: "Test"
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            errors = YAMLParser.validate_yaml(yaml_file)
            assert len(errors) == 1
            assert "Missing 'sections' key" in errors[0]
        finally:
            yaml_file.unlink()

    def test_validate_yaml_invalid_syntax(self):
        """Test validation with invalid YAML syntax."""
        yaml_content = """
title: "Test"
sections:
  Test:
    key: value
      invalid: indentation
"""
        yaml_file = self.create_temp_yaml(yaml_content)

        try:
            errors = YAMLParser.validate_yaml(yaml_file)
            assert len(errors) == 1
            assert "Invalid YAML syntax" in errors[0]
        finally:
            yaml_file.unlink()

    def test_validate_yaml_file_not_found(self):
        """Test validation with non-existent file."""
        non_existent = Path("/non/existent/file.yaml")
        errors = YAMLParser.validate_yaml(non_existent)
        assert len(errors) == 1
        assert "File not found" in errors[0]

    def test_parse_dict_invalid_format(self):
        """Test parsing invalid dictionary format."""
        with pytest.raises(ValueError, match="YAML data must be a dictionary"):
            YAMLParser.parse_dict("invalid")
