"""V34-045/046 — artisan theme picker for the standalone Tk *prototype*.

This adapter only styles the native shell. It does NOT choose the final GUI
framework, modify a .smartsvg project, color manufacturing operations or use
ComfyUI. tkinter is injected by the desktop entry point and never imported
here, so the offline `--probe` can still run with Python -I -S.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys

from smartsvg_core.native_theme_v34 import (
    ACCENTS, ThemePreferenceError, ThemePreferences,
    load_theme_preferences, resolve_theme, save_theme_preferences,
)

MODE_LABELS = {
    "light": "Clair",
    "night": "Nuit douce",
    "automatic": "Automatique (Windows)",
}
LABEL_MODES = {label: mode for mode, label in MODE_LABELS.items()}


def local_theme_path(*, platform: str | None = None, env=None, home=None) -> Path:
    """Provide a LOCAL config location, never inside a project .smartsvg.

    Parameters are injectable so Windows and Linux paths can be tested without
    touching user data or importing Windows-only libraries on Linux.
    """
    platform = sys.platform if platform is None else platform
    env = os.environ if env is None else env
    home = Path.home() if home is None else Path(home)
    if platform == "win32":
        value = env.get("LOCALAPPDATA")
        base = Path(value) if value else home / "AppData" / "Local"
        if not base.is_absolute():
            base = home / "AppData" / "Local"
        return base / "SmartSVG Studio" / "appearance.json"
    value = env.get("XDG_CONFIG_HOME")
    base = Path(value) if value else home / ".config"
    if not base.is_absolute():
        base = home / ".config"
    return base / "smartsvg-studio" / "appearance.json"


def windows_system_dark() -> bool | None:
    """Read Windows app theme, no network; None means unknown -> light fallback."""
    if sys.platform != "win32":
        return None
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        ) as key:
            return not bool(winreg.QueryValueEx(key, "AppsUseLightTheme")[0])
    except (ImportError, OSError, ValueError, TypeError):
        return None


class ArtisanThemePicker:
    """Small theme controls with instant display-only updates and local saving."""

    def __init__(self, *, root, parent, tk, ttk, settings_path=None):
        self.root = root
        self.tk = tk
        self.ttk = ttk
        self.settings_path = (Path(settings_path) if settings_path is not None
                              else local_theme_path())
        self.prefs = load_theme_preferences(self.settings_path)
        self.appearance_var = tk.StringVar(value=MODE_LABELS[self.prefs.appearance])
        self.motion_var = tk.BooleanVar(value=self.prefs.reduced_motion)
        self.status_var = tk.StringVar(value="Préférences locales, sans modifier vos créations.")
        self.style = ttk.Style(root)
        # The clam theme respects per-widget semantic foreground/background
        # values on more platforms than the Windows native ttk theme.
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        self._swatches = {}
        self._last_effective = None

        self.section = ttk.LabelFrame(parent, text="Personnaliser mon espace")
        self.section.pack(fill="x", pady=(0, 14))
        line = ttk.Frame(self.section)
        line.pack(fill="x", padx=12, pady=(9, 7))
        ttk.Label(line, text="Apparence :").pack(side="left")
        self.appearance = ttk.Combobox(
            line, textvariable=self.appearance_var, state="readonly",
            values=tuple(MODE_LABELS.values()), width=24,
        )
        self.appearance.pack(side="left", padx=(9, 24))
        self.appearance.bind("<<ComboboxSelected>>", self._on_appearance)
        self.motion = ttk.Checkbutton(
            line, text="Animations réduites", variable=self.motion_var,
            command=self._on_motion,
        )
        self.motion.pack(side="left")

        swatches = ttk.Frame(self.section)
        swatches.pack(fill="x", padx=12)
        for key, (label, hex_color) in ACCENTS.items():
            safe_ink = resolve_theme(ThemePreferences(accent=key)).colors[
                "action.accent_text"]
            button = tk.Button(
                swatches, text=label, bg=hex_color, fg=safe_ink,
                activebackground=hex_color, activeforeground=safe_ink,
                relief="flat", borderwidth=2, padx=7, pady=4,
                highlightthickness=2, takefocus=True,
                command=lambda chosen=key: self._on_accent(chosen),
            )
            button.pack(side="left", padx=(0, 7), pady=(1, 7))
            self._swatches[key] = button

        ttk.Label(
            self.section, textvariable=self.status_var,
            wraplength=680,
        ).pack(anchor="w", padx=12, pady=(0, 8))

        self.apply()
        self.root.after(3500, self._check_system_theme)

    def _save(self):
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            save_theme_preferences(self.settings_path, self.prefs)
        except (OSError, ThemePreferenceError):
            self.status_var.set(
                "Apparence appliquée, mais impossible d'enregistrer la préférence locale.")
        else:
            self.status_var.set("Apparence enregistrée localement.")

    def _on_appearance(self, _event=None):
        requested = LABEL_MODES.get(self.appearance_var.get())
        if requested is None:
            return
        self.prefs = ThemePreferences(
            appearance=requested, accent=self.prefs.accent,
            reduced_motion=self.prefs.reduced_motion,
        )
        self.apply()
        self._save()

    def _on_motion(self):
        self.prefs = ThemePreferences(
            appearance=self.prefs.appearance, accent=self.prefs.accent,
            reduced_motion=bool(self.motion_var.get()),
        )
        self.apply()
        self._save()

    def _on_accent(self, key):
        self.prefs = ThemePreferences(
            appearance=self.prefs.appearance, accent=key,
            reduced_motion=self.prefs.reduced_motion,
        )
        self.apply()
        self._save()

    def apply(self):
        system_dark = (windows_system_dark() if self.prefs.appearance == "automatic"
                       else None)
        theme = resolve_theme(self.prefs, system_dark=system_dark)
        colors = theme.colors
        self.root.configure(background=colors["surface.app"])
        self.style.configure("TFrame", background=colors["surface.panel"])
        self.style.configure("TLabel", background=colors["surface.panel"],
                             foreground=colors["text.primary"])
        self.style.configure("TButton", background=colors["surface.raised"],
                             foreground=colors["text.primary"],
                             padding=(9, 6))
        self.style.configure("TCheckbutton", background=colors["surface.panel"],
                             foreground=colors["text.primary"])
        self.style.configure("TLabelframe", background=colors["surface.panel"],
                             foreground=colors["text.primary"])
        self.style.configure("TLabelframe.Label", background=colors["surface.panel"],
                             foreground=colors["text.primary"])
        self.style.configure("TCombobox", background=colors["surface.raised"],
                             fieldbackground=colors["surface.raised"],
                             foreground=colors["text.primary"])
        self.style.map("TButton", background=[
            ("active", colors["action.accent"])
        ])
        for key, button in self._swatches.items():
            selected = key == self.prefs.accent
            label = ACCENTS[key][0]
            button.configure(
                text=("✓ " if selected else "") + label,
                relief="solid" if selected else "flat",
                borderwidth=3 if selected else 1,
                highlightbackground=colors["focus.ring"],
                highlightcolor=colors["focus.ring"],
                # Keep focus visible even when selection is not active.
            )
        self._last_effective = (theme.appearance, theme.accent)
        return theme

    def _check_system_theme(self):
        try:
            if not self.root.winfo_exists():
                return
            if self.prefs.appearance == "automatic":
                current = resolve_theme(
                    self.prefs, system_dark=windows_system_dark()).appearance
                if self._last_effective is None or current != self._last_effective[0]:
                    self.apply()
            self.root.after(3500, self._check_system_theme)
        except self.tk.TclError:
            return
