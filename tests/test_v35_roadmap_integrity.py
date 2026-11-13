"""Planning invariants, including deliberate corruptions; no product claims."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_roadmap_v35 import validate


class RoadmapV35IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / 'docs/roadmap-v3.5/backlog.json').read_text(encoding='utf-8'))

    def test_canonical_coverage_and_document_links(self):
        self.assertEqual(validate(self.plan, ROOT), [])

    def test_rejects_missing_duplicate_and_unknown_ids(self):
        for kind in ('requirements', 'tickets', 'slices'):
            for change in ('missing', 'duplicate', 'unknown'):
                with self.subTest(kind=kind, change=change):
                    plan = deepcopy(self.plan)
                    if change == 'missing':
                        plan[kind].pop()
                    elif change == 'duplicate':
                        plan[kind].append(deepcopy(plan[kind][0]))
                    else:
                        plan[kind][0]['id'] = 'UNKNOWN'
                    self.assertTrue(validate(plan, ROOT))

    def test_rejects_lost_edges_in_both_directions(self):
        for kind, field in (('requirements', 'v34_tickets'), ('tickets', 'requirement_ids')):
            with self.subTest(kind=kind):
                plan = deepcopy(self.plan)
                plan[kind][0][field].pop()
                self.assertTrue(validate(plan, ROOT))

    def test_rejects_dependency_cycle_and_unknown_dependency(self):
        for dependency in ('V35-01', 'V35-99'):
            with self.subTest(dependency=dependency):
                plan = deepcopy(self.plan)
                plan['slices'][0]['depends_on'] = [dependency]
                self.assertTrue(validate(plan, ROOT))

    def test_rejects_false_delivery_claim_or_authority_promotion(self):
        for kind in ('requirements', 'tickets', 'slices'):
            plan = deepcopy(self.plan)
            plan[kind][0]['delivery_status'] = 'PASS'
            self.assertTrue(validate(plan, ROOT))
        plan = deepcopy(self.plan)
        plan['active_roadmap'] = '3.5'
        self.assertTrue(validate(plan, ROOT))

    def test_rejects_lost_heritage_route_and_acceptance_criterion(self):
        plan = deepcopy(self.plan)
        next(r for r in plan['requirements'] if r['id'] == 'R33-028')['execution_slices'] = []
        self.assertTrue(validate(plan, ROOT))
        plan = deepcopy(self.plan)
        plan['slices'][0]['criteria'].pop()
        self.assertTrue(validate(plan, ROOT))

    def test_rejects_wrong_source_and_duplicate_slice_assignment(self):
        plan = deepcopy(self.plan)
        plan['tickets'][0]['source_path'] = '../outside-root.md'
        self.assertTrue(validate(plan, ROOT))
        plan = deepcopy(self.plan)
        plan['slices'][1]['v34_tickets'].append(plan['tickets'][0]['id'])
        self.assertTrue(validate(plan, ROOT))


if __name__ == '__main__':
    unittest.main()
