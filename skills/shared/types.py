"""Type definitions for PPT workflow data contracts.

Provides TypedDict and dataclass models for the various JSON schemas
used across the pipeline (spec.json, slides.json, chart specs, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

# ──────────────────────────────────────────────────────────────
# slides.json (orchestrator input)
# ──────────────────────────────────────────────────────────────


class SlideItem(TypedDict, total=False):
    """A single slide in slides.json."""

    section: str
    title: str
    points: list[str]
    evidence: str
    chart_needed: bool
    chart_type: str
    viz_type: str
    source: str
    minutes: float


class SlidesJson(TypedDict, total=False):
    """Top-level structure of slides.json."""

    theme: str
    audience: str
    scenario: str
    slides: list[SlideItem]


# ──────────────────────────────────────────────────────────────
# spec.json (pptx-generator input)
# ──────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ThemeSpec:
    """Color theme for the deck."""

    primary_color: str = "1E2761"
    accent_color: str = "F96167"
    secondary_color: str = "CADCFC"


@dataclass(frozen=True, slots=True)
class BulletItem:
    """A single bullet point."""

    text: str
    level: int = 0


@dataclass(frozen=True, slots=True)
class StatItem:
    """A statistic for stat slides."""

    value: str
    label: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class ProcessStep:
    """A step in a process slide."""

    title: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    """An event in a timeline slide."""

    date: str
    title: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class TwoColumnLeft:
    """Left column of a two-column slide."""

    heading: str = ""
    items: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TwoColumnRight:
    """Right column of a two-column slide."""

    heading: str = ""
    items: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SlideSpec:
    """A single slide specification."""

    # one of: title, bullet, two_column, stat, quote, process,
    #         table, timeline, section, thank_you
    type: str
    title: str = ""
    section_number: str = ""
    subtitle: str = ""
    author: str = ""
    date: str = ""
    bullets: list[BulletItem] = field(default_factory=list)
    stats: list[StatItem] = field(default_factory=list)
    text: str = ""
    attribution: str = ""
    steps: list[ProcessStep] = field(default_factory=list)
    headers: list[str] = field(
        default_factory=list,
    )
    rows: list[list[str]] = field(default_factory=list)
    events: list[TimelineEvent] = field(default_factory=list)
    left: TwoColumnLeft = field(default_factory=TwoColumnLeft)
    right: TwoColumnRight = field(default_factory=TwoColumnRight)
    note: str = ""
    image: str = ""


@dataclass(frozen=True, slots=True)
class Spec:
    """Top-level spec.json structure."""

    theme: ThemeSpec = field(default_factory=ThemeSpec)
    slides: list[SlideSpec] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────
# Chart spec (chart-slide-maker input)
# ──────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ChartSpec:
    """Specification for a single chart."""

    title: str = ""
    chart_type: str = "bar"  # bar, line, pie, scatter
    x_label: str = ""
    y_label: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    output_path: str = ""


# ──────────────────────────────────────────────────────────────
# Orchestrator state
# ──────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class OrchestratorConfig:
    """Configuration for the pipeline orchestrator."""

    input_dir: str
    output_dir: str
    theme: str = ""
    audience: str = ""
    scenario: str = ""
    template: str = ""
    force: bool = False
    skip_outline: bool = False
    skip_storyline: bool = False
    skip_template: bool = False
    skip_notes: bool = False
    skip_qa: bool = False
    verbose: bool = False
