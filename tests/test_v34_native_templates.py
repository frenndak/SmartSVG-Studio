"""Native card/tray callbacks using real geometry and headless widget doubles.

No actual Windows/Tk rendering, DPI, screen-reader or Cricut qualification.
"""
import importlib
import math
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))


class Var:
    def __init__(self, value=''):
        self.value = value
        self.callbacks = []
    def get(self): return self.value
    def set(self, value):
        self.value = value
        for callback in self.callbacks: callback('', '', '')
    def trace_add(self, _mode, callback):
        self.callbacks.append(callback)
        return str(id(callback))
    def trace_remove(self, _mode, handle):
        self.callbacks = [callback for callback in self.callbacks if str(id(callback)) != handle]


class Widget:
    def __init__(self, *_args, **kwargs):
        self.options = kwargs
        self.events = {}
        self.exists = True
        self.lines = []
        self.width, self.height = 720, 320
        self.lifts = 0
    def pack(self, **_kwargs): pass
    def grid(self, **_kwargs): pass
    def columnconfigure(self, *_args, **_kwargs): pass
    def configure(self, **kwargs): self.options.update(kwargs)
    def bind(self, event, callback): self.events[event] = callback
    def title(self, _text): pass
    def geometry(self, _size): pass
    def minsize(self, *_args): pass
    def transient(self, _root): pass
    def winfo_width(self): return self.width
    def winfo_height(self): return self.height
    def winfo_exists(self): return self.exists
    def grab_set(self): pass
    def grab_release(self): pass
    def lift(self): self.lifts += 1
    def destroy(self): self.exists = False
    def delete(self, _what): self.lines.clear()
    def create_line(self, *points, **kwargs): self.lines.append((points, kwargs))


class NativeTemplatePreviewTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ENGINE / 'native_templates_tk_v34.py').is_file(),
                        'The native template tool has not been implemented')
        self.module = importlib.import_module('native_templates_tk_v34')
        self.tk = SimpleNamespace(Toplevel=Widget, Canvas=Widget, StringVar=Var)
        self.ttk = SimpleNamespace(Frame=Widget, Label=Widget, Entry=Widget,
                                   Combobox=Widget, Button=Widget)
        self.root = Widget()
        self.panel = self.module.NativeTemplatePreview(self.root, self.tk, self.ttk)

    def test_default_tray_uses_real_dimensions_and_distinct_cut_score_lines(self):
        self.panel.calculate()
        proposal = self.panel.proposal
        self.assertEqual(proposal['template_id'], 'open-tray-glue-tabs')
        self.assertEqual(proposal['geometry']['bbox_mm'], [0, 0, 140, 110])
        self.assertEqual(len(self.panel.canvas.lines), 13)
        cut = [style for _, style in self.panel.canvas.lines if not style.get('dash')]
        score = [style for _, style in self.panel.canvas.lines if style.get('dash')]
        self.assertEqual((len(cut), len(score)), (5, 8))
        self.assertNotEqual(cut[0]['fill'], score[0]['fill'])
        self.assertIn('140', self.panel.status.get())
        self.assertIn('110', self.panel.status.get())
        self.assertFalse(proposal['persisted'])
        self.assertEqual(proposal['handoff']['machine_material_qualification'], 'UNKNOWN')

    def test_card_ignores_disabled_tray_fields_and_shows_one_fold(self):
        self.panel.kind.set('Carte pliée')
        self.panel.width.set('105')
        self.panel.depth.set('148')
        self.panel.wall.set('invalid unused value')
        self.panel.tab.set('also unused')
        self.panel.calculate()
        self.assertEqual(self.panel.proposal['geometry']['bbox_mm'], [0, 0, 210, 148])
        self.assertEqual(len(self.panel.canvas.lines), 2)
        self.assertEqual(self.panel.wall_entry.options['state'], 'disabled')
        self.assertEqual(self.panel.tab_entry.options['state'], 'disabled')

    def test_parameter_edit_immediately_discards_stale_drawing(self):
        self.panel.calculate()
        self.panel.width.set('90')
        self.assertIsNone(self.panel.proposal)
        self.assertEqual(self.panel.canvas.lines, [])
        self.panel.calculate()
        self.assertEqual(self.panel.proposal['geometry']['bbox_mm'], [0, 0, 150, 110])

    def test_invalid_values_clear_geometry_and_allow_correction(self):
        for value in ('0', '-1', 'nan', 'inf', 'not a number', '1e309', ''):
            with self.subTest(value=value):
                self.panel.width.set(value)
                self.panel.calculate()
                self.assertIsNone(self.panel.proposal)
                self.assertEqual(self.panel.canvas.lines, [])
                self.assertIn('Vérifier', self.panel.status.get())
        self.panel.width.set('80')
        self.panel.tab.set('30')
        self.panel.calculate()
        self.assertIsNone(self.panel.proposal)
        self.panel.tab.set('10')
        self.panel.calculate()
        self.assertEqual(len(self.panel.canvas.lines), 13)

    def test_decimal_comma_and_template_switch_refresh_controls(self):
        self.panel.width.set('80,5')
        self.panel.calculate()
        self.assertEqual(self.panel.proposal['geometry']['bbox_mm'], [0, 0, 140.5, 110])
        self.panel.kind.set('Carte pliée')
        self.assertIsNone(self.panel.proposal)
        self.panel.kind.set('Boîte ouverte')
        self.assertEqual(self.panel.wall_entry.options['state'], 'normal')
        self.assertEqual(self.panel.tab_entry.options['state'], 'normal')

    def test_resize_keeps_geometry_aspect_ratio_and_semantic_styles(self):
        self.panel.calculate()
        original = self.panel.proposal
        for width, height in ((720, 320), (400, 280), (1200, 500)):
            self.panel.canvas.width, self.panel.canvas.height = width, height
            self.panel.canvas.events['<Configure>'](None)
            points = [point for line, _ in self.panel.canvas.lines for point in zip(line[::2], line[1::2])]
            xs, ys = zip(*points)
            self.assertTrue(all(math.isfinite(value) for point in points for value in point))
            self.assertGreaterEqual(min(xs), 23.99)
            self.assertLessEqual(max(xs), width - 23.99)
            self.assertGreaterEqual(min(ys), 23.99)
            self.assertLessEqual(max(ys), height - 23.99)
            self.assertAlmostEqual((max(xs)-min(xs))/(max(ys)-min(ys)), 140/110)
            self.assertIs(self.panel.proposal, original)
            self.assertEqual(sum(bool(style.get('dash')) for _, style in self.panel.canvas.lines), 8)

    def test_entry_point_reuses_live_window_and_recreates_closed_one(self):
        panel = self.module.open_template_preview(None, self.root, self.tk, self.ttk)
        same = self.module.open_template_preview(panel, self.root, self.tk, self.ttk)
        self.assertIs(same, panel)
        self.assertEqual(panel.window.lifts, 1)
        panel.window.destroy()
        fresh = self.module.open_template_preview(panel, self.root, self.tk, self.ttk)
        self.assertIsNot(fresh, panel)

    def test_embedded_content_uses_existing_parent_without_a_popup(self):
        tk = SimpleNamespace(Canvas=Widget, StringVar=Var)
        panel = self.module.TemplatePreviewContent(self.root, tk, self.ttk)
        self.assertFalse(hasattr(panel, 'window'))
        self.assertEqual(len(panel.canvas.lines), 13)
        self.assertEqual(panel.proposal['geometry']['bbox_mm'], [0, 0, 140, 110])

    def test_preview_never_writes_project_or_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'preserve.smartsvg'
            file.write_bytes(b'unchanged fixture')
            before = {p.name: p.read_bytes() for p in Path(directory).iterdir()}
            with patch.object(Path, 'write_bytes', side_effect=AssertionError('unexpected write')), \
                 patch.object(Path, 'write_text', side_effect=AssertionError('unexpected write')):
                self.panel.calculate()
                self.panel.kind.set('Carte pliée')
                self.panel.calculate()
                self.panel.window.destroy()
            self.assertEqual({p.name: p.read_bytes() for p in Path(directory).iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
