"""Shared utility functions for the PPT workflow pipeline.

Single source of truth for common operations used across all skills.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple.

    Args:
        hex_color: Hex color string, e.g. '1E2761' or '#1E2761'.

    Returns:
        Tuple of (r, g, b) values, each in [0, 255].

    Raises:
        ValueError: If hex_color is not a valid 6-digit hex string.
    """
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r} (expected 6-digit hex)")
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
    except ValueError:
        msg = f"Invalid hex color: {hex_color!r} (not valid hex digits)"
        raise ValueError(msg) from None
    return (r, g, b)


def ensure_dir(path: str | Path) -> Path:
    """Create directory if it doesn't exist, return as Path.

    Args:
        path: Directory path to create.

    Returns:
        The directory as a Path object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: str | Path) -> Any:
    """Load a JSON file and return its contents.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def load_spec(path: str | Path) -> dict[str, Any]:
    """Load a spec.json file with validation.

    Args:
        path: Path to the spec JSON file.

    Returns:
        Parsed spec as a dictionary.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file doesn't contain a valid spec structure.
    """
    data = load_json(path)
    if not isinstance(data, dict):
        raise TypeError(f"Spec must be a JSON object, got {type(data).__name__}")
    if "slides" not in data:
        raise ValueError("Spec must contain a 'slides' key")
    return data


def write_json(path: str | Path, data: Any, indent: int = 2) -> Path:
    """Write data to a JSON file.

    Args:
        path: Output file path.
        data: Data to serialize.
        indent: JSON indentation level.

    Returns:
        The written file path.
    """
    p = Path(path)
    ensure_dir(p.parent)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    return p


def read_text(path: str | Path) -> str:
    """Read a text file and return its contents.

    Args:
        path: Path to the text file.

    Returns:
        File contents as string.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Text file not found: {p}")
    return p.read_text(encoding="utf-8")


def write_text(path: str | Path, content: str) -> Path:
    """Write text to a file.

    Args:
        path: Output file path.
        content: Text content to write.

    Returns:
        The written file path.
    """
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(content, encoding="utf-8")
    return p


def project_root() -> Path:
    """Find the project root by looking for README.md or pyproject.toml.

    Returns:
        Path to the project root directory.

    Raises:
        RuntimeError: If project root cannot be determined.
    """
    current = Path(__file__).resolve().parent
    # Walk up from skills/shared/ to find project root
    for parent in [current, *current.parents]:
        if (parent / "README.md").exists() or (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError(
        "Cannot determine project root (no README.md or pyproject.toml found)"
    )


def skills_dir() -> Path:
    """Get the skills directory path.

    Returns:
        Path to the skills/ directory.
    """
    return project_root() / "skills"


def find_script(skill_name: str, script_name: str) -> Path:
    """Find a script in the skills directory.

    Args:
        skill_name: Name of the skill directory.
        script_name: Name of the Python script.

    Returns:
        Full path to the script.

    Raises:
        FileNotFoundError: If the script doesn't exist.
    """
    script_path = skills_dir() / skill_name / "scripts" / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    return script_path
