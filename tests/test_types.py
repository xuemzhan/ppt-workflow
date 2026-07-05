"""Tests for shared/types.py — type definitions."""

from __future__ import annotations

import pytest

from skills.shared.types import (
    BulletItem,
    ChartSpec,
    OrchestratorConfig,
    SlideSpec,
    Spec,
    ThemeSpec,
)


class TestThemeSpec:
    """Tests for ThemeSpec dataclass."""

    def test_default_values(self) -> None:
        theme = ThemeSpec()
        assert theme.primary_color == "1E2761"
        assert theme.accent_color == "F96167"

    def test_custom_values(self) -> None:
        theme = ThemeSpec(primary_color="FF0000", accent_color="00FF00")
        assert theme.primary_color == "FF0000"

    def test_frozen(self) -> None:
        theme = ThemeSpec()
        try:
            theme.primary_color = "test"  # type: ignore[misc]
            pytest.fail("Should have raised")
        except AttributeError:
            pass


class TestSlideSpec:
    """Tests for SlideSpec dataclass."""

    def test_minimal(self) -> None:
        slide = SlideSpec(type="title")
        assert slide.type == "title"
        assert slide.title == ""

    def test_with_bullets(self) -> None:

        slide = SlideSpec(
            type="bullet",
            title="Test",
            bullets=[BulletItem(text="Point 1", level=0)],
        )
        assert len(slide.bullets) == 1


class TestSpec:
    """Tests for Spec dataclass."""

    def test_default_spec(self) -> None:
        spec = Spec()
        assert spec.theme.primary_color == "1E2761"
        assert spec.slides == []


class TestChartSpec:
    """Tests for ChartSpec dataclass."""

    def test_default(self) -> None:
        chart = ChartSpec()
        assert chart.chart_type == "bar"


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig dataclass."""

    def test_minimal(self) -> None:
        config = OrchestratorConfig(input_dir="in", output_dir="out")
        assert config.force is False
        assert config.verbose is False
