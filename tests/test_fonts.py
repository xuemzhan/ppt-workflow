"""Tests for shared/fonts.py — font discovery."""

from __future__ import annotations

from skills.shared.fonts import (
    check_font_availability,
    get_font_path,
    get_font_path_optional,
)


class TestGetFontPath:
    """Tests for font path resolution."""

    def test_returns_string(self) -> None:
        result = get_font_path()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_specific_font(self) -> None:
        # Should not raise even if font doesn't exist
        result = get_font_path("nonexistent_font.ttf")
        assert isinstance(result, str)


class TestGetFontPathOptional:
    """Tests for optional font path resolution."""

    def test_returns_string_or_none(self) -> None:
        result = get_font_path_optional()
        assert result is None or isinstance(result, str)


class TestCheckFontAvailability:
    """Tests for font availability check."""

    def test_returns_dict(self) -> None:
        result = check_font_availability()
        assert isinstance(result, dict)
        for value in result.values():
            assert isinstance(value, bool)
