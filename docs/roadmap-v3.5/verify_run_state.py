"""Check the sealed pre-adoption documentary cursor; current authority is AGENTS/main."""
import argparse
import json
from pathlib import Path
import re

DOC = Path(__file__).resolve().parent
# Changing the closure graph is a reviewed contract change, not a status edit.
REQUIRED_DEPENDENCIES = {
    'REVIEW_DELTA': set(),
    'REVIEW_DE': {'REVIEW_DELTA'},
    'SOURCE_CLOSURE': {'REVIEW_DE'},
    'OPPORTUNITIES_CLOSURE': set(),
    'GLOBAL_REVIEW': {'REVIEW_DELTA', 'REVIEW_DE', 'SOURCE_CLOSURE', 'OPPORTUNITIES_CLOSURE'},
    'PROMOTION_DOCS': {'GLOBAL_REVIEW'},
    'GOVERNANCE_HANDOFF': {'PROMOTION_DOCS'},
}
REQUIRED_SOURCE_WORK = {'Q01', 'Q02', 'Q03'} | {'Q04' + c for c in 'ABCDEFGHIJ'}


def validate(state, doc=DOC):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    def local_file(name):
        if not isinstance(name, str) or not name or Path(name).is_absolute():
            return False
        path = (doc / name).resolve()
        return path.is_relative_to(doc.resolve()) and path.is_file()

    check(state['schema'] == 'smartsvg-roadmap-run-state/1', 'Wrong schema')
    check(state['canonical_branch'] == 'roadmap/v3-5-design-candidate-20261112', 'Wrong branch')
    for key in ('main_observed_sha', 'candidate_base_sha'):
        check(isinstance(state[key], str) and re.fullmatch(r'[0-9a-f]{40}', state[key]), 'Invalid source SHA: ' + key)
    actions = state['actions']
    ids = [a['id'] for a in actions]
    check(len(ids) == len(set(ids)) and bool(ids), 'Duplicate or empty action list')
    check(set(ids) == set(REQUIRED_DEPENDENCIES), 'Missing or unknown closure action')
    by_id = {a['id']: a for a in actions}
    for action in actions:
        check(action['status'] in ('PENDING', 'READY', 'BLOCKED', 'DONE'), 'Invalid action status')
        check(bool(action['scope']) and bool(action['done_when']), 'Missing action contract')
        check(bool(action['inputs']) and all(local_file(p) for p in action['inputs']), 'Missing input: ' + action['id'])
        check(len(action['depends_on']) == len(set(action['depends_on'])), 'Duplicate dependencies')
        check(set(action['depends_on']) == REQUIRED_DEPENDENCIES.get(action['id']), 'Changed closure dependencies: ' + action['id'])
        check(all(d in by_id and d != action['id'] for d in action['depends_on']), 'Unknown/self dependency')
        check(isinstance(action['evidence'], list) and all(local_file(p) for p in action['evidence']), 'Invalid evidence')
        if action['status'] == 'DONE':
            check(bool(action['evidence']), 'DONE without evidence: ' + action['id'])
        if action['status'] in ('READY', 'DONE'):
            check(all(by_id.get(d, {}).get('status') == 'DONE' for d in action['depends_on']), 'Unfinished prerequisite: ' + action['id'])
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            errors.append('Dependency cycle: ' + key)
            return
        if key in visited or key not in by_id:
            return
        visiting.add(key)
        for dep in by_id[key]['depends_on']:
            visit(dep)
        visiting.remove(key)
        visited.add(key)
    for key in ids:
        visit(key)
    current = by_id.get(state['next_action'])
    check(current is not None and current['status'] == 'READY', 'Cursor is not an actionable READY item')
    source_work = state['completed_source_work']
    check(len({x['id'] for x in source_work}) == len(source_work), 'Duplicate source work')
    check({x['id'] for x in source_work} == REQUIRED_SOURCE_WORK, 'Missing or unknown completed source work')
    check(all(x['status'] in ('DOCUMENTED', 'SUPERSEDED_DESIGN', 'REFINED_DESIGN') and local_file(x['evidence']) for x in source_work), 'Missing source work evidence')
    check(state['next_action'] not in {x['id'] for x in source_work}, 'Cursor repeats completed source work')
    # Review completion is distinct from the separate governance adoption.
    check(state['active_roadmap'] == '3.4', 'Unreviewed authority transition')
    check(state['candidate_status'] in ('DESIGN_REVIEW_PENDING', 'DESIGN_REVIEWED_PENDING_INTEGRATION'), 'Invalid candidate review status')
    if state['candidate_status'] == 'DESIGN_REVIEWED_PENDING_INTEGRATION':
        check(by_id.get('GLOBAL_REVIEW', {}).get('status') == 'DONE', 'Reviewed candidate without completed global review')
    check(state['promotion_ready'] is False, 'Unsupported promotion claim')
    check(state['product_tests_added_in_this_campaign'] == 'NOT_RUN', 'Unsupported product-test claim')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, default=DOC / 'RUN_STATE.json')
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.state.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print('FAIL documentary state:', exc)
        return 1
    if errors:
        print('\n'.join(errors))
        return 1
    print('PASS documentary candidate snapshot/dependencies/evidence (V3.4 at capture). Current authority: AGENTS/main; product verdicts are separate.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
