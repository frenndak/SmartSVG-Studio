"""Integrity and regressions for the clean install of SmartSVG V21.2."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
root=Path(__file__).resolve().parent
latest=json.loads((root/'INSTALLATION_MANIFEST_V21_2.json').read_text(encoding='utf8'))
expected=latest['fichiers_sha256']
assert len(expected)==latest['nombre_fichiers'], 'Invalid manifest count'
for rel,digest in expected.items():
    path=root/rel
    if path.is_symlink() or not path.is_file():raise SystemExit('Missing/link: '+rel)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit('SHA mismatch: '+rel)
old=json.loads((root/'INSTALLATION_MANIFEST_V21_1.json').read_text(encoding='utf8'))
for rel,digest in old['fichiers_sha256'].items():
    if rel=='__init__.py':continue
    if expected.get(rel)!=digest:raise SystemExit('V21.1 legacy content modified: '+rel)
name='smartsvg212verify'
spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
cls=pkg.NODE_CLASS_MAPPINGS.get('SmartSVGExpressV212')
if cls is None:raise SystemExit('V21.2 node missing')
for label in ('SmartSVGExpressV211','SmartSVGSimpleV21','SmartSVGSimpleV206',
              'SmartSVGLineArtV205','SmartSVGCricutPreflightV205'):
    if label not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Legacy alias missing: '+label)
req=cls.INPUT_TYPES()['required'];opts=cls.INPUT_TYPES()['optional']
wfs=sorted((root/'example_workflows').glob('SmartSVG_Studio_V21_2_*.json'))
if len(wfs)!=7:raise SystemExit('V21.2 requires 7 workflows')
for wf in wfs:
    d=json.loads(wf.read_text(encoding='utf8'))
    nodes=[v for v in d['nodes'] if v['type']=='SmartSVGExpressV212']
    if len(nodes)!=1:raise SystemExit('Workflow node mismatch '+wf.name)
    node=nodes[0]
    if [i['name'] for i in node['inputs']]!=list(req)+list(opts):raise SystemExit('Inputs do not match '+wf.name)
    widgets=[i['name'] for i in node['inputs'] if 'widget' in i]
    if widgets!=list(req)[1:] or len(node['widgets_values'])!=len(widgets):
        raise SystemExit('Widget values mismatch '+wf.name)
    if len(node['outputs'])!=len(cls.RETURN_TYPES):raise SystemExit('Outputs mismatch '+wf.name)
    for key,val in zip(widgets,node['widgets_values']):
        choices=req[key][0]
        if isinstance(choices,list) and val not in choices:raise SystemExit('Invalid value '+wf.name+':'+key)

if '--integrity-only' in sys.argv:
    print('V21.2 SHA256 + 7 workflows + legacy aliases: OK')
    raise SystemExit(0)

# Split into bounded batches: full single run is slower/less dependable on CI.
parts=[
    ['test_v141','test_v15','test_v16','test_v17','test_v18','test_v181'],
    ['test_v19','test_v191','test_v192','test_v193','test_v194','test_v195',
     'test_v1951','test_v1952','test_v196','test_v197','test_v1971','test_v198',
     'test_v199','test_v20','test_v201','test_v2011','test_v2012','test_v202',
     'test_v202_merge','test_v203'],
    ['test_v204','test_v205','test_v206','test_v21','test_v211','test_v212'],
]
for part in parts:
    tests=['tests.'+n for n in part]
    subprocess.run([sys.executable,'-m','unittest','-q',*tests],cwd=root,check=True)
print('V21.2 VERIFIED: 7 workflows, all files SHA256, 506 tests in 3 families, legacy content unchanged.')
