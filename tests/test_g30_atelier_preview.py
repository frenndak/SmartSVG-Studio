"""G3.0 no-dependency checks for shipped offline interactive atelier.

This gate checks syntax, same-origin preview linkage and honest demo-only
claims; a Playwright/real-ComfyUI human inspection is still required.
"""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'engine/web/js/smartsvg_express_atelier_preview.html'
EXPRESS=ROOT/'engine/web/js/smartsvg_express_start_g15.js'

class AtelierPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=HTML.read_text(encoding='utf-8')
        cls.js=EXPRESS.read_text(encoding='utf-8')

    def test_browser_script_is_syntactically_valid(self):
        scripts=re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',
                           self.html,flags=re.IGNORECASE)
        self.assertEqual(len(scripts),1)
        node=shutil.which('node')
        if node is None:
            self.skipTest('Node.js is not installed')
        result=subprocess.run([node,'--check','-'],input=scripts[0],
                              text=True,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_five_navigation_steps_and_interactive_controls_exist(self):
        for step in ('source','clean','subjects','cut','export'):
            self.assertIn('data-step="'+step+'"',self.html)
        for required in ('id="sheet"','id="file"','id="dropZone"',
                         'id="zoomIn"','id="zoomOut"','id="zoomFit"',
                         'id="all"','id="none"','id="alternate"',
                         'id="width"','id="dpi"','id="next"'):
            self.assertIn(required,self.html)
        self.assertIn('SAMPLE_COUNT=12',self.html)
        self.assertIn('image/png,image/jpeg,image/webp',self.html)
        self.assertIn('role="status"',self.html)
        self.assertIn('@media(max-width:580px)',self.html)

    def test_preview_never_claims_real_cut_or_queues_comfyui(self):
        self.assertIn('APERÇU NON CERTIFIÉ',self.html)
        self.assertIn("aucun traitement IA ni découpe réelle",self.html)
        self.assertNotIn('queuePrompt',self.html)
        self.assertNotIn('fetch(',self.html)
        self.assertNotIn('XMLHttpRequest',self.html)
        self.assertNotIn('<script src=',self.html)
        self.assertNotIn('localStorage',self.html)
        self.assertNotIn('https://',self.html)
        self.assertIn("URL.revokeObjectURL",self.html)

    def test_comfyui_express_link_is_opt_in_and_not_auto_queued(self):
        self.assertIn("new URL('./smartsvg_express_atelier_preview.html',import.meta.url)",self.js)
        self.assertIn("window?.open?.(url.href,'_blank','noopener,noreferrer')",self.js)
        self.assertNotIn('app.queuePrompt',self.js)
        self.assertNotIn('innerHTML',self.js)

if __name__=='__main__':
    unittest.main()
