"""Tests for PDF generator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from cheatsheet_generator.generator import PDFGenerator
from cheatsheet_generator.models import CheatSheet, CheatSheetConfig, Hotkey


class TestPDFGenerator:
    """Test PDF generator functionality."""

    def create_sample_cheat_sheet(self) -> CheatSheet:
        """Create a sample cheat sheet for testing."""
        hotkeys = [
            Hotkey("Ctrl+C", "Copy text", "Edit", "Clipboard"),
            Hotkey("Ctrl+V", "Paste text", "Edit", "Clipboard"),
            Hotkey("Ctrl+Z", "Undo action", "Edit"),
            Hotkey("Ctrl+S", "Save file", "File"),
            Hotkey("Ctrl+O", "Open file", "File"),
        ]
        config = CheatSheetConfig(title="Test Cheat Sheet", font_size=9, columns=2)
        return CheatSheet("Test Cheat Sheet", hotkeys, config)

    def test_pdf_generator_initialization(self):
        """Test PDF generator initialization."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        assert generator.cheat_sheet == sheet
        assert generator.config == sheet.config
        assert "title" in generator.styles
        assert "section_header" in generator.styles
        assert "hotkey" in generator.styles

    def test_calculate_layout(self):
        """Test layout calculation."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        column_width, usable_height = generator._calculate_layout()

        assert column_width > 0
        assert usable_height > 0
        assert isinstance(column_width, float)
        assert isinstance(usable_height, float)

    def test_create_hotkey_table(self):
        """Test hotkey table creation."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        clipboard_hotkeys = [h for h in sheet.hotkeys if h.subsection == "Clipboard"]
        table = generator._create_hotkey_table(clipboard_hotkeys)

        assert table is not None
        assert len(table._argW) == 2

    def test_create_hotkey_table_empty(self):
        """Test hotkey table creation with empty list."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        table = generator._create_hotkey_table([])
        assert table is None

    def test_build_content(self):
        """Test content building."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        content = generator._build_content()

        assert len(content) > 1
        assert hasattr(content[0], "text")

    def test_estimate_pages(self):
        """Test page estimation."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        pages = generator.estimate_pages()

        assert pages >= 1
        assert isinstance(pages, int)

    def test_estimate_pages_many_hotkeys(self):
        """Test page estimation with many hotkeys."""

        hotkeys = []
        for i in range(100):
            hotkeys.append(
                Hotkey(
                    f"Key{i}",
                    f"Description {i}",
                    f"Section{i // 10}",
                    f"Subsection{i % 3}",
                )
            )

        config = CheatSheetConfig(font_size=6, columns=2, row_height=8)
        sheet = CheatSheet("Large Sheet", hotkeys, config)
        generator = PDFGenerator(sheet)

        pages = generator.estimate_pages()

        assert pages >= 1

    @patch("cheatsheet_generator.generator.BaseDocTemplate")
    def test_generate_pdf(self, mock_doc_class):
        """Test PDF generation."""

        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc

        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        output_path = Path("/tmp/test.pdf")
        generator.generate(output_path)

        mock_doc_class.assert_called_once()
        mock_doc.addPageTemplates.assert_called_once()
        mock_doc.build.assert_called_once()

        build_args = mock_doc.build.call_args[0]
        content = build_args[0]
        assert len(content) > 0

    def test_styles_creation(self):
        """Test that all required styles are created."""
        sheet = self.create_sample_cheat_sheet()
        generator = PDFGenerator(sheet)

        required_styles = ["title", "section_header", "subsection_header", "hotkey"]
        for style_name in required_styles:
            assert style_name in generator.styles
            style = generator.styles[style_name]
            assert hasattr(style, "fontSize")
            assert hasattr(style, "textColor")

    def test_font_size_configuration(self):
        """Test that font sizes are applied from configuration."""
        config = CheatSheetConfig(font_size=12, header_font_size=16)
        hotkeys = [Hotkey("Test", "Test", "Test")]
        sheet = CheatSheet("Test", hotkeys, config)
        generator = PDFGenerator(sheet)

        assert generator.styles["hotkey"].fontSize == 12
        assert generator.styles["section_header"].fontSize == 17
        assert generator.styles["title"].fontSize == 19
