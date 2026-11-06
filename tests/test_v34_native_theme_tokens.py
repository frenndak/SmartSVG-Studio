"""V34-045/046, UX-13/UX-18 — framework-neutral artisan theme contracts."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_theme_v34 import (
    ACCENTS, ThemePreferences, ThemePreferenceError,
    contrast_ratio, load_theme_preferences, resolve_theme, save_theme_preferences,
)


class ArtisanThemeTests(unittest.TestCase):
    def test_six_accessible_accents_in_both_modes(self):
        self.assertEqual(len(ACCENTS), 6)
        for accent in ACCENTS:
            for appearance in ("light", "night"):
                with self.subTest(accent=accent, appearance=appearance):
                    theme = resolve_theme(ThemePreferences(
                        accent=accent, appearance=appearance))
                    self.assertEqual(theme.appearance, appearance)
                    self.assertGreaterEqual(contrast_ratio(
                        theme.colors["action.accent_text"],
                        theme.colors["action.accent"]), 4.5)
                    self.assertGreaterEqual(contrast_ratio(
                        theme.colors["text.primary"],
                        theme.colors["surface.panel"]), 4.5)
                    self.assertGreaterEqual(contrast_ratio(
                        theme.colors["text.secondary"],
                        theme.colors["surface.panel"]), 4.5)
                    self.assertGreaterEqual(contrast_ratio(
                        theme.colors["focus.ring"],
                        theme.colors["surface.panel"]), 3.0)

    def test_default_sage_and_automatic_mode_without_os_call(self):
        preferences = ThemePreferences()
        self.assertEqual(preferences.accent, "sage")
        self.assertEqual(preferences.appearance, "automatic")
        self.assertEqual(resolve_theme(preferences).appearance, "light")
        self.assertEqual(resolve_theme(preferences, system_dark=True).appearance, "night")
        self.assertEqual(resolve_theme(preferences, system_dark=False).appearance, "light")
        self.assertEqual(resolve_theme(ThemePreferences(appearance="night"),
                                       system_dark=False).appearance, "night")

    def test_canvas_colors_and_operation_states_do_not_follow_accent(self):
        themes = [resolve_theme(ThemePreferences(accent=a, appearance=mode))
                  for a in ACCENTS for mode in ("light", "night")]
        for key in ("canvas.white", "canvas.neutral",
                    "canvas.checker.light", "canvas.checker.dark"):
            self.assertEqual(len({theme.colors[key] for theme in themes}), 1)
        self.assertEqual(themes[0].colors["canvas.white"], "#FFFFFF")
        for mode in ("light", "night"):
            self.assertEqual(len({theme.colors["status.error"]
                                  for theme in themes if theme.appearance == mode}), 1)
        with self.assertRaises(TypeError):
            themes[0].colors["canvas.white"] = "#000000"

    def test_all_settings_persist_locally_across_restart(self):
        with TemporaryDirectory() as tmp:
            location = Path(tmp) / "appearance.json"
            for accent in ACCENTS:
                for appearance in ("light", "night", "automatic"):
                    preferences = ThemePreferences(
                        appearance=appearance, accent=accent, reduced_motion=True)
                    save_theme_preferences(location, preferences)
                    reloaded = load_theme_preferences(location)
                    self.assertEqual(reloaded, preferences)
                    self.assertTrue(reloaded.reduced_motion)
                    self.assertEqual(set(json.loads(location.read_text())),
                                     {"appearance", "accent", "reduced_motion"})

    def test_missing_or_corrupt_settings_safely_fall_back(self):
        with TemporaryDirectory() as tmp:
            location = Path(tmp) / "appearance.json"
            self.assertEqual(load_theme_preferences(location), ThemePreferences())
            for invalid in (
                b"invalid json",
                b'{"appearance":"night","accent":"sage","reduced_motion":null}',
                b'{"appearance":"night","accent":"unknown","reduced_motion":false}',
                b'{"appearance":"night","accent":"sage","reduced_motion":false,"extra":1}',
                b'{"appearance":"night","appearance":"light","accent":"sage","reduced_motion":false}',
                b"x" * 2100,
            ):
                location.write_bytes(invalid)
                with self.subTest(value=invalid[:30]):
                    self.assertEqual(load_theme_preferences(location), ThemePreferences())

    def test_invalid_preference_types_fail_closed(self):
        for data in (
            {"accent": "invalid"},
            {"accent": 123},
            {"appearance": "sepia"},
            {"appearance": None},
            {"reduced_motion": 0},
        ):
            with self.subTest(data=data), self.assertRaises(ThemePreferenceError):
                ThemePreferences(**data)
        with self.assertRaises(ThemePreferenceError):
            resolve_theme(ThemePreferences(), system_dark="yes")

    def test_preferences_never_modify_a_project(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp) / "atelier.smartsvg"
            project.write_bytes(b"unchanged project bytes")
            before = project.read_bytes()
            settings = Path(tmp) / "appearance.json"
            save_theme_preferences(settings, ThemePreferences(
                appearance="night", accent="lavender"))
            self.assertEqual(project.read_bytes(), before)
            self.assertNotIn("atelier.smartsvg", settings.read_text())
            self.assertNotIn("unchanged project bytes", settings.read_text())
            self.assertEqual(load_theme_preferences(settings).appearance, "night")

    def test_reject_symlink_and_project_path_writes(self):
        with TemporaryDirectory() as tmp:
            other = Path(tmp) / "other.json"
            other.write_bytes(b"no touch")
            link = Path(tmp) / "appearance.json"
            try:
                link.symlink_to(other)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links unavailable")
            with self.assertRaises(ThemePreferenceError):
                save_theme_preferences(link, ThemePreferences(accent="peach"))
            self.assertEqual(other.read_bytes(), b"no touch")
            project = Path(tmp) / "art.smartsvg"
            with self.assertRaises(ThemePreferenceError):
                save_theme_preferences(project, ThemePreferences())
            self.assertFalse(project.exists())

    def test_reduced_motion_is_semantic_and_does_not_change_colors(self):
        a = resolve_theme(ThemePreferences(accent="mist_blue"))
        b = resolve_theme(ThemePreferences(accent="mist_blue", reduced_motion=True))
        self.assertEqual(a.colors, b.colors)
        self.assertFalse(a.reduced_motion)
        self.assertTrue(b.reduced_motion)


if __name__ == "__main__":
    unittest.main()
