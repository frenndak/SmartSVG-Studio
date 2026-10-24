"""Clean-install V21.3.1 verifier, independent from archived older verifiers."""
import hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'INSTALLATION_MANIFEST_V21_3_1.json').read_text(encoding='utf8'))
files=manifest['fichiers_sha256']
if len(files)!=manifest['nombre_fichiers']:
    raise SystemExit('Manifest count incorrect')
for rel,expected in files.items():
    p=root/rel
    if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
        raise SystemExit('File missing or modified: '+rel)
legacy=json.loads((root/'INSTALLATION_MANIFEST_V21_3.json').read_text(encoding='utf8'))
# Historical production modules and original test suites remain byte-identical.
legacy_modules=0
for rel,expected in legacy['fichiers_sha256'].items():
    if rel.endswith('.py') and rel!='__init__.py':
        if files.get(rel)!=expected:raise SystemExit('Historical Python module changed: '+rel)
        legacy_modules+=1
name='smartsvg2131verified'
spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
for cls_name in ('SmartSVGExpressV212','SmartSVGExpressV213','SmartSVGInstancesV213',
                 'SmartSVGExpressV2131','SmartSVGInstancesV2131'):
    if cls_name not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Missing registered node '+cls_name)
wfs=sorted((root/'example_workflows').glob('SmartSVG_Studio_V21_3_1_*.json'))
if len(wfs)!=7:raise SystemExit('Expected 7 workflows')
for path in wfs:
    graph=json.loads(path.read_text(encoding='utf8'))
    nodes={node['id']:node for node in graph['nodes']}
    if len(nodes)!=len(graph['nodes']):raise SystemExit('Duplicate node IDs '+path.name)
    exps=[node for node in nodes.values() if node['type']=='SmartSVGExpressV2131']
    if len(exps)!=1:raise SystemExit('Express missing '+path.name)
    for item in nodes.values():
        if item['type'] not in ('SmartSVGExpressV2131','SmartSVGInstancesV2131'):continue
        cls=pkg.NODE_CLASS_MAPPINGS[item['type']]
        required=cls.INPUT_TYPES()['required'];opt=cls.INPUT_TYPES().get('optional',{})
        if [x['name'] for x in item['inputs']]!=list(required)+list(opt):
            raise SystemExit('Wrong ComfyUI inputs '+path.name)
        fields=[x['name'] for x in item['inputs'] if 'widget' in x]
        if fields!=list(required)[1:] or len(fields)!=len(item['widgets_values']):
            raise SystemExit('Widget ordering mismatch '+path.name)
        if [x['type'] for x in item['outputs']]!=list(cls.RETURN_TYPES):
            raise SystemExit('Output ordering mismatch '+path.name)
        for field,value in zip(fields,item['widgets_values']):
            choices=required[field][0]
            if isinstance(choices,(tuple,list)) and value not in choices:
                raise SystemExit('Invalid dropdown option '+path.name)
    for link in graph['links']:
        if link[1] not in nodes or link[3] not in nodes:
            raise SystemExit('Link references absent node '+path.name)
        left=nodes[link[1]];right=nodes[link[3]]
        if link[2]>=len(left['outputs']) or link[4]>=len(right['inputs']):
            raise SystemExit('Bad port index '+path.name)
        if left['outputs'][link[2]]['type']!=link[5] or right['inputs'][link[4]]['type']!=link[5]:
            raise SystemExit('Port type mismatch '+path.name)
    if any(x['type']=='SmartSVGInstancesV2131' for x in nodes.values()):
        if exps[0]['inputs'][-1].get('link') is None:
            raise SystemExit('Guided masks not connected '+path.name)
print(f'Integrity OK: {len(files)} files, {legacy_modules} old Python files, 7 workflows',flush=True)
if '--integrity-only' in sys.argv:raise SystemExit(0)
parts=[
 ['test_v141','test_v15','test_v16','test_v17','test_v18','test_v181'],
 ['test_v19','test_v191','test_v192','test_v193','test_v194','test_v195','test_v1951','test_v1952',
  'test_v196','test_v197','test_v1971','test_v198','test_v199','test_v20','test_v201',
  'test_v2011','test_v2012','test_v202','test_v202_merge','test_v203'],
 ['test_v204','test_v205','test_v206','test_v21','test_v211','test_v212','test_v213','test_v2131'],
]
total=0
for i,part in enumerate(parts):
    # The older vector tests can run together, while newer ones are isolated
    # to avoid cumulative allocations across dozens of image pipelines.
    batches=[part] if i<2 else [[t] for t in part]
    for batch in batches:
        command=[sys.executable,'-m','unittest','-q',*['tests.'+name for name in batch]]
        print('Testing: '+', '.join(batch),flush=True)
        result=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=120)
        print(result.stderr[-1800:],flush=True)
        if result.returncode!=0:raise SystemExit('Test failure: '+', '.join(batch))
        match=re.search(r'Ran (\d+) tests?',result.stderr)
        if not match:raise SystemExit('Unable to confirm executed count '+', '.join(batch))
        total+=int(match.group(1))
print(f'V21.3.1 VERIFIED: {total} successful tests.',flush=True)
