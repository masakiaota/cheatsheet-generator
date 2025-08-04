"""PDF generator for cheat sheets."""

import math
from pathlib import Path
from typing import List, Tuple

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.doctemplate import BaseDocTemplate

from cheatsheet_generator.models import CheatSheet, Hotkey


class PDFGenerator:
    """Generates PDF cheat sheets from CheatSheet objects."""

    def __init__(self, cheat_sheet: CheatSheet):
        """Initialize the PDF generator."""
        self.cheat_sheet = cheat_sheet
        self.config = cheat_sheet.config
        self.styles = self._create_styles()

    def _create_styles(self) -> dict:
        """Create paragraph styles for the PDF."""
        styles = getSampleStyleSheet()

        custom_styles = {
            "title": ParagraphStyle(
                "title",
                parent=styles["Heading1"],
                fontSize=self.config.header_font_size + 3,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=15,
                fontName="Helvetica-Bold",
            ),
            "section_header": ParagraphStyle(
                "section_header",
                parent=styles["Heading2"],
                fontSize=self.config.header_font_size + 1,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=4,
                spaceBefore=8,
                leftIndent=0,
                rightIndent=0,
                fontName="Helvetica-Bold",
                borderWidth=1,
                borderColor=colors.black,
                borderPadding=4,
                backColor=colors.black,
            ),
            "subsection_header": ParagraphStyle(
                "subsection_header",
                parent=styles["Heading3"],
                fontSize=self.config.font_size + 1,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=3,
                spaceBefore=5,
                leftIndent=8,
                fontName="Helvetica-Bold",
            ),
            "hotkey": ParagraphStyle(
                "hotkey",
                parent=styles["Normal"],
                fontSize=self.config.font_size,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=1,
                leftIndent=0,
                fontName="Helvetica",
            ),
        }

        return custom_styles

    def _calculate_layout(self) -> Tuple[float, float]:
        """Calculate column width and usable page dimensions."""
        page_width, page_height = landscape(A4)
        usable_width = page_width - (2 * self.config.margin)
        usable_height = page_height - (2 * self.config.margin)

        column_spacing = 15
        column_width = (
            usable_width - (self.config.columns - 1) * column_spacing
        ) / self.config.columns

        return column_width, usable_height

    def _create_hotkey_table(self, hotkeys: List[Hotkey]) -> Table:
        """Create a table for hotkeys."""
        if not hotkeys:
            return None

        column_width, _ = self._calculate_layout()

        data = []
        for hotkey in hotkeys:
            from xml.sax.saxutils import escape

            escaped_key = escape(hotkey.key)
            escaped_desc = escape(hotkey.description)

            key_text = f"<font name='Courier-Bold'>{escaped_key}</font>"
            desc_text = escaped_desc

            data.append(
                [
                    Paragraph(key_text, self.styles["hotkey"]),
                    Paragraph(desc_text, self.styles["hotkey"]),
                ]
            )

        key_width = column_width * 0.35
        desc_width = column_width * 0.65

        table = Table(data, colWidths=[key_width, desc_width])
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), self.config.font_size),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.lightgrey),
                ]
            )
        )

        return table

    def _build_content(self) -> List:
        """Build the content for the PDF."""
        content = []

        title = Paragraph(self.cheat_sheet.title, self.styles["title"])
        content.append(title)
        content.append(Spacer(1, 12))

        sections = self.cheat_sheet.get_sections()

        section_items = []
        for section_name, subsections in sections.items():
            section_height = self._estimate_section_height(subsections)

            section_content = []

            section_header_text = f"<b>{section_name.upper()}</b>"
            section_header = Paragraph(
                section_header_text, self.styles["section_header"]
            )
            section_content.append(section_header)
            section_content.append(Spacer(1, 3))

            for subsection_name, hotkeys in subsections.items():
                if subsection_name != "General":
                    subsection_header_text = f"<i>{subsection_name}</i>"
                    subsection_header = Paragraph(
                        subsection_header_text, self.styles["subsection_header"]
                    )
                    section_content.append(subsection_header)

                table = self._create_hotkey_table(hotkeys)
                if table:
                    section_content.append(table)
                    section_content.append(Spacer(1, self.config.subsection_spacing))

            if section_height > 200:
                for i, (subsection_name, hotkeys) in enumerate(subsections.items()):
                    if i == 0:
                        subsection_content = [section_header, Spacer(1, 3)]
                    else:
                        subsection_content = []

                    if subsection_name != "General":
                        subsection_header_text = f"<i>{subsection_name}</i>"
                        subsection_header = Paragraph(
                            subsection_header_text, self.styles["subsection_header"]
                        )
                        subsection_content.append(subsection_header)

                    table = self._create_hotkey_table(hotkeys)
                    if table:
                        subsection_content.append(table)
                        subsection_content.append(
                            Spacer(1, self.config.subsection_spacing)
                        )

                    if len(subsection_content) > 0:
                        section_items.append(KeepTogether(subsection_content))

            elif section_height < 100:
                section_items.append(KeepTogether(section_content))
            else:
                section_items.extend(section_content)

            section_items.append(Spacer(1, self.config.section_spacing))

        content.extend(section_items)
        return content

    def _estimate_section_height(self, subsections: dict) -> float:
        """Estimate the height needed for a section."""
        total_height = 0

        total_height += self.config.header_font_size + 15

        for subsection_name, hotkeys in subsections.items():
            if subsection_name != "General":
                total_height += self.config.font_size + 8

            total_height += len(hotkeys) * self.config.row_height
            total_height += self.config.subsection_spacing

        total_height += self.config.section_spacing

        return total_height

    def generate(self, output_path: Path) -> None:
        """Generate the PDF cheat sheet."""
        doc = self._create_multicolumn_doc(output_path)
        content = self._build_content()
        doc.build(content)

    def _create_multicolumn_doc(self, output_path: Path) -> BaseDocTemplate:
        """Create a multi-column document template."""
        doc = BaseDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            topMargin=self.config.margin,
            bottomMargin=self.config.margin,
            leftMargin=self.config.margin,
            rightMargin=self.config.margin,
        )

        page_width, page_height = landscape(A4)
        frame_width = (
            page_width - 2 * self.config.margin - (self.config.columns - 1) * 15
        ) / self.config.columns
        frame_height = page_height - 2 * self.config.margin

        frames = []
        for i in range(self.config.columns):
            x = self.config.margin + i * (frame_width + 15)
            frame = Frame(
                x,
                self.config.margin,
                frame_width,
                frame_height,
                leftPadding=3,
                rightPadding=3,
                topPadding=6,
                bottomPadding=6,
                showBoundary=0,
            )
            frames.append(frame)

        template = PageTemplate(id="multicolumn", frames=frames)
        doc.addPageTemplates([template])

        return doc

    def estimate_pages(self) -> int:
        """Estimate the number of pages needed."""
        _, usable_height = self._calculate_layout()

        total_hotkeys = len(self.cheat_sheet.hotkeys)
        sections = self.cheat_sheet.get_sections()

        title_height = 30
        section_headers = len(sections) * 15
        subsection_headers = (
            sum(len(subsections) for subsections in sections.values()) * 12
        )
        hotkey_height = total_hotkeys * self.config.row_height
        spacing = len(sections) * self.config.section_spacing

        total_height = (
            title_height
            + section_headers
            + subsection_headers
            + hotkey_height
            + spacing
        )

        effective_height = total_height / self.config.columns

        pages = math.ceil(effective_height / usable_height)
        return max(1, pages)
