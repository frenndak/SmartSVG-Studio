"""V34-041/045/046 — gentle artisan themes for the standalone SmartSVG UI.

Framework-independent, CPU-only and offline. Never modifies a .smartsvg
project, a source image, an export, or CUT/SCORE semantic operation colors.

Design reference: docs/roadmap-v3.4/UX_UI_DESIGN_SYSTEM_ADDENDUM.md §3.1.
Tkinter, Qt and web shells may consume the same semantic tokens.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from types import MappingProxyType
from typing import Mapping

ACCENTS = MappingProxyType({
    "sage": ("Sauge", "#82A994"),
    "lavender": ("Lavande", "#A79BCB"),
    "lagoon": ("Lagune", "#75B8B5"),
    "dusty_rose": ("Rose poudré", "#D59EAA"),
    "peach": ("Pêche", "#DEA982"),
    "mist_blue": ("Bleu brume", "#90ACD0"),
})
APPEARANCES = frozenset(("light", "night", "automatic"))
MAX_PREFERENCES_BYTES = 2048

_BASE = MappingProxyType({
    "light": {
        "surface.app": "#F7F8F5",
        "surface.panel": "#FFFFFF",
        "surface.raised": "#EDF1EE",
        "text.primary": "#26322E",
        "text.secondary": "#59645F",
        "focus.ring": "#28675B",
    },
    "night": {
        "surface.app": "#202629",
        "surface.panel": "#2B3337",
        "surface.raised": "#354045",
        "text.primary": "#EBEFED",
        "text.secondary": "#B6C1BE",
        "focus.ring": "#BCE5D8",
    },
})

# Semantic manufacturing states are NEVER recolored by the cosmetic accent.
_OPERATION_LABELS = MappingProxyType({
    "CUT": "Découpe",
    "SCORE": "Rainurage",
    "DRAW": "Dessin",
    "FOIL": "Transfert de feuille",
})


class ThemePreferenceError(ValueError):
    """Preferences are invalid or the local destination is unsafe."""


@dataclass(frozen=True)
class ThemePreferences:
    appearance: str = "automatic"
    accent: str = "sage"
    reduced_motion: bool = False

    def __post_init__(self):
        if (type(self.appearance) is not str or self.appearance not in APPEARANCES
                or type(self.accent) is not str or self.accent not in ACCENTS
                or type(self.reduced_motion) is not bool):
            raise ThemePreferenceError("INVALID_THEME_PREFERENCES")


@dataclass(frozen=True)
class ResolvedTheme:
    appearance: str
    accent: str
    accent_label_fr: str
    colors: Mapping[str, str]
    reduced_motion: bool


def _linear(channel: int) -> float:
    v = channel / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(color: str) -> float:
    if (type(color) is not str or len(color) != 7 or color[0] != "#"
            or any(c not in "0123456789abcdefABCDEF" for c in color[1:])):
        raise ThemePreferenceError("INVALID_THEME_COLOR")
    channels = tuple(_linear(int(color[pos:pos + 2], 16)) for pos in (1, 3, 5))
    return sum(a * b for a, b in zip((0.2126, 0.7152, 0.0722), channels))


def contrast_ratio(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def resolve_theme(preferences: ThemePreferences, *, system_dark: bool | None = None) -> ResolvedTheme:
    """Resolve display-only colors; no OS calls and no modifications to data."""
    if not isinstance(preferences, ThemePreferences):
        raise ThemePreferenceError("INVALID_THEME_PREFERENCES")
    if system_dark is not None and type(system_dark) is not bool:
        raise ThemePreferenceError("INVALID_SYSTEM_THEME")
    appearance = ("night" if system_dark is True else "light") if (
        preferences.appearance == "automatic") else preferences.appearance
    label, accent = ACCENTS[preferences.accent]
    base = dict(_BASE[appearance])
    dark_ink = "#1D2927"
    light_ink = "#FFFFFF"
    readable = max((dark_ink, light_ink), key=lambda text: contrast_ratio(text, accent))
    if contrast_ratio(readable, accent) < 4.5:
        raise ThemePreferenceError("ACCENT_CONTRAST_INSUFFICIENT")
    base.update({
        "action.accent": accent,
        "action.accent_text": readable,
        # The canvas has its own intentionally neutral and stable rendering
        # background independent of application and accent choices.
        "canvas.white": "#FFFFFF",
        "canvas.neutral": "#EBECEA",
        "canvas.checker.light": "#FFFFFF",
        "canvas.checker.dark": "#DBDEDA",
        "status.error": "#9F3333" if appearance == "light" else "#FFC1BA",
        "status.warning": "#7D5614" if appearance == "light" else "#F6D89C",
    })
    return ResolvedTheme(
        appearance=appearance, accent=preferences.accent,
        accent_label_fr=label, colors=MappingProxyType(base),
        reduced_motion=preferences.reduced_motion,
    )


def _unique_pairs(items):
    parsed = {}
    for key, value in items:
        if key in parsed:
            raise ThemePreferenceError("DUPLICATE_PREFERENCE")
        parsed[key] = value
    return parsed


def _preferences_path(path: str | Path) -> Path:
    try:
        target = Path(path)
        if (target.suffix.lower() != ".json" or target.is_symlink()
                or not target.parent.is_dir() or target.parent.is_symlink()):
            raise ThemePreferenceError("UNSAFE_PREFERENCES_PATH")
        return target
    except (TypeError, OSError, ValueError) as exc:
        raise ThemePreferenceError("UNSAFE_PREFERENCES_PATH") from exc


def load_theme_preferences(path: str | Path) -> ThemePreferences:
    """Read bounded local settings. Any corruption returns safe defaults."""
    try:
        target = _preferences_path(path)
        if not target.is_file() or target.stat().st_size > MAX_PREFERENCES_BYTES:
            return ThemePreferences()
        with target.open("rb") as source:
            raw = source.read(MAX_PREFERENCES_BYTES + 1)
        if len(raw) > MAX_PREFERENCES_BYTES:
            return ThemePreferences()
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
        if (type(value) is not dict or
                set(value) != {"appearance", "accent", "reduced_motion"}):
            return ThemePreferences()
        return ThemePreferences(**value)
    except (OSError, ValueError, TypeError, UnicodeError):
        return ThemePreferences()


def save_theme_preferences(path: str | Path, preferences: ThemePreferences) -> None:
    """Atomic settings write to an explicitly chosen LOCAL config JSON file.

    No project data enters the settings file. The caller owns the choice of
    local config directory and must not pass a project resource path.
    """
    if not isinstance(preferences, ThemePreferences):
        raise ThemePreferenceError("INVALID_THEME_PREFERENCES")
    target = _preferences_path(path)
    payload = json.dumps({
        "appearance": preferences.appearance,
        "accent": preferences.accent,
        "reduced_motion": preferences.reduced_motion,
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".smartsvg-theme-", suffix=".tmp",
            dir=target.parent, delete=False
        ) as stream:
            temp = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if target.is_symlink():
            raise ThemePreferenceError("UNSAFE_PREFERENCES_PATH")
        os.replace(temp, target)
        temp = None
    except OSError as exc:
        raise ThemePreferenceError("PREFERENCES_SAVE_FAILED") from exc
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
