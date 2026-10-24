"""SmartSVG V21.4: integrity + exact historical hashes + ComfyUI workflow ports.

Usage: python verify_package_v214.py --integrity-only
       python verify_package_v214.py --suite 1 (then 2, 3, 4)
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_4.json'
SUITES={
  1:('test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',50),
  2:('test_v19 test_v191 test_v192 test_v193 test_v194 test_v195 test_v1951 '
     'test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 '
     'test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',300),
  3:('test_v204 test_v205 test_v206 test_v21 test_v211 test_v212 '
     'test_v213 test_v2131 test_v2132 test_svg_root_v2132',227),
  4:('test_v214',20),
}

def verify_files():
    m=json.loads((ROOT/MANIFEST).read_text(encoding='utf8'))
    hashes=m['fichiers_sha256']
    if len(hashes)!=m['nombre_fichiers']:
        raise SystemExit('MANIFEST compte incorrect')
    for relative,wanted in hashes.items():
        p=ROOT/relative
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(ROOT.resolve()):
            raise SystemExit('Fichier manquant/interdit : '+relative)
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if h!=wanted:raise SystemExit('SHA-256 incorrect : '+relative)
    # The new layers are additive. The old implementation is bit-for-bit intact.
    legacy=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_3_2.json').read_text(encoding='utf8'))
    preserved=0
    for relative,wanted in legacy['fichiers_sha256'].items():
        if relative=='__init__.py':continue
        p=ROOT/relative
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=wanted:
            raise SystemExit('RÉGRESSION historique : '+relative)
        preserved+=1
    return len(hashes),preserved


def verify_registry_and_workflows():
    name='smartsvg214_from_archive'
    spec=importlib.util.spec_from_file_location(name,ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(spec)
    sys.modules[name]=pkg
    spec.loader.exec_module(pkg)
    current=('SmartSVGExpressV214','SmartSVGInstancesV214','SmartSVGDiagnosticV214')
    for key in current:
        if key not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Nœud absent : '+key)
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_4_*.json'))
    if len(workflows)!=8:raise SystemExit('V21.4 doit fournir 8 workflows')
    for wf in workflows:
        a=json.loads(wf.read_text(encoding='utf8'))
        nodes={x['id']:x for x in a.get('nodes',[])}
        if len(nodes)!=len(a['nodes']):raise SystemExit('ID doublon : '+wf.name)
        for x in a['nodes']:
            cls=pkg.NODE_CLASS_MAPPINGS.get(x['type'])
            if cls is None:continue   # Built-in ComfyUI nodes such as LoadImage
            spec2=cls.INPUT_TYPES()
            ports=list(spec2['required'])+list(spec2.get('optional',{}))
            if [p['name'] for p in x.get('inputs',[])]!=ports:
                raise SystemExit('Entrées incompatibles : '+wf.name)
            if [p['type'] for p in x.get('outputs',[])]!=list(cls.RETURN_TYPES):
                raise SystemExit('Sorties incompatibles : '+wf.name)
            widget_names=[i['name'] for i in x['inputs'] if i.get('widget')]
            if len(widget_names)!=len(x.get('widgets_values',[])):
                raise SystemExit('Widgets incompatibles : '+wf.name)
            for field,value in zip(widget_names,x['widgets_values']):
                entry=spec2['required'].get(field,('',))
                choices=entry[0]
                if isinstance(choices,(list,tuple)) and value not in choices:
                    raise SystemExit(f'Option invalide {field} dans {wf.name}')
        for link in a.get('links',[]):
            if link[1] not in nodes or link[3] not in nodes:
                raise SystemExit('Lien sans nœud : '+wf.name)
            l=nodes[link[1]];r=nodes[link[3]]
            if link[2]>=len(l.get('outputs',[])) or link[4]>=len(r.get('inputs',[])):
                raise SystemExit('Index de lien invalide : '+wf.name)
            if l['outputs'][link[2]]['type']!=link[5] or r['inputs'][link[4]]['type']!=link[5]:
                raise SystemExit('Type de lien invalide : '+wf.name)
    return len(pkg.NODE_CLASS_MAPPINGS),len(workflows)


def run_suite(n):
    names,expected=SUITES[n]
    cmd=[sys.executable,'-m','unittest','-q',*('tests.'+x for x in names.split())]
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=180)
    if result.returncode:
        raise SystemExit('Échec des tests : '+result.stderr[-3500:])
    match=re.search(r'Ran (\d+) tests?',result.stderr)
    if match is None or int(match.group(1))!=expected:
        raise SystemExit(f'Comptage attendu {expected}, reçu {result.stderr[-500:]}')
    print(f'V21.4 — famille {n}: {expected} tests OK')
    return expected

if __name__=='__main__':
    count,preserved=verify_files()
    node_count,wf_count=verify_registry_and_workflows()
    print(f'V21.4 : {count} fichiers vérifiés, {preserved} historiques inchangés, '
          f'{node_count} identifiants ComfyUI, {wf_count} workflows.',flush=True)
    if '--suite' in sys.argv:
        try:chosen=int(sys.argv[sys.argv.index('--suite')+1]);assert chosen in SUITES
        except (ValueError,IndexError,AssertionError):raise SystemExit('Choisir --suite 1, 2, 3 ou 4')
        run_suite(chosen)
    elif '--integrity-only' not in sys.argv:
        print('Pour les 597 tests : répéter --suite 1, puis 2, 3 et 4.')
