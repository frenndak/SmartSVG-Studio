"""Offline installation audit for SmartSVG V21.0."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
root=Path(__file__).resolve().parent
man=json.loads((root/'INSTALLATION_MANIFEST_V21.json').read_text(encoding='utf8'))
assert len(man['fichiers_sha256'])==man['nombre_fichiers']
for rel,digest in man['fichiers_sha256'].items():
    p=root/rel
    if not p.is_file() or p.is_symlink():raise SystemExit('Fichier manquant/symbolique: '+rel)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('SHA256 incorrect: '+rel)
old=json.loads((root/'INSTALLATION_MANIFEST_V20_6.json').read_text(encoding='utf8'))
for rel,digest in old['fichiers_sha256'].items():
    if rel=='__init__.py':continue
    if man['fichiers_sha256'].get(rel)!=digest:raise SystemExit('Fichier historique V20.6 modifie: '+rel)
name='sv21verify'
spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
for key in ('SmartSVGSimpleV206','SmartSVGSimpleV21','SmartSVGLineArtV205','SmartSVGCricutPreflightV205','SmartSVGStudioV20Expert'):
    if key not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Noeud manquant: '+key)
wf=sorted((root/'example_workflows').glob('SmartSVG_Studio_V21_*.json'))
if len(wf)!=7:raise SystemExit('7 workflows V21 requis')
req=pkg.NODE_CLASS_MAPPINGS['SmartSVGSimpleV21'].INPUT_TYPES()['required']
opt=pkg.NODE_CLASS_MAPPINGS['SmartSVGSimpleV21'].INPUT_TYPES()['optional']
for file in wf:
    data=json.loads(file.read_text(encoding='utf8'))
    nodes=[n for n in data['nodes'] if n['type']=='SmartSVGSimpleV21']
    if len(nodes)!=1:raise SystemExit('Workflow sans noeud principal: '+file.name)
    n=nodes[0]
    if [i['name'] for i in n['inputs']]!=list(req)+list(opt):raise SystemExit('Ports dans le mauvais ordre: '+file.name)
    widgets=[x for x in n['inputs'] if 'widget' in x]
    if len(widgets)!=len(n['widgets_values']) or [x['name'] for x in widgets]!=[k for k in req if k!='image']:
        raise SystemExit('Valeurs de widgets desynchronisees: '+file.name)
    for key,value in zip([i['name'] for i in widgets],n['widgets_values']):
        typ=req[key][0]
        if isinstance(typ,list) and value not in typ:raise SystemExit('Valeur de widget invalide: '+key)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],cwd=root,check=True)
print('V21 OK : SHA-256, V20.6 intact (sauf __init__), 7 workflows, tests passes')
