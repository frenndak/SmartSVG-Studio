"""G2.9 path grammar regression suite, executed by the existing G0 admission CI."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class CutPathGrammarG29(unittest.TestCase):
    def test_native_svg_command_grammar(self):
        node=shutil.which('node')
        if node is None:self.skipTest('Node.js not installed')
        p=subprocess.run(
            [node,'--test',str(ROOT/'engine/tests/test_g29_path_grammar.mjs')],
            cwd=ROOT,text=True,capture_output=True,timeout=35
        )
        self.assertEqual(p.returncode,0,p.stdout[-10000:]+p.stderr[-4000:])

    def test_sanitize_before_svg_export_and_no_automatic_cut(self):
        source=(ROOT/'engine/web/js/smartsvg_cut_review_model_g27.mjs').read_text()
        syntax=(ROOT/'engine/web/js/smartsvg_svg_path_grammar_g29.mjs').read_text()
        self.assertIn("inspectSvgPathGrammar(value)",source)
        self.assertIn("PATH_OUTSIDE_VIEWBOX",source)
        self.assertNotIn('queuePrompt',source+syntax)
        self.assertNotIn('innerHTML',source+syntax)

if __name__=='__main__':unittest.main()
