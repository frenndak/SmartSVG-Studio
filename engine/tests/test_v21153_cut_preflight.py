"""Regression cases for V21.15.3 fail-closed Basic Cut path validation."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

from smartsvg_governance.artifact_qa import audit_project


class TestCutPreflight(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        image = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(image).ellipse((10, 10, 70, 70), fill='red')
        image.save(self.root / 'shape.png')
        report = {'objets': [{'png': 'shape.png', 'svg_contour': 'cut.svg',
                             'contour_nombre_chemins': 1,
                             'largeur_finale_avec_marge_mm': 30}]}
        (self.root / 'RAPPORT_V21_2.json').write_text(json.dumps(report), encoding='utf8')

    def audit_svg(self, markup):
        (self.root / 'cut.svg').write_text(markup, encoding='utf8')
        return audit_project(self.root / 'RAPPORT_V21_2.json')

    def svg(self, path, attrs='width="30mm"'):
        return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}><path d="{path}"/></svg>'

    def test_real_closed_polygon_may_enter_human_review(self):
        result = self.audit_svg(self.svg('M0 0 L20 0 L20 20 L0 20 Z'))
        self.assertEqual(result['status'], 'REVIEW_REQUIRED')
        self.assertTrue(result['objects'][0]['svg']['closed_paths_checked'])

    def test_empty_zero_area_and_open_paths_blocked(self):
        for d in ('', 'M0 0Z', 'M0 0 L20 0 Z',
                  'M0 0 L20 0 L20 20', 'M0 0 L20 0 L20 20 Z M1 1 L2 2'):
            with self.subTest(d=d):
                result = self.audit_svg(self.svg(d))
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertIn('FICHIER_NON_VERIFIABLE', result['blocking_codes'])

    def test_active_markup_and_external_references_rejected(self):
        for attrs in ('onload="alert(1)"', 'style="display:block"',
                      'transform="scale(0)"', 'href="https://bad.example/a"'):
            with self.subTest(attrs=attrs):
                result = self.audit_svg(self.svg('M0 0 L20 0 L20 20 Z', 'width="30mm" ' + attrs))
                self.assertEqual(result['status'], 'BLOCKED')
        result = self.audit_svg('<svg width="30mm"><rect x="1" y="1" width="2" height="2"/>'
                                '<path d="M0 0 L20 0 L20 20 Z"/></svg>')
        self.assertEqual(result['status'], 'BLOCKED')

    def test_missing_physical_unit_blocks_claim(self):
        result = self.audit_svg(self.svg('M0 0 L20 0 L20 20 Z', 'width="300px"'))
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('DIMENSIONS_MM_ABSENTES', result['blocking_codes'])

    def test_nonpolygonal_path_stays_manual_review(self):
        result = self.audit_svg(self.svg('M0 0 C10 0 20 15 30 25 L0 30 Z'))
        self.assertEqual(result['status'], 'REVIEW_REQUIRED')
        self.assertTrue(result['objects'][0]['svg']['nonpolygonal_paths_require_visual_review'])


    def test_corrective_message_matches_svg_failure(self):
        from tests.test_v21152 import release
        _action_for_qa = release._action_for_qa
        message = _action_for_qa({'status': 'BLOCKED',
                                  'blocking_codes': ['FICHIER_NON_VERIFIABLE']})
        self.assertIn('régénérer le SVG', message)
        self.assertNotIn('carte rectangulaire', message)
        self.assertIn('Corriger le masque', _action_for_qa({
            'status': 'BLOCKED',
            'blocking_codes': ['SILHOUETTE_RECTANGULAIRE_NON_FIABLE']}))

if __name__ == '__main__':
    unittest.main()
