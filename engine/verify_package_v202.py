"""Run install integrity and every regression suite for SmartSVG V20.2."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'INSTALLATION_MANIFEST_V20_2.json').read_text('utf8'))
for rel,digest in manifest['fichiers_sha256'].items():
    f=root/rel
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:
        raise SystemExit('Manifest mismatch: '+rel)
spec=importlib.util.spec_from_file_location('smartsvg_v202_validation',root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pkg;spec.loader.exec_module(pkg)
needed=('SmartSVGLineArtV201','SmartSVGLineArtV2011','SmartSVGLineArtV2012','SmartSVGLineArtV202','SmartSVGStudioV20Express','SmartSVGStudioV20Expert')
for n in needed:
    if n not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Unregistered node '+n)
cls=pkg.NODE_CLASS_MAPPINGS['SmartSVGLineArtV202']
required=cls.INPUT_TYPES()['required']
for wf in root.joinpath('example_workflows').glob('SmartSVG_Studio_V20_2_*.json'):
    d=json.loads(wf.read_text('utf8'))
    matches=[n for n in d['nodes'] if n['type']=='SmartSVGLineArtV202']
    if len(matches)!=1:raise SystemExit('Missing V202 node '+wf.name)
    n=matches[0]
    widgets=[i['name'] for i in n['inputs'] if i.get('widget')]
    want=[k for k in required if k!='image']
    if widgets!=want or len(n['widgets_values'])!=len(want):
        raise SystemExit('Workflow widget order invalid: '+wf.name)
    if n['inputs'][-1]['name']!='masques_objets':raise SystemExit('MASK slot missing')
    for k in ('operation_cricut','segmentation_ia','repere_masque'):
        allowed=required[k][0]
        if n['widgets_values'][want.index(k)] not in allowed:
            raise SystemExit('Invalid '+k+' in '+wf.name)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],cwd=root,check=True)
print('VALIDATED: legacy V20.1.2 + V20.2 modules, workflows, SHA-256, full tests',flush=True)
