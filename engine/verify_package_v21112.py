"""Package audit for V21.11.2. Run numerical suites independently."""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_11_2.json'
BASE='INSTALLATION_MANIFEST_V21_11_1.json'
CHANGED={'__init__.py','node_v2110.py','web/js/smartsvg_unified_v2110.js'}
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')

def integrity():
    meta=json.loads((ROOT/MANIFEST).read_text('utf8'))
    files=meta['fichiers_sha256']
    assert meta['version']=='21.11.2' and meta['nombre_fichiers']==len(files)
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert actual==set(files)|{MANIFEST},f'Fichiers inattendus : {actual^(set(files)|{MANIFEST})}'
    for rel,signature in files.items():
        f=ROOT/rel
        assert f.is_file() and not f.is_symlink() and f.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(f.read_bytes()).hexdigest()==signature,rel
    old=json.loads((ROOT/BASE).read_text('utf8'))['fichiers_sha256']
    differences={f for f in old if files.get(f)!=old[f]}
    assert differences<=CHANGED,(differences-CHANGED)
    assert not (set(old)-set(files))
    sp=importlib.util.spec_from_file_location('ss21112check',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(sp);sys.modules[sp.name]=pkg;sp.loader.exec_module(pkg)
    reg=pkg.NODE_CLASS_MAPPINGS
    from importlib import import_module
    previous=import_module('ss21112check.node_v2111').NODE_CLASS_MAPPINGS
    assert all(reg[k] is cls for k,cls in previous.items())
    names=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_11_2_*.json'))
    assert len(names)==4
    for path in names:
        graph=json.loads(path.read_text('utf8'))
        nodes={x['id']:x for x in graph['nodes']}
        assert len(nodes)==len(graph['nodes'])
        for n in nodes.values():
            cls=reg.get(n['type'])
            if cls is None:continue
            opts=cls.INPUT_TYPES();inputs=list(opts.get('required',{}))+list(opts.get('optional',{}))
            assert [x['name'] for x in n['inputs']]==inputs,(path.name,n['type'])
            assert [x['type'] for x in n['outputs']]==list(cls.RETURN_TYPES),(path.name,n['type'])
        for lid,src,so,dst,di,typ in graph['links']:
            assert nodes[src]['outputs'][so]['type']==typ and nodes[dst]['inputs'][di]['type']==typ
            assert nodes[dst]['inputs'][di]['link']==lid
            assert lid in (nodes[src]['outputs'][so].get('links') or [])
    print(f'INTEGRITE OK : {len(files)} fichiers ; {len(old)-len(differences)}/{len(old)} fichiers historiques inchangés ; 4 workflows',flush=True)

def run_py(groups):
    cmd=[sys.executable,'-m','unittest','-q',*('tests.'+x for x in groups)]
    p=subprocess.run(cmd,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=90)
    match=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-2300:])
    print('PYTHON OK :',match.group(1),flush=True)

def run_js():
    p=subprocess.run(['node','--test',*(str(x) for x in sorted((ROOT/'tests').glob('*.mjs')))],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=90)
    match=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-2300:])
    print('JAVASCRIPT OK :',match.group(1),flush=True)

def main():
    args=sys.argv[1:]
    if '--suite' in args:
        pos=args.index('--suite');idx=int(args[pos+1]);assert 1<=idx<=12
        sp=importlib.util.spec_from_file_location('old',ROOT/'verify_package_v21101.py')
        old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
        run_py(old.SUITES[idx-1].split())
    if '--python-new' in args:
        run_py(['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs','test_v21112_stabilisation'])
    if '--javascript' in args:run_js()
    integrity()

if __name__=='__main__':main()
