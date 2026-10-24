"""SmartSVG 21.12.1: deterministic source/manifest, workflows, test runner."""
from __future__ import annotations
import os,sys,re,hashlib,json,subprocess,importlib.util,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_12_1.json'
BASE='INSTALLATION_MANIFEST_V21_12.json'
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')

def check():
    doc=json.loads((ROOT/MANIFEST).read_text('utf-8'))
    digest=doc['fichiers_sha256']
    assert doc['version']=='21.12.1' and len(digest)==doc['nombre_fichiers']
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert actual==set(digest)|{MANIFEST},f'Missing or extra: {actual ^ (set(digest)|{MANIFEST})}'
    for name,sha in digest.items():
        item=ROOT/name
        assert item.is_file() and not item.is_symlink()
        assert item.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(item.read_bytes()).hexdigest()==sha,name
    old=json.loads((ROOT/BASE).read_text('utf-8'))['fichiers_sha256']
    delta={name for name,sha in old.items() if digest.get(name)!=sha}
    assert delta=={'__init__.py','verify_package_v2112.py'},delta
    assert not (set(old)-set(digest))
    sp=importlib.util.spec_from_file_location('ss21121verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(sp);sys.modules[sp.name]=pkg;sp.loader.exec_module(pkg)
    previous=__import__('ss21121verify.node_v2112',fromlist=['NODE_CLASS_MAPPINGS']).NODE_CLASS_MAPPINGS
    for name,value in previous.items():assert pkg.NODE_CLASS_MAPPINGS[name] is value
    latest=pkg.NODE_CLASS_MAPPINGS
    assert len(latest['SmartSVGAutoExpressV21121'].INPUT_TYPES()['required'])==6
    assert latest['SmartSVGAutoExpressV21121'].RETURN_TYPES==latest['SmartSVGAutoExpressV2112'].RETURN_TYPES
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_12_1_*.json'))
    assert len(workflows)==5
    for wf in workflows:
        graph=json.loads(wf.read_text('utf8'))
        nodes={n['id']:n for n in graph['nodes']}
        assert len(nodes)==len(graph['nodes'])
        for n in nodes.values():
            cls=latest.get(n['type'])
            if cls is None:continue
            spec=cls.INPUT_TYPES();fields=list(spec.get('required',{}))+list(spec.get('optional',{}))
            assert [x['name'] for x in n['inputs']]==fields,(wf.name,n['type'],[x['name'] for x in n['inputs']],fields)
            assert [x['type'] for x in n['outputs']]==list(cls.RETURN_TYPES)
        links=set()
        for ident,src,srcslot,dst,dstslot,ty in graph['links']:
            assert ident not in links;links.add(ident)
            assert nodes[src]['outputs'][srcslot]['type']==ty
            assert nodes[dst]['inputs'][dstslot]['type']==ty
            assert nodes[dst]['inputs'][dstslot]['link']==ident
            assert ident in (nodes[src]['outputs'][srcslot].get('links') or [])
    print(f'INTEGRITE OK : {len(digest)} fichiers ; {len(old)-len(delta)}/{len(old)} hérités inchangés ; {len(workflows)} workflows')

def suites():
    src=ast.parse((ROOT/'verify_package_v21101.py').read_text('utf8'))
    return next(ast.literal_eval(n.value) for n in src.body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in n.targets))

def test_py(names):
    p=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+n for n in names)],
                      cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=100)
    m=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not m:raise RuntimeError((p.stdout+p.stderr)[-2500:])
    print('PYTHON OK:',m.group(1))

def test_js():
    tests=sorted((ROOT/'tests').glob('*.mjs'))
    p=subprocess.run(['node','--test',*map(str,tests)],cwd=ROOT,env=ENV,
                      capture_output=True,text=True,timeout=120)
    m=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not m:raise RuntimeError((p.stdout+p.stderr)[-2500:])
    print('JAVASCRIPT OK:',m.group(1))

if __name__=='__main__':
    args=sys.argv[1:]
    check()
    if '--new' in args:test_py(['test_v21102_global','test_v21103_audit','test_v2111',
          'test_v21111_correctifs','test_v21112_stabilisation','test_v2112_ai','test_v21121_routing'])
    if '--javascript' in args:test_js()
    if '--suite' in args:
        i=args.index('--suite');n=int(args[i+1]);
        if not 1<=n<=12:raise SystemExit('Choisir N entre 1 et 12')
        test_py(suites()[n-1].split())
