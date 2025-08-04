"""Tests for data models."""

import pytest

from cheatsheet_generator.models import CheatSheet, CheatSheetConfig, Hotkey


class TestHotkey:
    """Test Hotkey model."""

    def test_valid_hotkey(self):
        """Test creating a valid hotkey."""
        hotkey = Hotkey(
            key="Ctrl+C", description="Copy", section="Edit", subsection="Clipboard"
        )
        assert hotkey.key == "Ctrl+C"
        assert hotkey.description == "Copy"
        assert hotkey.section == "Edit"
        assert hotkey.subsection == "Clipboard"

    def test_hotkey_without_subsection(self):
        """Test creating hotkey without subsection."""
        hotkey = Hotkey(key="Ctrl+C", description="Copy", section="Edit")
        assert hotkey.subsection == ""

    def test_invalid_hotkey(self):
        """Test validation of required fields."""
        with pytest.raises(
            ValueError, match="Key, description, and section are required"
        ):
            Hotkey(key="", description="Copy", section="Edit")

        with pytest.raises(
            ValueError, match="Key, description, and section are required"
        ):
            Hotkey(key="Ctrl+C", description="", section="Edit")

        with pytest.raises(
            ValueError, match="Key, description, and section are required"
        ):
            Hotkey(key="Ctrl+C", description="Copy", section="")


class TestCheatSheetConfig:
    """Test CheatSheetConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = CheatSheetConfig()
        assert config.title == "Hotkey Cheat Sheet"
        assert config.font_size == 7
        assert config.columns == 5

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "title": "Custom Title",
            "font_size": 12,
            "columns": 2,
            "unknown_field": "ignored",
        }
        config = CheatSheetConfig.from_dict(data)
        assert config.title == "Custom Title"
        assert config.font_size == 12
        assert config.columns == 2
        # Unknown fields should be ignored
        assert not hasattr(config, "unknown_field")


class TestCheatSheet:
    """Test CheatSheet model."""

    def test_cheat_sheet_creation(self):
        """Test creating a cheat sheet."""
        hotkeys = [Hotkey("Ctrl+C", "Copy", "Edit"), Hotkey("Ctrl+V", "Paste", "Edit")]
        sheet = CheatSheet("Test Sheet", hotkeys)
        assert sheet.title == "Test Sheet"
        assert len(sheet.hotkeys) == 2
        assert sheet.config.title == "Test Sheet"

    def test_get_sections(self):
        """Test grouping hotkeys by section and subsection."""
        hotkeys = [
            Hotkey("Ctrl+C", "Copy", "Edit", "Clipboard"),
            Hotkey("Ctrl+V", "Paste", "Edit", "Clipboard"),
            Hotkey("Ctrl+Z", "Undo", "Edit"),
            Hotkey("Ctrl+S", "Save", "File"),
        ]
        sheet = CheatSheet("Test", hotkeys)
        sections = sheet.get_sections()

        assert "Edit" in sections
        assert "File" in sections
        assert "Clipboard" in sections["Edit"]
        assert "General" in sections["Edit"]
        assert len(sections["Edit"]["Clipboard"]) == 2
        assert len(sections["Edit"]["General"]) == 1
        assert len(sections["File"]["General"]) == 1
