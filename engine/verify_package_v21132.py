"""Release verification: full SHA, compatibility, workflows, tests.

Execute historical test groups one at a time to isolate numerical native-runtime stalls.
"""
from __future__ import annotations
import ast,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_13_2.json'
OLD='INSTALLATION_MANIFEST_V21_13_1.json'
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'}
CHANGED={'__init__.py','smartsvg_vector/layers_v2113.py','smartsvg_vector/qa_v21131.py','tests/test_v21131.py'}
NEWTESTS=['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs',
 'test_v21112_stabilisation','test_v2112_ai','test_v21121_routing','test_v21122_batch','test_v2113','test_v21131','test_v21132']

def verify():
    doc=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'));data=doc['fichiers_sha256']
    actual={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*')
        if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert doc['version']=='21.13.2' and len(data)==doc['nombre_fichiers']
    assert set(actual)==set(data)|{MANIFEST},f'Delta fichiers : {set(actual)^(set(data)|{MANIFEST})}'
    for name,digest in data.items():
        f=actual[name]
        assert f.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
    prev=json.loads((ROOT/OLD).read_text(encoding='utf-8'))['fichiers_sha256']
    changed={name for name,digest in prev.items() if data.get(name)!=digest}
    assert changed==CHANGED,changed^CHANGED
    assert not(set(prev)-set(data))
    spec=importlib.util.spec_from_file_location('ss21132verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pkg;spec.loader.exec_module(pkg)
    older=__import__('ss21132verify.node_v21131',fromlist=['NODE_CLASS_MAPPINGS']).NODE_CLASS_MAPPINGS
    for name,cls in older.items():assert pkg.NODE_CLASS_MAPPINGS[name] is cls
    wf=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_13_2_*.json'))
    assert len(wf)==1
    for path in wf:
        graph=json.loads(path.read_text(encoding='utf-8'))
        nodes={n['id']:n for n in graph['nodes']}
        assert len(nodes)==len(graph['nodes'])
        for item in nodes.values():
            cls=pkg.NODE_CLASS_MAPPINGS.get(item['type'])
            if cls is None:assert item['type'] in ('LoadImage','PreviewImage');continue
            ports=cls.INPUT_TYPES();expected=list(ports.get('required',{}))+list(ports.get('optional',{}))
            assert [p['name'] for p in item['inputs']]==expected,(path.name,item['type'])
            assert [p['type'] for p in item['outputs']]==list(cls.RETURN_TYPES)
        for lid,src,so,dst,di,ty in graph['links']:
            assert nodes[src]['outputs'][so]['type']==ty and nodes[dst]['inputs'][di]['type']==ty
            assert nodes[dst]['inputs'][di]['link']==lid
            assert lid in (nodes[src]['outputs'][so].get('links') or [])
    print('INTEGRITE OK:',len(data),'fichiers ;',len(prev)-len(changed),'historique inchangés ;',len(wf),'nouveau workflow')

def run_python(suites):
    p=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+m for m in suites)],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=120)
    match=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-4500:])
    print('TESTS PYTHON OK:',match.group(1))

def run_js():
    p=subprocess.run(['node','--test',*(str(f) for f in sorted((ROOT/'tests').glob('*.mjs')))],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=120)
    match=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-4500:])
    print('TESTS JAVASCRIPT OK:',match.group(1))

if __name__=='__main__':
    args=sys.argv[1:]
    verify()
    if '--new' in args:run_python(NEWTESTS)
    if '--javascript' in args:run_js()
    if '--suite' in args:
        i=args.index('--suite');index=int(args[i+1]);assert 1<=index<=12
        program=ast.parse((ROOT/'verify_package_v21101.py').read_text())
        groups=next(ast.literal_eval(x.value) for x in program.body if isinstance(x,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in x.targets))
        run_python(groups[index-1].split())
