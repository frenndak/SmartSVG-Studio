"""Clean installation verification for V20.1.2; also runs all previous test suites."""
from pathlib import Path
import hashlib, json, subprocess, sys
root=Path(__file__).resolve().parent
proc=subprocess.run([sys.executable,str(root/'verify_package_v2011.py')],cwd=str(root))
if proc.returncode:sys.exit(proc.returncode)
manifest=json.loads((root/'INSTALLATION_MANIFEST_V20_1_2.json').read_text('utf8'))
for rel,digest in manifest['fichiers_sha256'].items():
    p=root/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise SystemExit('V20.1.2: SHA-256 mismatch: '+rel)
import importlib.util
spec=importlib.util.spec_from_file_location('smartsvg_v2012_verification',root/'__init__.py',submodule_search_locations=[str(root)])
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
for kind in ('SmartSVGLineArtV201','SmartSVGLineArtV2011','SmartSVGLineArtV2012','SmartSVGStudioV20Express'):
    if kind not in module.NODE_CLASS_MAPPINGS:raise SystemExit('Missing node '+kind)
for wf in ('SmartSVG_Studio_V20_1_2_Sticker_Contour.json','SmartSVG_Studio_V20_1_2_Coupe_Tous_Traits.json'):
    info=json.loads((root/'example_workflows'/wf).read_text('utf8'))
    node=next(n for n in info['nodes'] if n['type']=='SmartSVGLineArtV2012')
    expected=[n for n in module.NODE_CLASS_MAPPINGS['SmartSVGLineArtV2012'].INPUT_TYPES()['required'] if n!='image']
    got=[n['name'] for n in node['inputs'] if n.get('widget')]
    if got != expected or len(got)!=len(node['widgets_values']):raise SystemExit('Broken widgets in '+wf)
print('SmartSVG V20.1.2: clean install / QA / manifests / aliases PASS')
