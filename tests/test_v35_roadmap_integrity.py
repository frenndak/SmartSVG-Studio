"""Read-only checks of V3.5 design artifacts, never product qualification."""
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "roadmap-v3.5"


class RoadmapV35IntegrityTests(unittest.TestCase):
    def run_checker(self, name, *args):
        result = subprocess.run(
            [sys.executable, str(DOC / name), *args], cwd=ROOT,
            text=True, capture_output=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_complete_historical_criteria_and_dod_transfer(self):
        self.run_checker("verify_source_transfer.py", "--main-root", str(ROOT))

    def test_pinned_inventory_sources_and_ports(self):
        self.run_checker("verify_priority_register.py", "--pinned", "--main-root", str(ROOT))

    def test_documentary_cursor_dependencies_and_evidence(self):
        self.run_checker("verify_run_state.py")

    def test_local_markdown_destinations_stay_in_repository_and_exist(self):
        count = 0
        for page in DOC.glob("*.md"):
            for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
                target = raw.strip().strip("<>")
                if not target or target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                resolved = (page.parent / unquote(target.split("#", 1)[0])).resolve()
                with self.subTest(page=page.name, target=target):
                    self.assertTrue(resolved.is_relative_to(ROOT), "Link escapes repository")
                    self.assertTrue(resolved.is_file(), "Missing local file")
                count += 1
        self.assertGreater(count, 0)


if __name__ == "__main__":
    unittest.main()
