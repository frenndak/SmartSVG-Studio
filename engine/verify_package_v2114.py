"""SmartSVG V21.14 independently verifiable package, ports and regressions."""
from __future__ import annotations
import ast,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_14.json'
OLD='INSTALLATION_MANIFEST_V21_13_2.json'
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'}
TARGETED=['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs',
'test_v21112_stabilisation','test_v2112_ai','test_v21121_routing','test_v21122_batch',
'test_v2113','test_v21131','test_v21132','test_v2114']

def verify():
    doc=json.loads((ROOT/MANIFEST).read_text('utf-8'));data=doc['fichiers_sha256']
    actual={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*')
       if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert doc['version']=='21.14' and len(data)==doc['nombre_fichiers']
    assert set(actual)==set(data)|{MANIFEST},f'Fichiers incohérents : {set(actual)^(set(data)|{MANIFEST})}'
    for name,digest in data.items():
        f=actual[name]
        assert f.resolve().is_relative_to(ROOT.resolve()) and hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
    prev=json.loads((ROOT/OLD).read_text('utf-8'))['fichiers_sha256']
    changed={k for k,v in prev.items() if data.get(k)!=v}
    assert changed=={'__init__.py'},changed
    spec=importlib.util.spec_from_file_location('smartsvg2114verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    older=__import__('smartsvg2114verify.node_v21132',fromlist=['NODE_CLASS_MAPPINGS']).NODE_CLASS_MAPPINGS
    for key,value in older.items():assert mod.NODE_CLASS_MAPPINGS[key] is value,key
    assert 'SmartSVGEditableColorsV2114' in mod.NODE_CLASS_MAPPINGS
    wf=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_14_*.json'))
    assert len(wf)==1
    for f in wf:
        graph=json.loads(f.read_text('utf-8'));nodes={n['id']:n for n in graph['nodes']}
        assert len(nodes)==len(graph['nodes'])
        for n in nodes.values():
            cls=mod.NODE_CLASS_MAPPINGS.get(n['type'])
            if cls is None:assert n['type'] in ('LoadImage','PreviewImage');continue
            args=cls.INPUT_TYPES()
            fields=list(args.get('required',{}))+list(args.get('optional',{}))
            assert [i['name'] for i in n['inputs']]==fields,(f.name,n['type'])
            assert [o['type'] for o in n['outputs']]==list(cls.RETURN_TYPES),(f.name,n['type'])
        for lid,s,so,t,ti,kind in graph['links']:
            assert nodes[s]['outputs'][so]['type']==kind and nodes[t]['inputs'][ti]['type']==kind
            assert nodes[t]['inputs'][ti]['link']==lid
            assert lid in (nodes[s]['outputs'][so].get('links') or [])
    print(f'INTEGRITE OK : {len(data)} fichiers, {len(prev)-len(changed)}/{len(prev)} hérités inchangés, 1 workflow',flush=True)

def run_py(modules):
    p=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+m for m in modules)],
       cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    match=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-2400:])
    print('PYTHON OK:',match.group(1),flush=True)

def run_js():
    p=subprocess.run(['node','--test',*(str(f) for f in sorted((ROOT/'tests').glob('*.mjs')))],
       cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    match=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-2400:])
    print('JAVASCRIPT OK:',match.group(1),flush=True)

if __name__=='__main__':
    verify()
    args=sys.argv[1:]
    if '--targeted' in args:run_py(TARGETED)
    if '--javascript' in args:run_js()
    if '--suite' in args:
        i=args.index('--suite');index=int(args[i+1]);assert 1<=index<=12
        tree=ast.parse((ROOT/'verify_package_v21101.py').read_text('utf-8'))
        suites=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in n.targets))
        run_py(suites[index-1].split())
