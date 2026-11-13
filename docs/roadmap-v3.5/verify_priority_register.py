"""Verify V3.5 planning inventory and ordering; never certify product behavior."""
from __future__ import annotations

import argparse
from hashlib import sha1
import json
from pathlib import Path
import re

DOC = Path(__file__).resolve().parent
REJECTED = {'O-003','O-015','O-018','O-021','O-024','O-027','O-030','O-033'}
GROUPS = {'Fondation produit','Architecture UI','Smart Delivery','Smart Cut Advisor',
          'Smart Weeding','Print Then Cut Assistant','Compatibilité Design Space','Smart Cost',
          'Séries personnalisées','Smart Cut Feedback','Recettes/modèles partageables',
          'Production multimarque','Optimisation multicritère','80 capacités UX','Héritage intégral V3.4'}
SOURCES = {'INHERITANCE_REGISTER.md','UX_ARCHITECTURE_AND_WORKFLOWS.md',
           'COV19_OPPORTUNITIES_001_033_DECISIONS.md','SCENARIOS_V34_02_08.md',
           'SCENARIOS_V34_09_16.md','SCENARIOS_V34_17_22.md',
           'AUTOMATION_QUALITY_CONTRACT.md','SOURCE_142_SCOPE_SNAPSHOT.md'}
PORTS = {'engine/smartsvg_cricut/delivery_v21122.py',
         'engine/smartsvg_governance/artifact_qa.py',
         'engine/smartsvg_cricut/direct_import_v218.py',
         'engine/smartsvg_vector/svg_publication.py',
         'engine/smartsvg_core/template_geometry_v34.py',
         'engine/smartsvg_core/template_preflight_v34.py',
         'engine/smartsvg_core/project_contracts.py'}


def rows(path):
    return [[c.strip() for c in line.split('|')[1:-1]]
            for line in path.read_text(encoding='utf-8').splitlines() if line.startswith('|')]


def blob(raw):
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def validate(plan, doc=DOC, *, pinned=False, main_root=None):
    doc = Path(doc).resolve()
    errors = []

    def check(ok, message):
        if not ok:
            errors.append(message)

    def unique_ids(values, expected, field='id'):
        ids = [v[field] if field else v for v in values]
        check(len(ids) == len(set(ids)) and set(ids) == expected,
              'Missing, duplicate or unknown IDs: ' + (field or 'inheritance'))

    expected_ux = {f'{g}{n:02d}' for g,count in [('A',16),('B',14),('C',18),('D',12),('E',20)] for n in range(1,count+1)}
    unique_ids(plan['ux'], expected_ux)
    check(plan['schema'] == 'smartsvg-v35-priorities/1', 'Unknown schema')
    check(plan['status'] == 'CANDIDATE' and plan['active_roadmap'] == '3.4', 'Unauthorized authority promotion')
    check(plan['canonical_branch'] == 'roadmap/v3-5-design-candidate-20261112', 'Wrong master branch')
    source = {r[0].strip('*` '): r[1] for r in rows(doc/'INHERITANCE_REGISTER.md')
              if re.fullmatch(r'[ABCDE]\d{2}',r[0].strip('*` '))}
    priority = {r[0].strip('*` '): r[3] for r in rows(doc/'UX_ARCHITECTURE_AND_WORKFLOWS.md')
                if re.fullmatch(r'[ABCDE]\d{2}',r[0].strip('*` '))}
    for item in plan['ux']:
        sid = item['id']
        check(item['description'] == source.get(sid), 'Changed source description: '+sid)
        check(item['source_priority'] == priority.get(sid), 'Changed source priority: '+sid)
        check(type(item['recommended_entry_rank']) is int and 1 <= item['recommended_entry_rank'] <= 12,
              'Invalid delivery rank: '+sid)
        check(item['primary_unit'] in {f'W{n:02d}' for n in range(17)}, 'Unknown delivery unit: '+sid)
        check(item['status'] == 'CANDIDATE_SEMANTIC_REVIEW_OPEN', 'Unsupported maturity claim: '+sid)
        check(bool(item['design_files']) and all((doc/p).is_file() for p in item['design_files']), 'Missing design: '+sid)
    unique_ids(plan['source142_groups'], GROUPS, 'source_group')
    check(plan['source_groups_file'] == 'SOURCE_142_SCOPE_SNAPSHOT.md', 'Wrong scope source')
    group_source = {r[0].strip('*` '):r for r in rows(doc/'SOURCE_142_SCOPE_SNAPSHOT.md')
                    if r[0].strip('*` ') in GROUPS}
    check(set(group_source) == GROUPS, 'Missing source142 scope in fixture')
    for item in plan['source142_groups']:
        original = group_source.get(item['source_group'])
        check(original is not None and [item['value_and_scope'],item['source_decision']] == original[1:3],
              'Changed source142 scope/decision: '+item['source_group'])
        check(bool(item['units']) and set(item['units']) <= {f'W{n:02d}' for n in range(17)},
              'Missing or unknown units for source142 group: '+item['source_group'])
    unique_ids(plan['opportunities'], {f'O-{n:03d}' for n in range(1,34)})
    source_opps = {r[0].strip('*` '):r for r in rows(doc/'COV19_OPPORTUNITIES_001_033_DECISIONS.md')
                   if re.fullmatch(r'O-\d{3}',r[0].strip('*` '))}
    for item in plan['opportunities']:
        row = source_opps.get(item['id'])
        check(row is not None and [item['decision'],item['horizon'],item['treatment'],item['contrary_risk']] == row[1:5],
              'Changed opportunity decision: '+item['id'])
    check({o['id'] for o in plan['opportunities'] if 'REJETER' in o['decision']} == REJECTED, 'Lost rejection')
    inherit = plan['inheritance']
    unique_ids(inherit['lots'], {f'{n:02d}' for n in range(1,25)}, None)
    unique_ids(inherit['requirements'], {f'S-{n:03d}' for n in range(1,102)} | {f'R33-{n:03d}' for n in range(1,41)}, None)
    unique_ids(inherit['tickets'], {f'V34-{n:03d}' for n in range(1,141)}, None)
    source_scenarios = {}
    for name in ('SCENARIOS_V34_02_08.md','SCENARIOS_V34_09_16.md','SCENARIOS_V34_17_22.md'):
        for row in rows(doc/name):
            if re.fullmatch(r'T-V34-\d{2}-\d{2}',row[0]):
                check(row[0] not in source_scenarios, 'Duplicate source scenario: '+row[0])
                source_scenarios[row[0]] = name
    check(len(source_scenarios) == 437, 'Wrong source scenario count')
    unique_ids(inherit['scenarios'], set(source_scenarios))
    for item in inherit['scenarios']:
        check(item['inventory_file'] == source_scenarios.get(item['id']), 'Wrong scenario source: '+item['id'])
    check(set(plan['exceptions']['scenarios_without_source_ticket']) ==
          {'T-V34-03-16','T-V34-06-22','T-V34-06-24','T-V34-06-25','T-V34-07-16','T-V34-07-25'}, 'Lost six exceptions')
    check(set(plan['exceptions']['requirements_without_v34']) ==
          {'S-021','S-036','S-037','S-044','S-047','S-064','S-066','S-092','S-099','R33-028'}, 'Lost G6/G9 requirements')
    index_ids = [r[1] for r in rows(doc/'PRIORITY_INDEX.md') if len(r)>1 and re.fullmatch(r'[ABCDE]\d{2}',r[1])]
    unique_ids(index_ids, expected_ux, None)
    expected_order = [x['id'] for x in sorted(plan['ux'],key=lambda x:(x['recommended_entry_rank'],x['id']))]
    check(index_ids == expected_order, 'Human index differs from recommended ordering')
    indexed = {r[1]:r for r in rows(doc/'PRIORITY_INDEX.md') if len(r)>1 and re.fullmatch(r'[ABCDE]\d{2}',r[1])}
    for item in plan['ux']:
        row = indexed.get(item['id'])
        check(row is not None and row[0] == str(item['recommended_entry_rank'])
              and row[2] == item['description'] and row[3] == item['source_priority']
              and row[4].startswith(item['primary_unit']+' '), 'Changed human index content: '+item['id'])
    proof = plan['proof']
    check(proof['semantic_certification'] == 'OPEN' and proof['new_zip_implementation'] == 'ABSENT'
          and proof['new_zip_tests'] == 'NOT_RUN', 'Unsupported feature/semantic proof claim')
    check(proof['historical_delivery_tests'] == {'count':31,'failures':0,'skipped':0,'scope':'MANIFEST_ONLY_NOT_ZIP'},
          'Changed bounded historical test evidence')
    unique_ids(plan['source_documents'], {'docs/roadmap-v3.5/'+name for name in SOURCES}, 'path')
    unique_ids(plan['main_ports'], PORTS, 'path')
    if pinned:
        for item in plan['source_documents']:
            file = doc.parents[1]/item['path']
            check(file.is_file() and blob(file.read_bytes()) == item['sha'], 'Source snapshot changed: '+item['path'])
    if main_root:
        for item in plan['main_ports']:
            file = Path(main_root)/item['path']
            check(file.is_file() and blob(file.read_bytes()) == item['blob_sha'], 'Main port differs: '+item['path'])
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pinned',action='store_true')
    parser.add_argument('--main-root',type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads((DOC/'PRIORITY_REGISTER.json').read_text(encoding='utf-8')),
                          pinned=args.pinned,main_root=args.main_root)
    except (OSError,ValueError,KeyError,TypeError,IndexError) as exc:
        print('FAIL documentaire: '+str(exc))
        return 1
    if result:
        print('\n'.join(result))
        return 1
    print('PASS documentaire: 80 UX, 15 groupes, 33 opportunités, 24/141/140/437 hérités. Couverture sémantique OPEN ; produit non qualifié.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
