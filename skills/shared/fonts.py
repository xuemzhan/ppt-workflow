"""Cross-platform font discovery and resolution.

Provides a single get_font_path() that works across Windows, macOS, and Linux
with graceful fallback to system defaults.
"""

from __future__ import annotations

import platform
from pathlib import Path

# Platform-specific font search paths
_FONT_SEARCH_PATHS: dict[str, list[Path]] = {
    "Windows": [
        Path("C:/Windows/Fonts"),
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
    ],
    "Darwin": [  # macOS
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
    ],
    "Linux": [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".local/share/fonts",
    ],
}

# Preferred font families in priority order (CJK-aware)
_PREFERRED_FONTS: list[list[str]] = [
    # Chinese (Simplified)优先
    ["msyh.ttc", "msyhbd.ttc", "msyhl.ttc"],  # Microsoft YaHei
    ["PingFang.ttc", "PingFang SC.ttc"],  # macOS
    ["NotoSansCJK-Regular.ttc", "NotoSansSC-Regular.otf"],  # Linux
    ["SourceHanSansCN-Regular.otf", "SourceHanSansSC-Regular.otf"],  # Adobe
    ["SimSun.ttc", "simsun.ttc"],  # 宋体 fallback
    # Generic sans-serif fallback
    ["arial.ttf", "Arial.ttf"],
    ["DejaVuSans.ttf"],
]

# Fallback to Pillow if available
_PILLOW_FONT: str | None = None

try:
    from PIL import ImageFont

    _default_font = ImageFont.load_default()
    # Pillow's default font is always available
    _PILLOW_FONT = "PIL_DEFAULT"
except ImportError:
    pass


def _get_search_paths() -> list[Path]:
    """Get platform-specific font search directories."""
    system = platform.system()
    paths = _FONT_SEARCH_PATHS.get(system, [])
    return [p for p in paths if p.exists()]


def _find_font_in_dirs(font_names: list[str], search_dirs: list[Path]) -> Path | None:
    """Search for a font file in the given directories."""
    for search_dir in search_dirs:
        for font_name in font_names:
            font_path = search_dir / font_name
            if font_path.exists():
                return font_path
    return None


def get_font_path(font_name: str | None = None) -> str:
    """Get the path to a suitable font for text rendering.

    Args:
        font_name: Specific font filename to look for (e.g. 'msyh.ttc').
                   If None, uses the preferred CJK font chain.

    Returns:
        Font file path as a string. Returns 'PIL_DEFAULT' if no font found
        and Pillow is available, otherwise raises FileNotFoundError.
    """
    search_dirs = _get_search_paths()

    # If specific font requested, try to find it
    if font_name is not None:
        result = _find_font_in_dirs([font_name], search_dirs)
        if result is not None:
            return str(result)

    # Try preferred font families in order
    for font_family in _PREFERRED_FONTS:
        result = _find_font_in_dirs(font_family, search_dirs)
        if result is not None:
            return str(result)

    # Last resort: Pillow default
    if _PILLOW_FONT is not None:
        return _PILLOW_FONT

    raise FileNotFoundError(
        f"No suitable font found. Searched: {[str(d) for d in search_dirs]}. "
        "Install a CJK font (e.g., Noto Sans CJK) or Microsoft YaHei."
    )


def get_font_path_optional(font_name: str | None = None) -> str | None:
    """Like get_font_path() but returns None instead of raising.

    Args:
        font_name: Specific font filename to look for.

    Returns:
        Font path or None if not found.
    """
    try:
        return get_font_path(font_name)
    except FileNotFoundError:
        return None


def check_font_availability() -> dict[str, bool]:
    """Check which preferred fonts are available on this system.

    Returns:
        Dict mapping font family names to availability status.
    """
    search_dirs = _get_search_paths()
    result: dict[str, bool] = {}
    for font_family in _PREFERRED_FONTS:
        key = font_family[0]  # Use primary font name as key
        result[key] = _find_font_in_dirs(font_family, search_dirs) is not None
    return result
