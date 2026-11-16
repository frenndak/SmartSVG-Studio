"""Verify literal source transfer and lookup integrity, never semantic/product PASS."""
import argparse
from git_blob_provenance import file_blob
import json
from pathlib import Path
import re

DOC = Path(__file__).resolve().parent
REQ = {f'S-{i:03d}' for i in range(1, 102)} | {f'R33-{i:03d}' for i in range(1, 41)}
TICKETS = {f'V34-{i:03d}' for i in range(1, 141)}
GAPS = {'S-021', 'S-036', 'S-037', 'S-044', 'S-047', 'S-064', 'S-066', 'S-092', 'S-099', 'R33-028'}
PRESERVATION = 'All full normative parent sections, common DoDs, dependencies, tests, proof axes and rollback remain binding. Stored rows and clarifications are lookup aids, never reduced acceptance definitions.'


def validate(data, main_root, doc=DOC):
    errors = []
    root = Path(main_root).resolve()

    def check(ok, message):
        if not ok:
            errors.append(message)

    def source_path(name):
        if not isinstance(name, str) or not name or Path(name).is_absolute():
            raise ValueError('Invalid source path')
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Source outside root')
        return path

    check(data['schema'] == 'smartsvg-source-transfer/1', 'Wrong schema')
    check(data['documentary_status'] in ('REVIEW_PENDING', 'REVIEWED'), 'Invalid documentary status')
    check(data['preservation_rule'] == PRESERVATION and bool(data['historical_link_semantics']), 'Changed preservation rule or missing link qualifier')
    for key in ('candidate_base_sha', 'main_observed_sha'):
        check(bool(re.fullmatch(r'[0-9a-f]{40}', data[key])), 'Invalid commit SHA')

    expected_sources = {
        'docs/ROADMAP_MASTER_v3_3.md', 'docs/ROADMAP_HERITAGE_v3_3.md',
        'docs/ROADMAP_TRACEABILITY_v3_3.md', 'docs/ROADMAP_COVERAGE_v3_3.md',
        'docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md',
    }
    lot_files = {}
    for path in (root / 'docs/roadmap-v3.4').glob('[0-2][0-9]_*.md'):
        lot = int(path.name[:2])
        if 1 <= lot <= 21:
            if not re.search(r'^\|\s*(?:\*\*)?V34-\d{3}\b', path.read_text(encoding='utf-8'), re.M):
                continue
            check(lot not in lot_files, 'Duplicate source lot')
            lot_files[lot] = path.relative_to(root).as_posix()
    check(set(lot_files) == set(range(1, 22)), 'Missing local source lots')
    expected_sources.update(lot_files.values())
    pins = data['source_blobs']
    check(len(pins) == len({p['path'] for p in pins}), 'Duplicate source pin')
    check({p['path'] for p in pins} == expected_sources, 'Missing/unknown source pin')
    pinned = {p['path']: p['blob_sha'] for p in pins}
    cache = {}
    for name, expected in pinned.items():
        raw = source_path(name).read_bytes()
        actual = file_blob(source_path(name))
        check(actual == expected, 'Source blob changed: ' + name)
        cache[name] = raw.decode('utf-8').splitlines()

    def literal(ref):
        name, number = ref['path'], ref['line']
        check(name in pinned and ref['blob_sha'] == pinned.get(name), 'Unpinned source reference')
        check(type(number) is int and number > 0, 'Invalid source line')
        lines = cache.get(name, [])
        check(type(number) is int and 0 < number <= len(lines) and lines[number - 1] == ref['text'], 'Changed literal source row: ' + name)

    def refs(entry):
        check(bool(entry['candidate_refs']), 'Missing candidate consumer: ' + entry['id'])
        for name in entry['candidate_refs']:
            path = (doc / name).resolve()
            check(path.is_relative_to(doc.resolve()) and path.is_file(), 'Missing candidate reference: ' + name)
        check(entry['implementation_status'] == 'NOT_EVALUATED', 'Unsupported product claim')

    requirements = data['requirements']
    check(len(requirements) == 141 and {r['id'] for r in requirements} == REQ, 'Missing/duplicate requirement')
    links = {}
    for line in cache.get('docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md', []):
        match = re.match(r'\| ((?:S|R33)-\d{3}) \|', line)
        if match:
            links[match[1]] = set(re.findall(r'V34-\d{3}', line))
    check(set(links) == REQ, 'Incomplete source links')
    for row in requirements:
        literal(row['dossier'])
        check(row['dossier']['path'] == 'docs/ROADMAP_TRACEABILITY_v3_3.md' and row['dossier']['text'].startswith('| ' + row['id'] + ' |'), 'Wrong requirement dossier')
        check(bool(row['acceptance_sources']), 'No acceptance source')
        acceptance_path = 'docs/ROADMAP_HERITAGE_v3_3.md' if row['id'].startswith('S-') else 'docs/ROADMAP_MASTER_v3_3.md'
        expected_rows = [(i, line) for i, line in enumerate(cache.get(acceptance_path, []), 1) if line.startswith('| ' + row['id'] + ' |')]
        actual_rows = [(item['line'], item['text']) for item in row['acceptance_sources'] if item['path'] == acceptance_path]
        check(len(actual_rows) == len(row['acceptance_sources']) and actual_rows == expected_rows, 'Missing/changed acceptance row: ' + row['id'])
        for item in row['acceptance_sources']:
            literal(item)
        actual_links = row['historical_planning_tickets']
        check(len(actual_links) == len(set(actual_links)) and set(actual_links) == links.get(row['id']), 'Changed planning links: ' + row['id'])
        check(row['decision'] == 'PRESERVE_WITH_CLARIFICATION' and len(row['clarification']) > 15, 'Missing transfer decision')
        check(all(re.fullmatch(r'W(?:0[0-9]|1[0-6])', o) for o in row['candidate_owners']), 'Undefined candidate owner')
        check(all(re.fullmatch(r'CP[0-6]', g) for g in row['candidate_gates']), 'Undefined candidate gate')
        if row['id'] in GAPS:
            check(not actual_links and bool(row['candidate_owners']), 'Lost historical gap attribution')
        refs(row)
    check({r['id'] for r in requirements if not r['historical_planning_tickets']} == GAPS, 'Changed historical gap set')

    tickets = data['tickets']
    check(len(tickets) == 140 and {t['id'] for t in tickets} == TICKETS, 'Missing/duplicate ticket')
    for row in tickets:
        literal(row['source'])
        check(row['source']['path'] == lot_files.get(row['lot']), 'Wrong source lot')
        check(bool(re.match(r'\|\s*(?:\*\*)?' + re.escape(row['id']) + r'\b', row['source']['text'])), 'Wrong ticket source row')
        check(row['decision'] == 'PRESERVE_FULL_DOD', 'Reduced ticket DoD')
        refs(row)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-root', type=Path, required=True)
    parser.add_argument('--register', type=Path, default=DOC / 'SOURCE_TRANSFER_REGISTER.json')
    parser.add_argument('--id', help='After integrity validation, show one requirement/ticket and its complete source rows')
    args = parser.parse_args()
    try:
        data = json.loads(args.register.read_text(encoding='utf-8'))
        problems = validate(data, args.main_root)
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        print('FAIL source transfer:', exc)
        return 1
    if problems:
        print('\n'.join(problems))
        return 1
    if args.id:
        match = next((row for row in data['requirements'] + data['tickets'] if row['id'] == args.id), None)
        if match is None:
            print('FAIL unknown requirement/ticket:', args.id)
            return 1
        related = [row for row in data['tickets'] if row['id'] in match.get('historical_planning_tickets', [])]
        print(json.dumps({'entry': match, 'related_planning_tickets': related,
                          'preservation_rule': data['preservation_rule'],
                          'historical_link_semantics': data['historical_link_semantics']}, ensure_ascii=False, indent=2))
        return 0
    print('PASS literal 141 criteria / 140 DoD / 26 pins and references. Semantic and product verdicts are separate.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
