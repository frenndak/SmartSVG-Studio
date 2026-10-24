"""Self-contained V21.12 package verifier. Run suites independently."""
from __future__ import annotations
import os,sys,subprocess,json,hashlib,re,importlib.util,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_12.json'
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')

def verify_integrity():
    meta=json.loads((ROOT/MANIFEST).read_text(encoding='utf8'))
    signatures=meta['fichiers_sha256']
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
       if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert meta['version']=='21.12' and len(signatures)==meta['nombre_fichiers']
    assert actual==set(signatures)|{MANIFEST},(actual^(set(signatures)|{MANIFEST}))
    for relative,sha in signatures.items():
        f=ROOT/relative
        assert f.is_file() and not f.is_symlink() and f.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(f.read_bytes()).hexdigest()==sha,relative
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_11_2.json').read_text(encoding='utf8'))['fichiers_sha256']
    assert not (set(old)-set(signatures))
    changed={name for name,digest in old.items() if signatures.get(name)!=digest}
    assert changed=={'__init__.py'},changed
    spec=importlib.util.spec_from_file_location('ss2112verify', ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pkg;spec.loader.exec_module(pkg)
    oldreg=__import__('ss2112verify.node_v21112',fromlist=['NODE_CLASS_MAPPINGS']).NODE_CLASS_MAPPINGS
    for key,value in oldreg.items():assert pkg.NODE_CLASS_MAPPINGS[key] is value
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_12_*.json'))
    assert len(workflows)==4
    for wf in workflows:
        graph=json.loads(wf.read_text(encoding='utf8'))
        nodes={n['id']:n for n in graph['nodes']}
        assert len(nodes)==len(graph['nodes'])
        for n in nodes.values():
            cls=pkg.NODE_CLASS_MAPPINGS.get(n['type'])
            if cls is None:continue
            spec=cls.INPUT_TYPES()
            inp=list(spec.get('required',{}))+list(spec.get('optional',{}))
            assert [x['name'] for x in n['inputs']]==inp,(wf.name,n['type'],[x['name'] for x in n['inputs']],inp)
            assert [x['type'] for x in n['outputs']]==list(cls.RETURN_TYPES)
        for lid,src,so,dst,di,typ in graph['links']:
            assert nodes[src]['outputs'][so]['type']==typ
            assert nodes[dst]['inputs'][di]['type']==typ
            assert nodes[dst]['inputs'][di]['link']==lid
            assert lid in (nodes[src]['outputs'][so].get('links') or [])
    print(f'INTÉGRITÉ OK : {len(signatures)} fichiers ; {len(old)-len(changed)} historiques inchangés ; {len(workflows)} workflows')

def run_python(modules):
    cmd=[sys.executable,'-m','unittest','-q',*('tests.'+m for m in modules)]
    p=subprocess.run(cmd,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    m=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not m:raise RuntimeError((p.stdout+p.stderr)[-1800:])
    print('PYTHON OK :',m.group(1))

def run_js():
    paths=sorted(str(p) for p in (ROOT/'tests').glob('*.mjs'))
    p=subprocess.run(['node','--test',*paths],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    m=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not m:raise RuntimeError((p.stdout+p.stderr)[-2000:])
    print('JAVASCRIPT OK :',m.group(1))

def main():
    arg=sys.argv[1:]
    if '--suite' in arg:
        i=arg.index('--suite');idx=int(arg[i+1]);assert 1<=idx<=12
        tree=ast.parse((ROOT/'verify_package_v21101.py').read_text(encoding='utf8'))
        suites=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
          and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in n.targets))
        run_python(suites[idx-1].split())
    if '--quick' in arg:
        run_python(['test_v21102_global','test_v21103_audit','test_v2111',
            'test_v21111_correctifs','test_v21112_stabilisation','test_v2112_ai'])
        run_js()
    verify_integrity()

if __name__=='__main__':
    # Compatibility entry point: running an old verifier on a new package must
    # never claim the V21.12 manifest is still the canonical one.
    if (ROOT/'INSTALLATION_MANIFEST_V21_12_1.json').is_file():
        import runpy
        runpy.run_path(str(ROOT/'verify_package_v21121.py'),run_name='__main__')
    else:
        main()

