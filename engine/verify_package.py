"""SmartSVG V20.0 package QA. Runs from an extracted ZIP, without ComfyUI UI."""
from pathlib import Path
import json
import subprocess
import sys
root=Path(__file__).resolve().parent
mandatory=['__init__.py','node_v195.py','node_v196.py','mask_compare_v196.py',
           'photo_contacts_v195.py','photo_geometry_v191.py','README.md','CHANGELOG.md',
           'AUDIT_V19_6.md','AUDIT_V19_7.md','telemetry_v197.py','node_v197.py','node_v1971.py','tests/test_v196.py','tests/test_v197.py','tests/test_v1971.py','mask_alignment_v198.py','node_v198.py','tests/test_v198.py','requirements.txt','adaptive_refiner_v199.py','node_v199.py','tests/test_v199.py','AUDIT_V19_9.md','adaptive_refiner_v20.py','node_v20.py','README_V20.md','AUDIT_V20.md','tests/test_v20.py','example_workflows/SmartSVG_Studio_V20_Diagnostic_Installation.json','INSTALLATION_MANIFEST_V20.json','lineart_v201.py','node_v201.py','tests/test_v201.py','README_V20_1.md','ROADMAP_APRES_V20_1.md','example_workflows/SmartSVG_Studio_V20_1_LineArt_Express.json','INSTALLATION_MANIFEST_V20_1.json']
for rel in mandatory:
    if not (root/rel).is_file():raise SystemExit(f'Missing required file: {rel}')

import importlib.util
spec=importlib.util.spec_from_file_location('smartsvg_v196_pack',root/'__init__.py',submodule_search_locations=[str(root)])
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
for kind in ('Express','Expert'):
    wf=json.loads((root/'example_workflows'/f'SmartSVG_Studio_V19_7_1_{kind}.json').read_text('utf-8'))
    registered=f'SmartSVGStudioV1971{kind}'
    cls=mod.NODE_CLASS_MAPPINGS.get(registered)
    if cls is None:raise SystemExit(f'Node not registered: {registered}')
    target=[n for n in wf['nodes'] if n['type']==registered]
    if len(target)!=1:raise SystemExit('Invalid workflow nodes')
    node=target[0]
    ordered_required=[k for k in cls.INPUT_TYPES()['required'] if k!='image']
    widgets=[i['name'] for i in node['inputs'] if i.get('widget')]
    if widgets!=ordered_required or len(widgets)!=len(node['widgets_values']):
        raise SystemExit('Mismatched workflow widget names, order or values')
    nodes={n['id']:n for n in wf['nodes']}
    for lid,_,_,dst,index,typ in wf['links']:
        if nodes[dst]['inputs'][index]['link']!=lid or nodes[dst]['inputs'][index]['type']!=typ:
            raise SystemExit('Broken workflow link')
for kind in ('Express','Expert'):
    wf=json.loads((root/'example_workflows'/f'SmartSVG_Studio_V19_8_{kind}.json').read_text('utf8'))
    registered=f'SmartSVGStudioV198{kind}'
    cls=mod.NODE_CLASS_MAPPINGS.get(registered)
    if cls is None:raise SystemExit('Nœud V19.8 manquant: '+registered)
    node=next((n for n in wf['nodes'] if n['type']==registered),None)
    if node is None:raise SystemExit('Workflow V19.8 manquant: '+registered)
    ordered_required=[k for k in cls.INPUT_TYPES()['required'] if k!='image']
    widgets=[i['name'] for i in node['inputs'] if i.get('widget')]
    if widgets!=ordered_required or len(widgets)!=len(node['widgets_values']):
        raise SystemExit('Workflow V19.8: ordre des widgets incompatible')
    nodes={n['id']:n for n in wf['nodes']}
    for lid,_,_,dst,index,typ in wf['links']:
        if nodes[dst]['inputs'][index]['link']!=lid or nodes[dst]['inputs'][index]['type']!=typ:
            raise SystemExit('Workflow V19.8: lien rompu')
helper=json.loads((root/'example_workflows'/'SmartSVG_Studio_V19_8_Comparer_Puis_Exporter.json').read_text('utf8'))
comparator=next(n for n in helper['nodes'] if n['type']=='SmartSVGAlignMasksV198')
if next(v['link'] for v in comparator['inputs'] if v['name']=='masque_reference') is not None:
    raise SystemExit('Masque reference: le workflow ne doit pas simuler un masque IA')
for clazz in ('SmartSVGAlignMasksV198','SmartSVGStudioV198Express','SmartSVGStudioV198Expert','SmartSVGCompareMasksV196','SmartSVGGpuDiagnosticV196','SmartSVGStudioV1952Expert','SmartSVGStudioV196Expert'):
    if clazz not in mod.NODE_CLASS_MAPPINGS:raise SystemExit(f'Regression: node {clazz} missing')
for kind in ('Express','Expert'):
    wf=json.loads((root/'example_workflows'/f'SmartSVG_Studio_V19_9_{kind}.json').read_text('utf8'))
    clazz='SmartSVGStudioV199'+kind
    cls=mod.NODE_CLASS_MAPPINGS[clazz]
    nn=next(n for n in wf['nodes'] if n['type']==clazz)
    expected=[n for n in cls.INPUT_TYPES()['required'] if n!='image']
    widgets=[n['name'] for n in nn['inputs'] if n.get('widget')]
    if expected != widgets or len(nn['widgets_values'])!=len(widgets):
        raise SystemExit('V19.9: widget values incorrect order')
    nodes={n['id']:n for n in wf['nodes']}
    for lid,_,_,dst,index,typ in wf['links']:
        if nodes[dst]['inputs'][index]['link']!=lid or nodes[dst]['inputs'][index]['type']!=typ:
            raise SystemExit('V19.9: broken link')
for clazz in ('SmartSVGAdaptiveV199','SmartSVGStudioV199Expert','SmartSVGStudioV199Express'):
    if clazz not in mod.NODE_CLASS_MAPPINGS:raise SystemExit('V19.9: unregistered node '+clazz)
demo=json.loads((root/'example_workflows'/'SmartSVG_Studio_V19_9_Photo_Orchestration.json').read_text('utf8'))
nn=next(n for n in demo['nodes'] if n['type']=='SmartSVGStudioV199Express')
widgets=[i['name'] for i in nn['inputs'] if i.get('widget')]
if nn['widgets_values'][widgets.index('raffinement_ia')]!='diagnostic':
    raise SystemExit('V19.9 photo demo does not run diagnostic mode')
# V20.0 nodes, workflows, and read-only diagnostics.
for kind in ('Express','Expert'):
    fname=f'SmartSVG_Studio_V20_{kind}.json'
    wf=json.loads((root/'example_workflows'/fname).read_text(encoding='utf8'))
    clazz='SmartSVGStudioV20'+kind
    instance=mod.NODE_CLASS_MAPPINGS[clazz]
    entries=[n for n in wf['nodes'] if n['type']==clazz]
    if len(entries)!=1:raise SystemExit('V20: invalid workflow class '+clazz)
    node=entries[0]
    widget_keys=[field['name'] for field in node['inputs'] if field.get('widget')]
    expected=[field for field in instance.INPUT_TYPES()['required'] if field!='image']
    if widget_keys!=expected or len(widget_keys)!=len(node['widgets_values']):
        raise SystemExit('V20: workflow widget values mismatch')
    nodes={n['id']:n for n in wf['nodes']}
    for lid,_,_,dst,index,typ in wf['links']:
        if nodes[dst]['inputs'][index]['link']!=lid:raise SystemExit('V20: workflow link broken')
for key in ('SmartSVGAdaptiveV20','SmartSVGStudioV20Express','SmartSVGStudioV20Expert','SmartSVGEnvironmentV20'):
    if key not in mod.NODE_CLASS_MAPPINGS:raise SystemExit('V20 node missing: '+key)
preflight=json.loads((root/'example_workflows'/'SmartSVG_Studio_V20_Diagnostic_Installation.json').read_text(encoding='utf8'))
if not any(n['type']=='SmartSVGEnvironmentV20' for n in preflight['nodes']):
    raise SystemExit('V20: preflight workflow invalid')
# Manifest contains all files except itself; check file content after clean extraction.
from hashlib import sha256
manifest=json.loads((root/'INSTALLATION_MANIFEST_V20.json').read_text('utf8'))
for rel, digest in manifest['fichiers_sha256'].items():
    item=root/rel
    if not item.is_file() or sha256(item.read_bytes()).hexdigest()!=digest:
        raise SystemExit('V20 manifest mismatch: '+rel)

# V20.1 additive node and workflow checks.
clazz='SmartSVGLineArtV201'
assert clazz in mod.NODE_CLASS_MAPPINGS, 'V20.1: missing Line Art node'
for fname in ('SmartSVG_Studio_V20_1_LineArt_Express.json','SmartSVG_Studio_V20_1_Photo_Ecran_Exemple.json'):
    wf=json.loads((root/'example_workflows'/fname).read_text('utf8'))
    node=next((n for n in wf['nodes'] if n['type']==clazz),None)
    if node is None:raise SystemExit('V20.1: missing node in workflow '+fname)
    fields=[v for v in mod.NODE_CLASS_MAPPINGS[clazz].INPUT_TYPES()['required'] if v!='image']
    widgets=[x['name'] for x in node['inputs'] if x.get('widget')]
    if widgets!=fields or len(node['widgets_values'])!=len(fields):
        raise SystemExit('V20.1: bad workflow widgets '+fname)
    assert wf['links']==[[1,1,0,2,0,'IMAGE']]
manifest201=json.loads((root/'INSTALLATION_MANIFEST_V20_1.json').read_text('utf8'))
for rel, expected_digest in manifest201['fichiers_sha256'].items():
    f=root/rel
    if not f.is_file() or sha256(f.read_bytes()).hexdigest()!=expected_digest:
        raise SystemExit('V20.1 manifest mismatch: '+rel)
print('Package files/workflows/legacy aliases: PASS',flush=True)
proc=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-p','test_*.py','-q'],cwd=root)
if proc.returncode:sys.exit(proc.returncode)
print('SmartSVG V20.1: ALL TESTS PASS',flush=True)
