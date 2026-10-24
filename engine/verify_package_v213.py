"""Clean-install verifier for SmartSVG Studio V21.3."""
import hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'INSTALLATION_MANIFEST_V21_3.json').read_text(encoding='utf8'))
expected=manifest['fichiers_sha256']
if len(expected)!=manifest['nombre_fichiers']:raise SystemExit('V21.3 manifest count incorrect')
for rel,digest in expected.items():
    p=root/rel
    if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise SystemExit('V21.3 file integrity error '+rel)
old=json.loads((root/'INSTALLATION_MANIFEST_V21_2.json').read_text(encoding='utf8'))
for rel,digest in old['fichiers_sha256'].items():
    if rel=='__init__.py':continue
    if expected.get(rel)!=digest:raise SystemExit('V21.2 legacy module changed: '+rel)
name='smartsvg213verified'
spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
req_old=('SmartSVGExpressV212','SmartSVGExpressV211','SmartSVGSimpleV21','SmartSVGLineArtV205')
for alias in (*req_old,'SmartSVGExpressV213','SmartSVGInstancesV213'):
    if alias not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Missing ComfyUI node '+alias)
wfs=sorted((root/'example_workflows').glob('SmartSVG_Studio_V21_3_*.json'))
if len(wfs)!=7:raise SystemExit('Expected 7 V21.3 workflows')
for path in wfs:
    d=json.loads(path.read_text(encoding='utf8'))
    nodes={n['id']:n for n in d['nodes']}
    if len(nodes)!=len(d['nodes']):raise SystemExit('Duplicate node IDs '+path.name)
    express=[n for n in nodes.values() if n['type']=='SmartSVGExpressV213']
    if len(express)!=1:raise SystemExit('Express missing: '+path.name)
    for n in nodes.values():
        if n['type'] not in ('SmartSVGExpressV213','SmartSVGInstancesV213'):continue
        cls=pkg.NODE_CLASS_MAPPINGS[n['type']]
        fields=cls.INPUT_TYPES()['required'];optional=cls.INPUT_TYPES().get('optional',{})
        if [x['name'] for x in n['inputs']]!=list(fields)+list(optional):
            raise SystemExit('Input ports do not match '+path.name)
        widgets=[x['name'] for x in n['inputs'] if 'widget' in x]
        if widgets!=list(fields)[1:]:raise SystemExit('Wrong widget order '+path.name)
        if len(widgets)!=len(n['widgets_values']):raise SystemExit('Wrong widget count '+path.name)
        if [x['type'] for x in n['outputs']]!=list(cls.RETURN_TYPES):
            raise SystemExit('Output ports do not match '+path.name)
        for field,val in zip(widgets,n['widgets_values']):
            choices=fields[field][0]
            if isinstance(choices,(list,tuple)) and val not in choices:
                raise SystemExit('Illegal combo value '+path.name+' '+field)
    for l in d['links']:
        if l[1] not in nodes or l[3] not in nodes:raise SystemExit('Invalid link endpoint')
        src=nodes[l[1]];dst=nodes[l[3]]
        if l[2]>=len(src['outputs']) or l[4]>=len(dst['inputs']):raise SystemExit('Invalid link slot')
        if src['outputs'][l[2]]['type']!=l[5] or dst['inputs'][l[4]]['type']!=l[5]:
            raise SystemExit('Wrong link types '+path.name)
    if any(n['type']=='SmartSVGInstancesV213' for n in nodes.values()):
        if express[0]['inputs'][-1]['link'] is None:raise SystemExit('Guided mask not connected')
if '--integrity-only' in sys.argv:
    print('V21.3 integrity + 7 workflows + legacy classes: OK');raise SystemExit(0)
parts=[
  ['test_v141','test_v15','test_v16','test_v17','test_v18','test_v181'],
  ['test_v19','test_v191','test_v192','test_v193','test_v194','test_v195',
   'test_v1951','test_v1952','test_v196','test_v197','test_v1971','test_v198',
   'test_v199','test_v20','test_v201','test_v2011','test_v2012','test_v202',
   'test_v202_merge','test_v203'],
  ['test_v204','test_v205','test_v206','test_v21','test_v211','test_v212','test_v213'],
]
for index,part in enumerate(parts):
    # Isolate recent suites to avoid accumulated image/torch allocations and
    # intermittent combined-process timeouts on constrained environments.
    batches=[[name] for name in part] if index==2 else [part]
    for batch in batches:
        print('Tests:', ', '.join(batch),flush=True)
        subprocess.run([sys.executable,'-m','unittest','-q',*['tests.'+name for name in batch]],cwd=root,check=True,timeout=60)
print('SmartSVG V21.3 verified: 534 software tests + legacy integrity + 7 workflows')
