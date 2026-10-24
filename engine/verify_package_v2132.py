"""Independent final verifier: archives preserved except root __init__ and confirmed QA SVG fix."""
import hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'INSTALLATION_MANIFEST_V21_3_2.json').read_text(encoding='utf8'))
files=manifest['fichiers_sha256']
if len(files)!=manifest['nombre_fichiers']:raise SystemExit('Manifest size mismatch')
for rel,sha in files.items():
    f=root/rel
    if not f.is_file() or f.is_symlink() or hashlib.sha256(f.read_bytes()).hexdigest()!=sha:
        raise SystemExit('Incorrect packaged file: '+rel)
legacy=json.loads((root/'INSTALLATION_MANIFEST_V21_3_1.json').read_text(encoding='utf8'))
changed=[]; preserved=0
for rel,sha in legacy['fichiers_sha256'].items():
    if rel.endswith('.py') and rel!='__init__.py':
        if files.get(rel)!=sha:changed.append(rel)
        else:preserved+=1
if changed!=['controle_export_v212.py']:raise SystemExit('Unexpected historical changes: '+str(changed))
name='smartsvg2132checked';spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
for key in ('SmartSVGExpressV2131','SmartSVGInstancesV2131','SmartSVGExpressV2132','SmartSVGInstancesV2132','SmartSVGDiagnosticV2132'):
    if key not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Missing node '+key)
wfs=sorted((root/'example_workflows').glob('SmartSVG_Studio_V21_3_2_*.json'))
if len(wfs)!=8:raise SystemExit('Unexpected number of V21.3.2 workflows')
for wf in wfs:
    a=json.loads(wf.read_text(encoding='utf8'));graph={n['id']:n for n in a['nodes']}
    if len(graph)!=len(a['nodes']):raise SystemExit('Duplicate node in '+wf.name)
    for n in a['nodes']:
        if n['type'] in ('SmartSVGExpressV2132','SmartSVGInstancesV2132','SmartSVGDiagnosticV2132'):
            cls=pkg.NODE_CLASS_MAPPINGS[n['type']];spec2=cls.INPUT_TYPES();port=list(spec2['required'])+list(spec2.get('optional',{}))
            if [i['name'] for i in n['inputs']]!=port:raise SystemExit('Bad node input '+wf.name)
            if [o['type'] for o in n['outputs']]!=list(cls.RETURN_TYPES):raise SystemExit('Bad node output '+wf.name)
            widgets=[i['name'] for i in n['inputs'] if 'widget' in i]
            if len(widgets)!=len(n['widgets_values']):raise SystemExit('Bad widgets '+wf.name)
            for field,value in zip(widgets,n['widgets_values']):
                choices=spec2['required'].get(field,('',))[0]
                if isinstance(choices,(list,tuple)) and value not in choices:raise SystemExit('Invalid option '+field)
    for link in a['links']:
        if link[1] not in graph or link[3] not in graph:raise SystemExit('Bad link '+wf.name)
        l=graph[link[1]];r=graph[link[3]]
        if link[2]>=len(l['outputs']) or link[4]>=len(r['inputs']):raise SystemExit('Bad port index '+wf.name)
        if l['outputs'][link[2]]['type']!=link[5] or r['inputs'][link[4]]['type']!=link[5]:
            raise SystemExit('Bad port type '+wf.name)
print(f'Integrity checked: {len(files)} files, {preserved} preserved historical Python modules, {len(wfs)} workflows.',flush=True)
if '--integrity-only' in sys.argv:sys.exit(0)
if '--suite' not in sys.argv:
    print('Run tests independently with: python verify_package_v2132.py --suite 1, then --suite 2 and --suite 3',flush=True)
    sys.exit(0)
try:selected=int(sys.argv[sys.argv.index('--suite')+1])
except (ValueError,IndexError):raise SystemExit('Choose --suite 1, 2 or 3')
if selected not in (1,2,3):raise SystemExit('Suite must be 1, 2 or 3')
parts=[
 ['test_v141','test_v15','test_v16','test_v17','test_v18','test_v181'],
 ['test_v19','test_v191','test_v192','test_v193','test_v194','test_v195','test_v1951','test_v1952','test_v196','test_v197','test_v1971','test_v198','test_v199','test_v20','test_v201','test_v2011','test_v2012','test_v202','test_v202_merge','test_v203'],
 ['test_v204','test_v205','test_v206','test_v21','test_v211','test_v212','test_v213','test_v2131','test_v2132','test_svg_root_v2132'],
]
total=0
for idx,part in enumerate(parts):
    if idx+1!=selected:continue
    groups=[part]  # one fresh Python process per family avoids costly repeated model imports
    for group in groups:
        cmd=[sys.executable,'-m','unittest','-q',*['tests.'+x for x in group]]
        p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=120)
        if p.returncode:print(p.stderr[-2500:]);raise SystemExit('Test suite failed: '+','.join(group))
        m=re.search(r'Ran (\d+) tests?',p.stderr)
        if not m:raise SystemExit('No test count: '+str(group))
        total+=int(m.group(1))
    print(f'Test group {idx+1} passed; cumulative {total}',flush=True)
expected={1:50,2:300,3:227}[selected]
if total!=expected:raise SystemExit(f'Expected {expected} tests, got {total}')
print(f'SmartSVG V21.3.2: suite {selected} — {total} passed.',flush=True)
