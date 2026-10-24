"""V20.1.1 complete QA; original V20 and V20.1 verifier remains untouched."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
root=Path(__file__).resolve().parent
process=subprocess.run([sys.executable,str(root/'verify_package.py')],cwd=root)
if process.returncode:sys.exit(process.returncode)
import importlib.util
spec=importlib.util.spec_from_file_location('pkg_v2011_check',root/'__init__.py',submodule_search_locations=[str(root)])
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
for name in ('SmartSVGLineArtV201','SmartSVGLineArtV2011','SmartSVGStudioV20Expert'):
    if name not in mod.NODE_CLASS_MAPPINGS:
        raise SystemExit('Missing node '+name)
for filename in ('SmartSVG_Studio_V20_1_1_LineArt_Express.json',
                 'SmartSVG_Studio_V20_1_1_Photo_Ecran_Exemple.json'):
    wf=json.loads((root/'example_workflows'/filename).read_text('utf8'))
    kind='SmartSVGLineArtV2011'
    node=next((x for x in wf['nodes'] if x['type']==kind),None)
    if node is None:raise SystemExit('Missing V20.1.1 workflow node: '+filename)
    cls=mod.NODE_CLASS_MAPPINGS[kind]
    actual=[x['name'] for x in node['inputs'] if x.get('widget')]
    expected=[x for x in cls.INPUT_TYPES()['required'] if x!='image']
    if expected!=actual or len(node['widgets_values'])!=len(expected):
        raise SystemExit('Bad V20.1.1 widget order: '+filename)
    for link_id,source,source_idx,target,target_idx,type_name in wf['links']:
        t=next(x for x in wf['nodes'] if x['id']==target)
        if t['inputs'][target_idx]['link']!=link_id:
            raise SystemExit('Bad V20.1.1 workflow link: '+filename)
manifest=json.loads((root/'INSTALLATION_MANIFEST_V20_1_1.json').read_text('utf8'))
for rel,digest in manifest['fichiers_sha256'].items():
    p=root/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise SystemExit('V20.1.1 file digest mismatch: '+rel)
print('SmartSVG V20.1.1: package, aliases, workflows and tests PASS',flush=True)
