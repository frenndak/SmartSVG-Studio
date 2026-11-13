"""Validate planning integrity only; never qualify the application or hardware."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha1
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PLAN = Path('docs/roadmap-v3.5/backlog.json')
TRACE = Path('docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md')
ORPHANS = {'S-021', 'S-036', 'S-037', 'S-044', 'S-047', 'S-064',
           'S-066', 'S-092', 'S-099', 'R33-028'}


def table_rows(text):
    return [
        [cell.strip() for cell in line.split('|')[1:-1]]
        for line in text.splitlines() if line.startswith('|')
    ]


def blob_sha(raw):
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def validate(plan, root=ROOT, *, pinned=False):
    """Return every detected planning error; empty means documentation consistent.

    --pinned additionally checks the originally inspected source blobs. Without
    that option, compare the current canonical ID sets and planning edges, so
    unrelated prose updates do not require rewriting this historical proposal.
    """
    root = Path(root).resolve()
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def local_file(path):
        check(isinstance(path, str), 'Non-string source path')
        if not isinstance(path, str):
            return None
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            errors.append('Missing or outside-root file: ' + path)
            return None
        return resolved

    def indexed(key, expected):
        values = plan.get(key, [])
        check(isinstance(values, list), 'Expected list: ' + key)
        if not isinstance(values, list):
            return {}
        ids = [value.get('id') for value in values if isinstance(value, dict)]
        check(len(ids) == len(values), 'Invalid entry: ' + key)
        check(all(isinstance(item, str) for item in ids), 'Invalid ID: ' + key)
        valid_ids = [item for item in ids if isinstance(item, str)]
        check(len(valid_ids) == len(set(valid_ids)), 'Duplicate IDs: ' + key)
        check(set(valid_ids) == expected, 'Canonical ID set mismatch: ' + key)
        return {value['id']: value for value in values
                if isinstance(value, dict) and isinstance(value.get('id'), str)}

    check(plan.get('schema') == 'smartsvg-roadmap-plan/1', 'Unknown schema')
    check(plan.get('status') == 'PROPOSITION', 'Unexpected authority promotion')
    check(plan.get('active_roadmap') == '3.4', 'Active roadmap changed by plan')
    reqs = indexed('requirements', {f'S-{n:03d}' for n in range(1, 102)} |
                   {f'R33-{n:03d}' for n in range(1, 41)})
    tickets = indexed('tickets', {f'V34-{n:03d}' for n in range(1, 141)})
    slices = indexed('slices', {f'V35-{n:02d}' for n in range(1, 16)})
    for item in [*reqs.values(), *tickets.values(), *slices.values()]:
        check(item.get('delivery_status') == 'NON_VERIFIE',
              'Unsubstantiated delivery status: ' + item['id'])

    trace = local_file(str(TRACE))
    if trace is None:
        return errors
    rows = table_rows(trace.read_text(encoding='utf-8'))
    canonical_reqs = {r[0]: r for r in rows if re.fullmatch(r'(S|R33)-\d{3}', r[0])}
    canonical_tickets = {r[0]: r for r in rows if re.fullmatch(r'V34-\d{3}', r[0])}
    direct_edges, inverse_edges = set(), set()
    for rid, req in reqs.items():
        canonical = canonical_reqs.get(rid)
        check(canonical is not None, 'Requirement missing from source: ' + rid)
        assigned = req.get('v34_tickets', [])
        check(len(assigned) == len(set(assigned)), 'Duplicate requirement edge: ' + rid)
        if canonical:
            check(req.get('title') == canonical[1], 'Changed source title: ' + rid)
            check(assigned == re.findall(r'V34-\d{3}', canonical[2]),
                  'Changed canonical requirement edges: ' + rid)
            check(req.get('reference_tests') == canonical[3], 'Changed source tests: ' + rid)
        for tid in assigned:
            check(tid in tickets, 'Unknown ticket edge: ' + str(tid))
            direct_edges.add((rid, tid))
        routes = req.get('execution_slices', [])
        check(bool(routes) and set(routes) <= set(slices), 'Unrouted requirement: ' + rid)
        expected_routes = {tickets[tid]['execution_slice'] for tid in assigned if tid in tickets}
        if not assigned:
            expected_routes = {'V35-12'}
        check(set(routes) == expected_routes, 'Inconsistent requirement routing: ' + rid)
    check({rid for rid, r in reqs.items() if not r.get('v34_tickets')} == ORPHANS,
          'Historical requirements without V34 tickets changed')

    source_index = {s['path']: s['blob_sha'] for s in plan.get('sources', [])}
    for tid, ticket in tickets.items():
        canonical = canonical_tickets.get(tid)
        check(canonical is not None, 'Ticket missing from source: ' + tid)
        linked = ticket.get('requirement_ids', [])
        check(len(linked) == len(set(linked)), 'Duplicate inverse edge: ' + tid)
        if canonical:
            check(linked == re.findall(r'(?:S|R33)-\d{3}', canonical[2]),
                  'Changed canonical ticket edges: ' + tid)
            check(ticket.get('source_lot') == int(re.search(r'\d+', canonical[1])[0]),
                  'Changed ticket source lot: ' + tid)
            check(ticket.get('reference_tests') == canonical[3], 'Changed source tests: ' + tid)
        inverse_edges.update((rid, tid) for rid in linked)
        check(ticket.get('execution_slice') in slices, 'Unassigned ticket: ' + tid)
        path = ticket.get('source_path', '')
        check(ticket.get('source_blob_sha') == source_index.get(path),
              'Unpinned ticket source: ' + tid)
        file = local_file(path)
        if file:
            check(tid in file.read_text(encoding='utf-8'), 'Ticket absent in source: ' + tid)
    check(direct_edges == inverse_edges, 'Asymmetric requirement/ticket edges')

    counts = Counter()
    visiting, visited = set(), set()

    def visit(sid):
        if sid in visiting:
            errors.append('Dependency cycle: ' + sid)
            return
        if sid in visited or sid not in slices:
            return
        visiting.add(sid)
        for dependency in slices[sid].get('depends_on', []):
            check(dependency in slices, 'Unknown dependency: ' + str(dependency))
            visit(dependency)
        visiting.remove(sid)
        visited.add(sid)

    criteria_text = (root / 'docs/roadmap-v3.5/02_EXECUTION.md').read_text(encoding='utf-8')
    for sid, item in slices.items():
        visit(sid)
        assigned = item.get('v34_tickets', [])
        counts.update(assigned)
        check(set(assigned) == {tid for tid, t in tickets.items() if t.get('execution_slice') == sid},
              'Slice ticket index mismatch: ' + sid)
        check(set(item.get('requirement_ids', [])) ==
              {rid for rid, r in reqs.items() if sid in r.get('execution_slices', [])},
              'Slice requirement index mismatch: ' + sid)
        heading = re.search(r'^## ' + re.escape(sid) + r' — [^\n]+\n(.*?)(?=^## |\Z)',
                            criteria_text, re.M | re.S)
        criteria = re.findall(r'^- A(\d+) :', heading[1], re.M) if heading else []
        check(item.get('criteria') == [sid + '-A' + number for number in criteria] and bool(criteria),
              'Missing or changed acceptance criteria: ' + sid)
        check(item.get('criteria_path') == 'docs/roadmap-v3.5/02_EXECUTION.md',
              'Wrong acceptance document: ' + sid)
    check(set(counts) == set(tickets) and all(n == 1 for n in counts.values()),
          'Each V34 ticket must have exactly one primary slice')

    for file in (root / 'docs/roadmap-v3.5').glob('*.md'):
        for link in re.findall(r'(?<!!)\[[^]]+\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
            target = link.split('#', 1)[0]
            if target and '://' not in target:
                local_file(str((file.parent / target).relative_to(root)))

    if pinned:
        baseline = plan.get('baseline', {})
        check(baseline.get('trace_path') == str(TRACE), 'Wrong baseline trace path')
        check(blob_sha(trace.read_bytes()) == baseline.get('trace_blob_sha'),
              'Baseline trace blob changed')
        for source in plan.get('sources', []):
            file = local_file(source.get('path'))
            if file:
                check(blob_sha(file.read_bytes()) == source.get('blob_sha'),
                      'Source blob changed: ' + source['path'])
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pinned', action='store_true', help='Also verify original source blob hashes')
    args = parser.parse_args(argv)
    try:
        errors = validate(json.loads((ROOT / PLAN).read_text(encoding='utf-8')), pinned=args.pinned)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Documentation validation failed: ' + str(exc))
        return 1
    if errors:
        print('\n'.join(errors))
        return 1
    print('PASS documentaire : 141 exigences, 140 tickets, 15 tranches ; aucune qualification produit.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
