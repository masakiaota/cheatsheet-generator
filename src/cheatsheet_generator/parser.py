from pathlib import Path
from typing import Any, Dict, List

import yaml

from cheatsheet_generator.models import CheatSheet, CheatSheetConfig, Hotkey


class YAMLParser:
    @staticmethod
    def parse_file(file_path: Path) -> CheatSheet:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return YAMLParser.parse_dict(data)

    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> CheatSheet:
        if not isinstance(data, dict):
            raise ValueError("YAML data must be a dictionary")

        title = data.get("title", "Hotkey Cheat Sheet")
        config_data = data.get("config", {})
        config = CheatSheetConfig.from_dict(config_data)
        config.title = title

        hotkeys = []
        sections_data = data.get("sections", {})

        for section_name, section_data in sections_data.items():
            if not isinstance(section_data, dict):
                continue

            for subsection_name, subsection_data in section_data.items():
                if isinstance(subsection_data, dict):
                    for key, description in subsection_data.items():
                        hotkeys.append(
                            Hotkey(
                                key=key,
                                description=description,
                                section=section_name,
                                subsection=subsection_name,
                            )
                        )
                else:
                    hotkeys.append(
                        Hotkey(
                            key=subsection_name,
                            description=subsection_data,
                            section=section_name,
                        )
                    )

        return CheatSheet(title=title, hotkeys=hotkeys, config=config)

    @staticmethod
    def validate_yaml(file_path: Path) -> List[str]:
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {e}")
            return errors
        except FileNotFoundError:
            errors.append(f"File not found: {file_path}")
            return errors

        if not isinstance(data, dict):
            errors.append("Root element must be a dictionary")
            return errors

        if "sections" not in data:
            errors.append("Missing 'sections' key")
            return errors

        sections = data["sections"]
        if not isinstance(sections, dict):
            errors.append("'sections' must be a dictionary")
            return errors

        for section_name, section_data in sections.items():
            if not isinstance(section_data, dict):
                errors.append(f"Section '{section_name}' must be a dictionary")
                continue

            if not section_data:
                errors.append(f"Section '{section_name}' is empty")

        return errors
