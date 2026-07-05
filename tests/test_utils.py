"""Tests for shared/utils.py — shared utility functions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from skills.shared.utils import (
    ensure_dir,
    find_script,
    hex_to_rgb,
    load_json,
    load_spec,
    project_root,
    read_text,
    write_json,
    write_text,
)


class TestHexToRgb:
    """Tests for hex_to_rgb conversion."""

    def test_valid_hex_no_hash(self) -> None:
        assert hex_to_rgb("1E2761") == (30, 39, 97)

    def test_valid_hex_with_hash(self) -> None:
        assert hex_to_rgb("#1E2761") == (30, 39, 97)

    def test_black(self) -> None:
        assert hex_to_rgb("000000") == (0, 0, 0)

    def test_white(self) -> None:
        assert hex_to_rgb("FFFFFF") == (255, 255, 255)

    def test_lowercase_hex(self) -> None:
        assert hex_to_rgb("ff6167") == (255, 97, 103)

    def test_invalid_length(self) -> None:
        with pytest.raises(ValueError, match="Invalid hex color"):
            hex_to_rgb("1E27")

    def test_invalid_hex_chars(self) -> None:
        with pytest.raises(ValueError, match="Invalid hex color"):
            hex_to_rgb("GGGGGG")


class TestEnsureDir:
    """Tests for ensure_dir."""

    def test_creates_directory(self, tmp_path: Path) -> None:
        new_dir = tmp_path / "new_dir" / "subdir"
        result = ensure_dir(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_existing_directory(self, tmp_path: Path) -> None:
        result = ensure_dir(tmp_path)
        assert result.exists()
        assert result == tmp_path


class TestLoadJson:
    """Tests for load_json."""

    def test_valid_json(self, tmp_path: Path) -> None:
        data = {"key": "value", "num": 42}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))
        assert load_json(json_file) == data

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="JSON file not found"):
            load_json(tmp_path / "missing.json")

    def test_invalid_json(self, tmp_path: Path) -> None:
        json_file = tmp_path / "bad.json"
        json_file.write_text("{invalid json}")
        with pytest.raises(json.JSONDecodeError):
            load_json(json_file)


class TestLoadSpec:
    """Tests for load_spec."""

    def test_valid_spec(self, tmp_path: Path) -> None:
        spec = {"slides": [{"type": "title", "title": "Hello"}]}
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps(spec))
        assert load_spec(spec_file) == spec

    def test_missing_slides_key(self, tmp_path: Path) -> None:
        spec = {"theme": "test"}
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps(spec))
        with pytest.raises(ValueError, match="must contain a 'slides' key"):
            load_spec(spec_file)

    def test_not_a_dict(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps([1, 2, 3]))
        with pytest.raises(ValueError, match="must be a JSON object"):
            load_spec(spec_file)


class TestWriteJson:
    """Tests for write_json."""

    def test_writes_json(self, tmp_path: Path) -> None:
        data = {"test": True}
        result = write_json(tmp_path / "out.json", data)
        assert result.exists()
        assert json.loads(result.read_text()) == data


class TestReadWriteText:
    """Tests for read_text and write_text."""

    def test_roundtrip(self, tmp_path: Path) -> None:
        content = "Hello, 世界!"
        result = write_text(tmp_path / "test.txt", content)
        assert read_text(result) == content


class TestProjectRoot:
    """Tests for project root detection."""

    def test_finds_root(self) -> None:
        root = project_root()
        assert (root / "README.md").exists() or (root / "pyproject.toml").exists()


class TestFindScript:
    """Tests for script discovery."""

    def test_finds_known_script(self) -> None:
        script = find_script("pptx-generator", "spec_to_pptx.py")
        assert script.exists()

    def test_raises_on_missing(self) -> None:
        with pytest.raises(FileNotFoundError, match="Script not found"):
            find_script("nonexistent", "missing.py")
