"""V21.15 package SHA verification + non-regression suites.

Usage: python verify_package_v2115.py --integrity --targeted --javascript
       python verify_package_v2115.py --full
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
LATEST='INSTALLATION_MANIFEST_V21_15.json'
BASE='INSTALLATION_MANIFEST_V21_14_1.json'
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1',
     'MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'}


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integrity():
    current=json.loads((ROOT/LATEST).read_text(encoding='utf-8'))
    legacy=json.loads((ROOT/BASE).read_text(encoding='utf-8'))
    mapping=current['fichiers_sha256']
    present={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*')
             if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert current['version']=='21.15.0'
    assert set(present)==set(mapping)|{LATEST}, 'Fichiers ajoutés/supprimés non manifestés'
    assert len(mapping)==current['nombre_fichiers']
    for filename,digest in mapping.items():
        assert sha(present[filename])==digest,filename
    changed={name for name,digest in legacy['fichiers_sha256'].items()
             if mapping.get(name)!=digest}
    assert changed=={'__init__.py'},f'Altération de la baseline historique : {changed}'
    assert current['baseline_b0_zip_sha256']=='b35ed631bcf6243bf0dd9b0af5b8e01dab1cfe38a5ef0f93e74f21a49df28835'
    print(f'INTEGRITE OK : {len(mapping)} fichiers hashés, baseline inchangée hormis point d’entrée',flush=True)


def run_process(args,kind):
    p=subprocess.run(args,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=240)
    out=p.stdout+'\n'+p.stderr
    if p.returncode:raise RuntimeError(f'{kind} ERREUR : '+out[-4500:])
    if kind=='PYTHON':
        count=re.search(r'Ran (\d+) tests',out)
    else:
        count=re.search(r'^# pass (\d+)$',out,re.M)
    if not count:raise RuntimeError(f'{kind} sans décompte de tests : '+out[-2500:])
    print(f'{kind} OK: {count.group(1)}',flush=True)


def main():
    parser=argparse.ArgumentParser()
    for flag in ('integrity','targeted','javascript','full'):
        parser.add_argument('--'+flag,action='store_true')
    args=parser.parse_args()
    integrity()
    if args.targeted:
        run_process([sys.executable,'-m','unittest','-q','tests.test_v2115_governance',
            'tests.test_v21141_color','tests.test_v2114','tests.test_v21131','tests.test_v21132'],'PYTHON')
    if args.full:
        run_process([sys.executable,'-m','unittest','discover','-s','tests', '-p','test_*.py','-q'],'PYTHON')
    if args.javascript:
        run_process(['node','--test',*(str(p) for p in sorted((ROOT/'tests').glob('*.mjs')))],'JAVASCRIPT')

if __name__=='__main__':main()
