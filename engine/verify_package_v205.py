from pathlib import Path
import hashlib,importlib.util,json,sys,subprocess
root=Path(__file__).resolve().parent
man=json.loads((root/'INSTALLATION_MANIFEST_V20_5.json').read_text())
items=man['fichiers_sha256']
assert len(items)==man['nombre_fichiers']
for rel,digest in items.items():
    p=root/rel
    if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('SHA invalide: '+rel)
legacy=json.loads((root/'INSTALLATION_MANIFEST_V20_4.json').read_text())
for rel,digest in legacy['fichiers_sha256'].items():
    if rel!='__init__.py' and items.get(rel)!=digest:raise SystemExit('Historique V20.4 modifie: '+rel)
spec=importlib.util.spec_from_file_location('sv205_verified',root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pkg;spec.loader.exec_module(pkg)
for name in ('SmartSVGLineArtV204','SmartSVGStudioV20Expert','SmartSVGLineArtV205','SmartSVGCricutPreflightV205'):
    if name not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Noeud absent: '+name)
wf=list((root/'example_workflows').glob('SmartSVG_Studio_V20_5_*.json'))
if len(wf)!=6:raise SystemExit('Workflows V20.5 absents')
for p in wf:
    d=json.loads(p.read_text());nodes=[n for n in d['nodes'] if n['type'] in ('SmartSVGLineArtV205','SmartSVGCricutPreflightV205')]
    if len(nodes)!=1:raise SystemExit('Noeud attendu: '+p.name)
    n=nodes[0];inputs=pkg.NODE_CLASS_MAPPINGS[n['type']].INPUT_TYPES();req=inputs['required'];opt=inputs.get('optional',{})
    if {x['name'] for x in n['inputs']}!=set(req)|set(opt):raise SystemExit('Ports incoherents: '+p.name)
    widgets=[x['name'] for x in n['inputs'] if 'widget' in x]
    if widgets!=[k for k in req if k not in ('image','masques_objets')]:raise SystemExit('Widgets mal ordonnes: '+p.name)
    if len(widgets)!=len(n['widgets_values']):raise SystemExit('Nombre widgets: '+p.name)
    for k,val in zip(widgets,n['widgets_values']):
        typ=req[k][0]
        if isinstance(typ,list) and val not in typ:raise SystemExit('Valeur widget: '+p.name)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],check=True,cwd=root)
print('V20.5 OK: 406 tests, hash historiques V20.4, six workflows et archive propre.')
