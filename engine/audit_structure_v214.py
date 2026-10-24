"""Static architecture audit. Does not import ComfyUI/PyTorch or execute models.

Usage: python audit_structure_v214.py [--json]
"""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MODULAR_PACKAGES=('smartsvg_core','smartsvg_ai','smartsvg_vector','smartsvg_cricut','smartsvg_compat')
HEAVY={'torch','cv2','PIL','numpy','transformers','diffusers','huggingface_hub'}


def analyse(root=ROOT):
    files=sorted(p for p in root.rglob('*.py') if not any(s in p.parts for s in ('tests','__pycache__')))
    modules={str(p.relative_to(root).with_suffix('')).replace('/', '.'):p for p in files}
    deps={};parse_errors=[];external=set()
    for name,p in modules.items():
        try: tree=ast.parse(p.read_text(encoding='utf8'),filename=str(p))
        except (UnicodeError,SyntaxError) as exc:
            parse_errors.append(name+':'+str(exc)[:80]);continue
        edges=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.ImportFrom):
                if n.level:
                    prefix=name.split('.')[:-1]
                    if n.level<=len(prefix)+1:
                        anchor=prefix[:len(prefix)-(n.level-1)]
                        guess='.'.join(anchor+[n.module] if n.module else anchor)
                        if guess in modules:edges.add(guess)
                elif n.module:
                    external.add(n.module.split('.')[0])
            if isinstance(n,ast.Import):
                for x in n.names:
                    target=x.name
                    if target in modules: edges.add(target)
                    else:external.add(target.split('.')[0])
        deps[name]=sorted(edges)
    packages={}
    for package in MODULAR_PACKAGES:
        members=sorted(n for n in modules if n.startswith(package+'.'))
        heavy=[]
        for n in members:
            tree=ast.parse(modules[n].read_text(encoding='utf8'))
            imports=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):imports.extend(a.name.split('.')[0] for a in node.names)
                elif isinstance(node,ast.ImportFrom) and not node.level and node.module:
                    imports.append(node.module.split('.')[0])
            if any(t in HEAVY for t in imports):heavy.append(n)
        packages[package]={'modules':len(members),'imports_heavy':heavy}
    return {
      'modules_total':len(modules),
      'historical_node_modules':len([m for m in modules if m.startswith('node_v')]),
      'historical_verifiers':len([m for m in modules if m.startswith('verify_package')]),
      'new_partition_modules':packages,
      'static_import_links':sum(map(len,deps.values())),
      'syntax_errors':parse_errors,
      'frontdoor':'node_v214.py',
      'migration':'INCREMENTALE, anciens moteurs et identifiants conservés',
      'limitations':['V21.4 ne déplace pas encore les moteurs historiques',
                     'Nœuds Legacy encore présents dans la recherche ComfyUI',
                     'CUDA / poids IA / machine Cricut non exécutés par ce rapport'],
    }

if __name__=='__main__':
    result=analyse()
    if '--json' in sys.argv: print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print('SmartSVG V21.4 — audit sans chargement IA')
        print('Modules:',result['modules_total'],'anciens nœuds:',result['historical_node_modules'])
        print('Répartition:',', '.join(f'{k}={v["modules"]}' for k,v in result['new_partition_modules'].items()))
        print('Erreurs syntaxiques:',result['syntax_errors'])
    if result['syntax_errors']:raise SystemExit(1)
