"""Negative UI tests for bounded, read-only archived-mask diagnostics (V34-132)."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel
from smartsvg_core.source_preview_v34 import SourcePreview


class Variable:
    def __init__(self, value=''):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class AtelierFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.loaded_images = []
        self.decoded = []
        self.panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        self.panel.snapshot = SimpleNamespace(project_id='synthetic', sha256='a' * 64)
        self.panel.selection = Variable('subject-synthetic')
        self.panel.details = Variable()
        self.panel.viewport = SimpleNamespace(
            load=lambda image: self.loaded_images.append(image))
        self.panel.parent = SimpleNamespace(winfo_ismapped=lambda: True)
        self.panel.tk = SimpleNamespace(PhotoImage=lambda **kwargs: self.decoded.append(kwargs))

    def load_status(self, status, proof='png_only'):
        subject = SimpleNamespace(
            subject_id='subject-synthetic',
            source_id='source-synthetic',
            mask_id='mask-synthetic',
            bbox_px=(0, 1, 2, 3),
            proof_status=proof,
            preview=SourcePreview(status),
        )
        self.panel.subjects = {subject.subject_id: subject}
        self.panel.render()
        return self.panel.details.get()

    def test_every_rejected_preview_has_distinct_safe_guidance_and_never_decodes(self):
        cases = {
            'SOURCE_MISSING': 'Ressource du masque absente',
            'SOURCE_INVALID_PNG': 'PNG du masque invalide',
            'SOURCE_CHANGED': 'empreinte attendues',
            'SOURCE_TOO_LARGE': 'Masque trop volumineux',
        }
        for status, expected in cases.items():
            with self.subTest(status=status):
                message = self.load_status(status)
                self.assertIn(expected, message)
                self.assertIn('Masque mask-synthetic', message)
                self.assertNotIn('C:\\', message)
                self.assertNotIn('/home/', message)
                self.assertIsNone(self.loaded_images[-1])
        self.assertEqual(self.decoded, [])

    def test_future_unknown_preview_or_proof_status_fails_closed_without_crashing(self):
        message = self.load_status('FUTURE_STATUS', 'future-proof-status')
        self.assertIn('Liaison de masque non vérifiée', message)
        self.assertIn('Aperçu indisponible pour ce masque', message)
        self.assertIn('F5', message)
        self.assertIsNone(self.loaded_images[-1])
        self.assertEqual(self.decoded, [])


if __name__ == '__main__':
    unittest.main()
