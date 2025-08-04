#!/usr/bin/env python3
"""Build script for creating standalone executables."""

import os
import platform
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout


def main():
    """Build executable for current platform."""
    system = platform.system()

    exe_name = "cheatsheet-gen"
    if system == "Windows":
        exe_name += ".exe"

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        exe_name.replace(".exe", ""),
        "--add-data",
        f"src/cheatsheet_generator{os.pathsep}cheatsheet_generator",
        "--hidden-import",
        "cheatsheet_generator.cli",
        "--hidden-import",
        "cheatsheet_generator.parser",
        "--hidden-import",
        "cheatsheet_generator.generator",
        "--hidden-import",
        "cheatsheet_generator.models",
        "--console",
        "src/cheatsheet_generator/cli.py",
    ]

    run_command(pyinstaller_cmd)

    dist_path = Path("dist") / exe_name
    if dist_path.exists():
        print(f" Successfully built executable: {dist_path}")
        print(f"Size: {dist_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print("Executable not found in dist/ directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
