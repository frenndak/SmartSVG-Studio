"""G3.3e-b2a: execute the real browser-client Node contract in G0/preflight.

No third-party Python package, browser, model or external network is needed.
If Node is unavailable locally, the explicit skip is not a pass.
"""
from pathlib import Path
import shutil
import subprocess
import unittest


class SubjectBrushPreviewClientNodeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js runtime unavailable")
    def test_browser_preview_contract(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [shutil.which("node"), "--test",
             str(root / "tools" / "test_subject_brush_preview_client_g33e.mjs")],
            cwd=root, capture_output=True, text=True, timeout=25,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0,
            "Node client preview contract failed:\n" + result.stdout + "\n" +
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
