"""Authoritative post-extraction verification for V20.3; preserves V20.2 history."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

root=Path(__file__).resolve().parent
manifest=json.loads((root/'INSTALLATION_MANIFEST_V20_3.json').read_text(encoding='utf8'))
items=manifest['fichiers_sha256']
if manifest['nombre_fichiers']!=len(items):
    raise SystemExit('Nombre de fichiers du manifeste incoherent')
for rel,digest in items.items():
    p=root/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise SystemExit('Signature invalide: '+rel)
# All V20.2 files unchanged EXCEPT the Python package loader that now exposes the new nodes.
legacy=json.loads((root/'INSTALLATION_MANIFEST_V20_2.json').read_text(encoding='utf8'))
for rel,digest in legacy['fichiers_sha256'].items():
    if rel=='__init__.py':continue
    if rel not in items or items[rel]!=digest:
        raise SystemExit('Regression binaire des sources V20.2: '+rel)
spec=importlib.util.spec_from_file_location('smartsvg_v203_package_validation',root/'__init__.py',
                                            submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=pkg
spec.loader.exec_module(pkg)
for key in ('SmartSVGLineArtV2012','SmartSVGLineArtV202','SmartSVGLineArtV203',
            'SmartSVGGPUPreflightV203','SmartSVGStudioV20Express','SmartSVGStudioV20Expert'):
    if key not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Noeud manque: '+key)
for wf in (root/'example_workflows').glob('SmartSVG_Studio_V20_3_*.json'):
    d=json.loads(wf.read_text(encoding='utf8'))
    new=[n for n in d['nodes'] if n['type'] in ('SmartSVGLineArtV203','SmartSVGGPUPreflightV203')]
    if len(new)!=1:raise SystemExit('Workflow doit posseder exactement un noeud V20.3: '+wf.name)
    n=new[0];k=n['type']
    cls=pkg.NODE_CLASS_MAPPINGS[k]
    req=cls.INPUT_TYPES()['required'];opt=cls.INPUT_TYPES().get('optional',{})
    widgets=[x['name'] for x in n['inputs'] if x.get('widget')]
    expected=[x for x in req if x!='image']
    if widgets!=expected or len(n['widgets_values'])!=len(expected):
        raise SystemExit('Widgets non synchronises: '+wf.name)
    inputs={x['name'] for x in n['inputs']}
    if inputs!=set(req)|set(opt):raise SystemExit('Ports du noeud non synchronises: '+wf.name)
    for name,value in zip(widgets,n['widgets_values']):
        spec=req[name]
        if isinstance(spec[0],(list,tuple)) and value not in spec[0]:
            raise SystemExit('Valeur du widget non valide: '+wf.name+' '+name)
    if k=='SmartSVGLineArtV203' and len([x for x in d['nodes'] if x['type']=='LoadImage'])!=1:
        raise SystemExit('LoadImage absent: '+wf.name)
# Fully execute historical and new tests, including Cricut parity.
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],
               check=True,cwd=root)
print('VALIDATION V20.3: manifeste, sources V20.2 preservees (hors init), workflows, tests OK')
