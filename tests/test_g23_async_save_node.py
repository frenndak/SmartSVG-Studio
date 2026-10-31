"""G2.3: run actual Node event handlers for stale async editor saves in G0."""
from pathlib import Path
import shutil
import subprocess
import unittest


class EditorAsyncSaveNodeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js runtime unavailable")
    def test_stale_editor_save_races(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [shutil.which("node"), "--test",
             str(root / "engine/tests/test_g23_async_save_race.mjs")],
            cwd=root, capture_output=True, text=True, timeout=25,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0,
            "Node editor save race tests failed:\n" + result.stdout + "\n" +
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
