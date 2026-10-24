"""Re-extracted SmartSVG V21.13 package verification and regression launcher."""
from __future__ import annotations
import ast,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_13.json'
PREV='INSTALLATION_MANIFEST_V21_12_2.json'
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')

def verify():
    meta=json.loads((ROOT/MANIFEST).read_text('utf8'));sha=meta['fichiers_sha256']
    assert meta['version']=='21.13' and meta['nombre_fichiers']==len(sha)
    actual={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink()
           and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert set(actual)==set(sha)|{MANIFEST},set(actual)^(set(sha)|{MANIFEST})
    for rel,digest in sha.items():
        p=actual[rel]
        assert p.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
    older=json.loads((ROOT/PREV).read_text('utf8'))['fichiers_sha256']
    changes={name for name,sha_ in older.items() if sha.get(name)!=sha_}
    assert changes=={'__init__.py'},changes
    assert not (set(older)-set(sha))
    spec=importlib.util.spec_from_file_location('ssv2113verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    package=importlib.util.module_from_spec(spec);sys.modules[spec.name]=package;spec.loader.exec_module(package)
    from importlib import import_module
    prev=import_module('ssv2113verify.node_v21122').NODE_CLASS_MAPPINGS
    assert all(package.NODE_CLASS_MAPPINGS.get(k) is v for k,v in prev.items())
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_13_*.json'))
    assert len(workflows)==2
    for path in workflows:
        w=json.loads(path.read_text('utf8')); nodes={n['id']:n for n in w['nodes']}
        assert len(nodes)==len(w['nodes'])
        for node in w['nodes']:
            cls=package.NODE_CLASS_MAPPINGS.get(node['type'])
            if cls is None:continue
            options=cls.INPUT_TYPES();fields=list(options.get('required',{}))+list(options.get('optional',{}))
            assert [x['name'] for x in node['inputs']]==fields,(path.name,node['type'])
            assert [o['type'] for o in node['outputs']]==list(cls.RETURN_TYPES)
        for ident,src,slot,dst,port,kind in w['links']:
            assert nodes[src]['outputs'][slot]['type']==kind
            assert nodes[dst]['inputs'][port]['type']==kind
            assert nodes[dst]['inputs'][port]['link']==ident
            assert ident in (nodes[src]['outputs'][slot].get('links') or [])
    print(f'INTEGRITE OK : {len(sha)} fichiers, {len(older)-len(changes)}/{len(older)} fichiers historiques inchangés, 2 workflows')

def run_py(names):
    r=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+x for x in names)],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=105)
    count=re.search(r'Ran (\d+) tests',r.stdout+r.stderr)
    if r.returncode or not count:raise RuntimeError((r.stderr+r.stdout)[-3000:])
    print(f'PYTHON OK : {count.group(1)} tests')

def run_js():
    r=subprocess.run(['node','--test',*(str(p) for p in sorted((ROOT/'tests').glob('*.mjs')))],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=90)
    count=re.search(r'^# pass (\d+)$',r.stdout,re.M)
    if r.returncode or not count:raise RuntimeError((r.stdout+r.stderr)[-2500:])
    print(f'JAVASCRIPT OK : {count.group(1)} tests')

if __name__=='__main__':
    args=sys.argv[1:];verify()
    if '--new' in args:run_py(['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs',
        'test_v21112_stabilisation','test_v2112_ai','test_v21121_routing','test_v21122_batch','test_v2113'])
    if '--javascript' in args:run_js()
    if '--suite' in args:
        idx=args.index('--suite');n=int(args[idx+1]);assert 1<=n<=12
        tree=ast.parse((ROOT/'verify_package_v21101.py').read_text('utf8'))
        groups=next(ast.literal_eval(item.value) for item in tree.body if isinstance(item,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in item.targets))
        run_py(groups[n-1].split())
