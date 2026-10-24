"""Authoritative V20.4 package integrity + workflow and full test verification."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

root=Path(__file__).resolve().parent
man=json.loads((root/'INSTALLATION_MANIFEST_V20_4.json').read_text(encoding='utf8'))
items=man['fichiers_sha256']
if len(items)!=man['nombre_fichiers']:raise SystemExit('Nombre fichiers incorrect')
for rel,digest in items.items():
    p=root/rel
    if (not p.is_file() or p.is_symlink() or
        hashlib.sha256(p.read_bytes()).hexdigest()!=digest):
        raise SystemExit('Signature invalide: '+rel)
legacy=json.loads((root/'INSTALLATION_MANIFEST_V20_3.json').read_text(encoding='utf8'))
for rel,digest in legacy['fichiers_sha256'].items():
    if rel=='__init__.py':continue
    if rel not in items or digest!=items[rel]:
        raise SystemExit('Module historique V20.3 modifie: '+rel)

spec=importlib.util.spec_from_file_location('smartsvg_v204_verified',root/'__init__.py',
                                            submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=pkg
spec.loader.exec_module(pkg)
for name in ['SmartSVGLineArtV203','SmartSVGGPUPreflightV203',
             'SmartSVGLineArtV204','SmartSVGMaskQualityV204','SmartSVGStudioV20Expert']:
    if name not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Noeud disparu: '+name)
workflows=list((root/'example_workflows').glob('SmartSVG_Studio_V20_4_*.json'))
if len(workflows)!=6:raise SystemExit('Nombre workflow V20.4 invalide')
for wf in workflows:
    data=json.loads(wf.read_text(encoding='utf-8'))
    nodes=[n for n in data['nodes'] if n['type'] in ('SmartSVGLineArtV204','SmartSVGMaskQualityV204')]
    if len(nodes)!=1:raise SystemExit('Noeud V20.4 manquant: '+wf.name)
    node=nodes[0];cls=pkg.NODE_CLASS_MAPPINGS[node['type']]
    decl=cls.INPUT_TYPES()
    req=decl['required'];opt=decl.get('optional',{})
    declared=set(req)|set(opt)
    inputs={x['name'] for x in node['inputs']}
    if inputs!=declared:raise SystemExit('Ports incoherents: '+wf.name)
    names=[x['name'] for x in node['inputs'] if x.get('widget')]
    expected=[x for x in req if x not in ('image','masques_objets')]
    if names!=expected or len(names)!=len(node['widgets_values']):
        raise SystemExit('Widgets non synchronises: '+wf.name)
    for name,val in zip(names,node['widgets_values']):
        spec=req[name][0]
        if isinstance(spec,(list,tuple)) and val not in spec:
            raise SystemExit('Valeur widget invalide: '+wf.name+':'+name)
    linkids={x[0] for x in data['links']}
    if len(linkids)!=len(data['links']):raise SystemExit('Liens dupliques: '+wf.name)
    for inp in node['inputs']:
        if inp['link'] is not None and inp['link'] not in linkids:
            raise SystemExit('Lien entree invalide: '+wf.name)

subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],
               check=True,cwd=root)
print('V20.4 OK: manifeste SHA256, conservation historique V20.3, nœuds, 6 workflows et tests.')
