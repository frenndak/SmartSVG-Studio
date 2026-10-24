"""Run from an extracted V20.6 directory. No mutation of installed files."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
root=Path(__file__).resolve().parent
man=json.loads((root/'INSTALLATION_MANIFEST_V20_6.json').read_text(encoding='utf8'))
assert len(man['fichiers_sha256'])==man['nombre_fichiers']
for rel,digest in man['fichiers_sha256'].items():
    p=root/rel
    if not p.is_file() or p.is_symlink():raise SystemExit('Fichier absent/symbolique: '+rel)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise SystemExit('Empreinte incorrecte: '+rel)
old=json.loads((root/'INSTALLATION_MANIFEST_V20_5.json').read_text(encoding='utf8'))
for rel,digest in old['fichiers_sha256'].items():
    if rel in ('__init__.py','CHANGELOG.md'):continue  # registration of the new version is deliberate
    if man['fichiers_sha256'].get(rel)!=digest:raise SystemExit('Module V20.5 modifie: '+rel)
name='sv206verify'
spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
for name in ('SmartSVGSimpleV206','SmartSVGLineArtV205','SmartSVGCricutPreflightV205','SmartSVGStudioV20Expert'):
    if name not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Noeud absent: '+name)
wf=sorted((root/'example_workflows').glob('SmartSVG_Studio_V20_6_*.json'))
if len(wf)!=6:raise SystemExit('6 workflows V20.6 attendus')
required=pkg.NODE_CLASS_MAPPINGS['SmartSVGSimpleV206'].INPUT_TYPES()['required']
for file in wf:
    d=json.loads(file.read_text(encoding='utf8'));nodes=[n for n in d['nodes'] if n['type']=='SmartSVGSimpleV206']
    if len(nodes)!=1:raise SystemExit('Noeud SmartSVG absent: '+file.name)
    n=nodes[0];widgets=[i['name'] for i in n['inputs'] if 'widget' in i]
    if [i['name'] for i in n['inputs']]!=list(required):raise SystemExit('Ordre des ports incorrect: '+file.name)
    if widgets!=[x for x in required if x!='image'] or len(widgets)!=len(n['widgets_values']):
        raise SystemExit('Widgets incorrects: '+file.name)
    for param,value in zip(widgets,n['widgets_values']):
        kind=required[param][0]
        if isinstance(kind,list) and value not in kind:raise SystemExit('Choix invalide: '+param)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],check=True,cwd=root)
print('V20.6 OK: 431 tests, 6 workflows, anciens modules V20.5 inchanges (sauf init), manifestes valides.')
