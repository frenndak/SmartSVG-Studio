"""Read-only integrity tests for the planned V3.4 roadmap.

This checks documentation consistency, NOT product implementation or hardware.
The historical V3.3 normative requirements remain binding after promotion.
"""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
V34 = ROOT / "docs" / "roadmap-v3.4"
PREFIXES = (("S", 101), ("R33", 40))


def expected_requirements():
    return {
        f"{prefix}-{number:03d}"
        for prefix, count in PREFIXES
        for number in range(1, count + 1)
    }


def markdown_rows(text):
    return [
        [cell.strip() for cell in line.split("|")[1:-1]]
        for line in text.splitlines()
        if line.startswith("|")
    ]


class RoadmapV34IntegrityTests(unittest.TestCase):
    def test_index_and_local_readme_links(self):
        readme = (V34 / "README.md").read_text(encoding="utf-8")
        self.assertIn("24/24 lots documentés", readme)
        self.assertIn("AGENTS.md", readme)
        self.assertIn("437 tests", readme)
        for link in re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", readme):
            target = link.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (V34 / target).resolve()
            self.assertTrue(resolved.is_relative_to(ROOT), target)
            self.assertTrue(resolved.is_file(), f"Broken README link: {target}")

    def test_141_historical_requirements_are_preserved_in_index(self):
        heritage = (V34 / "HERITAGE_INDEX.md").read_text(encoding="utf-8")
        actual = re.findall(r"^\|\s*((?:S|R33)-\d{3})\s*\|", heritage, re.M)
        self.assertEqual(len(actual), 141)
        self.assertEqual(set(actual), expected_requirements())
        self.assertEqual(len(set(actual)), len(actual))

    def test_140_tickets_and_bidirectional_requirement_links(self):
        trace = (V34 / "23_TRACEABILITE_BACKLOG.md").read_text(encoding="utf-8")
        direct = trace.split("## 2. Exigence", 1)[1].split("## 3. Ticket", 1)[0]
        inverse = trace.split("## 3. Ticket", 1)[1].split("## 4.", 1)[0]
        direct_rows = [
            row for row in markdown_rows(direct)
            if re.fullmatch(r"(?:S|R33)-\d{3}", row[0])
        ]
        inverse_rows = [
            row for row in markdown_rows(inverse)
            if re.fullmatch(r"V34-\d{3}", row[0])
        ]
        requirements = [row[0] for row in direct_rows]
        tickets = [row[0] for row in inverse_rows]
        expected_tickets = {f"V34-{n:03d}" for n in range(1, 141)}
        self.assertEqual(len(requirements), 141)
        self.assertEqual(set(requirements), expected_requirements())
        self.assertEqual(len(tickets), 140)
        self.assertEqual(set(tickets), expected_tickets)
        direct_edges = {
            (row[0], ticket)
            for row in direct_rows
            for ticket in re.findall(r"V34-\d{3}", row[2])
        }
        inverse_edges = {
            (requirement, row[0])
            for row in inverse_rows
            for requirement in re.findall(r"(?:S|R33)-\d{3}", row[2])
        }
        self.assertTrue(direct_edges)
        self.assertEqual(direct_edges, inverse_edges)
        self.assertEqual(
            {row[0] for row in direct_rows if "V3.3 G6/G9" in row[2]},
            {"S-021", "S-036", "S-037", "S-044", "S-047",
             "S-064", "S-066", "S-092", "S-099", "R33-028"},
        )

    def test_planned_tests_are_not_claimed_to_be_executed(self):
        summary = (V34 / "24_CONTRE_EXPERTISE_PASSATION.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("437", summary)
        self.assertIn("403", summary)
        self.assertIn("NON_EXECUTE", summary)
        self.assertIn("Windows", summary)
        self.assertIn("Design Space", summary)


if __name__ == "__main__":
    unittest.main()
