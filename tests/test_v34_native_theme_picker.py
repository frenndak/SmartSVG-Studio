"""V34-046 UX-13/18: artisan theme controls in the standalone shell.

Mocked widgets prove callbacks and storage; these tests DO NOT certify actual
Tk rendering, Windows contrast, high-DPI layout or accessibility.
"""
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import json.scanner
import subprocess
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_theme_tk_v34 import (
    ArtisanThemePicker, local_theme_path, windows_system_dark, MODE_LABELS
)
from smartsvg_core.native_theme_v34 import (
    ACCENTS, ThemePreferences, contrast_ratio, load_theme_preferences,
)


class FakeVar:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, new):
        self.value = new


class FakeWidget:
    def __init__(self, *_args, **kwargs):
        self.values = dict(kwargs)

    def pack(self, **_kwargs):
        return None

    def bind(self, *_args):
        return None

    def configure(self, **kwargs):
        self.values.update(kwargs)


class FakeRoot(FakeWidget):
    def __init__(self):
        super().__init__()
        self.callbacks = []

    def after(self, ms, callback):
        self.callbacks.append((ms, callback))

    def winfo_exists(self):
        return True


class FakeStyle:
    def __init__(self, _root):
        self.rules = {}
        self.active_theme = None

    def theme_names(self):
        return ("clam", "default")

    def theme_use(self, theme):
        self.active_theme = theme

    def configure(self, name, **kwargs):
        self.rules[name] = kwargs

    def map(self, name, **kwargs):
        self.rules[name + "/map"] = kwargs


class NativeThemePickerTests(unittest.TestCase):
    def widgets(self):
        tk = SimpleNamespace(
            StringVar=FakeVar, BooleanVar=FakeVar, Button=FakeWidget,
            TclError=RuntimeError,
        )
        ttk = SimpleNamespace(
            Style=FakeStyle, LabelFrame=FakeWidget, Frame=FakeWidget,
            Label=FakeWidget, Combobox=FakeWidget, Checkbutton=FakeWidget,
        )
        return tk, ttk

    def test_windows_local_config_path_outside_project(self):
        home = Path("C:/Users/Creator")
        env = {"LOCALAPPDATA": "C:/Users/Creator/AppData/Local"}
        path = local_theme_path(platform="win32", env=env, home=home)
        self.assertEqual(path.name, "appearance.json")
        self.assertEqual(path.parent.name, "SmartSVG Studio")
        self.assertNotIn(".smartsvg", str(path))
        # Relative LOCALAPPDATA must be ignored (not a project-relative path).
        fallback = local_theme_path(platform="win32",
                                    env={"LOCALAPPDATA": "relative"},
                                    home=home)
        self.assertTrue(str(fallback).endswith("SmartSVG Studio/appearance.json")
                        or str(fallback).endswith("SmartSVG Studio\\appearance.json"))
        self.assertNotIn("relative", str(fallback))

    def test_posix_config_falls_back_without_xdg(self):
        home = Path("/tmp/creator")
        path = local_theme_path(platform="linux", env={}, home=home)
        self.assertEqual(path, home / ".config" / "smartsvg-studio" / "appearance.json")
        relative = local_theme_path(platform="linux",
                                    env={"XDG_CONFIG_HOME": "somewhere"},
                                    home=home)
        self.assertEqual(relative, path)

    def test_headless_offline_probe_has_no_tk_import(self):
        with TemporaryDirectory() as tmp:
            output = subprocess.run(
                [sys.executable, "-I", "-S", str(ENGINE / "standalone_desktop_v34.py"),
                 "--probe"], cwd=tmp, capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(output.returncode, 0, output.stderr)
            state = json.loads(output.stdout)
            self.assertTrue(state["ok"])
            self.assertTrue(state["tkinter_lazy"])
            self.assertFalse(state["comfyui_required"])

    def test_picker_changes_accent_and_night_mode_without_touching_project(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            project = folder / "illustration.smartsvg"
            project.write_bytes(b"original project - no styling in archive")
            before = project.read_bytes()
            pref_path = folder / "appearance.json"
            tk, ttk = self.widgets()
            root = FakeRoot()
            picker = ArtisanThemePicker(
                root=root, parent=FakeWidget(), tk=tk, ttk=ttk,
                settings_path=pref_path,
            )
            self.assertEqual(picker.prefs.accent, "sage")
            self.assertEqual(picker.prefs.appearance, "automatic")
            self.assertIn("sage", picker._swatches)
            self.assertEqual(len(picker._swatches), 6)
            picker._on_accent("lavender")
            picker.appearance_var.set(MODE_LABELS["night"])
            picker._on_appearance()
            picker.motion_var.set(True)
            picker._on_motion()
            loaded = load_theme_preferences(pref_path)
            self.assertEqual(loaded, ThemePreferences(
                accent="lavender", appearance="night", reduced_motion=True))
            self.assertEqual(root.values["background"], "#202629")
            self.assertTrue(picker._swatches["lavender"].values["text"].startswith("✓ "))
            self.assertNotIn("✓", picker._swatches["sage"].values["text"])
            self.assertIn("enregistrée", picker.status_var.get())
            self.assertEqual(project.read_bytes(), before)

    def test_nested_corrupt_preferences_do_not_block_picker_startup(self):
        with TemporaryDirectory() as tmp:
            location = Path(tmp) / "appearance.json"
            project = Path(tmp) / "creation.smartsvg"
            project.write_bytes(b"original creation")
            payload = b"[" * 1000 + b"]" * 1000
            location.write_bytes(payload)
            tk, ttk = self.widgets()
            with patch("json.scanner.make_scanner", json.scanner.py_make_scanner):
                picker = ArtisanThemePicker(root=FakeRoot(), parent=FakeWidget(),
                                            tk=tk, ttk=ttk, settings_path=location)
            self.assertEqual(picker.prefs, ThemePreferences())
            self.assertEqual(location.read_bytes(), payload, "opening never silently repairs a file")
            picker._on_accent("lagoon")  # an explicit user action may save valid preferences
            self.assertEqual(load_theme_preferences(location).accent, "lagoon")
            self.assertEqual(project.read_bytes(), b"original creation")

    def test_reopening_restores_saved_preferences(self):
        with TemporaryDirectory() as tmp:
            location = Path(tmp) / "appearance.json"
            tk, ttk = self.widgets()
            picker = ArtisanThemePicker(root=FakeRoot(), parent=FakeWidget(),
                                        tk=tk, ttk=ttk, settings_path=location)
            picker._on_accent("peach")
            picker.appearance_var.set(MODE_LABELS["night"])
            picker._on_appearance()
            fresh = ArtisanThemePicker(root=FakeRoot(), parent=FakeWidget(),
                                       tk=tk, ttk=ttk, settings_path=location)
            self.assertEqual(fresh.prefs.accent, "peach")
            self.assertEqual(fresh.prefs.appearance, "night")
            self.assertEqual(fresh._last_effective[0], "night")

    def test_corrupt_preferences_do_not_break_picker(self):
        with TemporaryDirectory() as tmp:
            location = Path(tmp) / "appearance.json"
            location.write_bytes(b"not json")
            tk, ttk = self.widgets()
            picker = ArtisanThemePicker(root=FakeRoot(), parent=FakeWidget(),
                                        tk=tk, ttk=ttk, settings_path=location)
            self.assertEqual(picker.prefs.accent, "sage")
            self.assertEqual(picker._last_effective[0], "light")

    def test_ui_change_remains_temporary_when_settings_cannot_be_saved(self):
        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "missing" / "appearance.json"
            tk, ttk = self.widgets()
            picker = ArtisanThemePicker(root=FakeRoot(), parent=FakeWidget(),
                                        tk=tk, ttk=ttk, settings_path=bad)
            with patch("native_theme_tk_v34.save_theme_preferences",
                       side_effect=OSError("disk full")):
                picker._on_accent("lagoon")
            self.assertEqual(picker.prefs.accent, "lagoon")
            self.assertIn("impossible", picker.status_var.get())

    def test_active_button_text_remains_readable_for_all_twelve_combinations(self):
        # Regression: a pastel hover background must not retain pale night text.
        tk, ttk = self.widgets()
        for mode in ("light", "night"):
            for accent in ACCENTS:
                with self.subTest(mode=mode, accent=accent):
                    picker = ArtisanThemePicker(
                        root=FakeRoot(), parent=FakeWidget(), tk=tk, ttk=ttk,
                    )
                    picker.prefs = ThemePreferences(appearance=mode, accent=accent)
                    theme = picker.apply()
                    mapping = picker.style.rules["TButton/map"]
                    hover_background = mapping["background"][0][1]
                    hover_foreground = mapping["foreground"][0][1]
                    self.assertEqual(hover_background, theme.colors["action.accent"])
                    self.assertEqual(hover_foreground,
                                     theme.colors["action.accent_text"])
                    self.assertGreaterEqual(
                        contrast_ratio(hover_foreground, hover_background), 4.5
                    )

    def test_mode_mapping_is_explicit_and_complete(self):
        self.assertEqual(set(MODE_LABELS), {"light", "night", "automatic"})
        self.assertEqual(len(set(MODE_LABELS.values())), 3)


if __name__ == "__main__":
    unittest.main()
