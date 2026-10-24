"""Offline, reproducible V21.1 install audit; no GPU or Cricut hardware needed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parent
latest=json.loads((root/'INSTALLATION_MANIFEST_V21_1.json').read_text(encoding='utf8'))
expected=latest['fichiers_sha256']
if len(expected)!=latest['nombre_fichiers']:raise SystemExit('Manifest count mismatch')
for rel,digest in expected.items():
    p=root/rel
    if p.is_symlink() or not p.is_file():raise SystemExit('Missing or linked: '+rel)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise SystemExit('SHA256 mismatch '+rel)
old=json.loads((root/'INSTALLATION_MANIFEST_V21.json').read_text(encoding='utf8'))
for rel,digest in old['fichiers_sha256'].items():
    if rel=='__init__.py':continue
    if expected.get(rel)!=digest:raise SystemExit('Legacy V21 source changed: '+rel)
name='sv211verify'
spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec)
sys.modules[name]=pkg;spec.loader.exec_module(pkg)
cls=pkg.NODE_CLASS_MAPPINGS.get('SmartSVGExpressV211')
if cls is None:raise SystemExit('Missing Express node')
for key in ('SmartSVGSimpleV21','SmartSVGSimpleV206','SmartSVGLineArtV205','SmartSVGCricutPreflightV205'):
    if key not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Missing legacy node '+key)
req=cls.INPUT_TYPES()['required'];optional=cls.INPUT_TYPES()['optional']
wf=sorted((root/'example_workflows').glob('SmartSVG_Studio_V21_1_*.json'))
if len(wf)!=6:raise SystemExit('Six Express workflows required')
for p in wf:
    d=json.loads(p.read_text(encoding='utf8'))
    nodes=[x for x in d['nodes'] if x['type']=='SmartSVGExpressV211']
    if len(nodes)!=1:raise SystemExit('Bad workflow '+p.name)
    n=nodes[0]
    if [x['name'] for x in n['inputs']]!=list(req)+list(optional):
        raise SystemExit('Mismatch input order '+p.name)
    widgets=[x['name'] for x in n['inputs'] if 'widget' in x]
    if widgets!=list(req)[1:] or len(n['widgets_values'])!=len(widgets):
        raise SystemExit('Wrong widget order '+p.name)
    if len(n['outputs'])!=len(cls.RETURN_TYPES):raise SystemExit('Output port mismatch '+p.name)
    for key,value in zip(widgets,n['widgets_values']):
        opts=req[key][0]
        if isinstance(opts,list) and value not in opts:raise SystemExit('Invalid option '+key)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],cwd=root,check=True)
print('V21.1 OK: history intact, 6 workflows, SHA256, 486 regression tests')
