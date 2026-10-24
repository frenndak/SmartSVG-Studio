"""V21.13.1 clean-archive integrity, legacy mapping, workflows and tests."""
from __future__ import annotations
import ast,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_13_1.json'
OLD='INSTALLATION_MANIFEST_V21_13.json'
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
NEWTESTS=['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs',
 'test_v21112_stabilisation','test_v2112_ai','test_v21121_routing','test_v21122_batch','test_v2113','test_v21131']

def verify():
    doc=json.loads((ROOT/MANIFEST).read_text('utf8'));data=doc['fichiers_sha256']
    actual={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*') if p.is_file()
            and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert doc['version']=='21.13.1' and len(data)==doc['nombre_fichiers']
    assert set(actual)==set(data)|{MANIFEST},f'Unmatched files: {set(actual)^(set(data)|{MANIFEST})}'
    for rel,digest in data.items():
        f=actual[rel]
        assert f.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,rel
    old=json.loads((ROOT/OLD).read_text('utf8'))['fichiers_sha256']
    changes={name for name,sha in old.items() if data.get(name)!=sha}
    assert changes=={'__init__.py'},f'Legacy file modified unexpectedly: {changes}'
    assert not (set(old)-set(data))
    spec=importlib.util.spec_from_file_location('ss21131verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    legacy=__import__('ss21131verify.node_v2113',fromlist=['NODE_CLASS_MAPPINGS']).NODE_CLASS_MAPPINGS
    for name,cls in legacy.items():assert module.NODE_CLASS_MAPPINGS[name] is cls
    files=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_13_1_*.json'))
    assert len(files)==2
    for file in files:
        document=json.loads(file.read_text('utf8'));nodes={n['id']:n for n in document['nodes']}
        assert len(nodes)==len(document['nodes'])
        for n in nodes.values():
            cls=module.NODE_CLASS_MAPPINGS.get(n['type'])
            if not cls:
                assert n['type'] in ('PreviewImage','LoadImage')
                continue
            fields=cls.INPUT_TYPES()
            assert [i['name'] for i in n['inputs']]==list(fields.get('required',{}))+list(fields.get('optional',{})),(file.name,n['type'])
            assert [i['type'] for i in n['outputs']]==list(cls.RETURN_TYPES),(file.name,n['type'])
        ids=set()
        for lid,src,slot,dst,port,typ in document['links']:
            assert lid not in ids;ids.add(lid)
            assert nodes[src]['outputs'][slot]['type']==typ and nodes[dst]['inputs'][port]['type']==typ
            assert nodes[dst]['inputs'][port]['link']==lid
            assert lid in (nodes[src]['outputs'][slot].get('links') or [])
    print('INTEGRITY OK:',len(data),'files,',len(old)-len(changes),'historical unchanged,',len(files),'workflows',flush=True)

def run_python(suites):
    p=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+x for x in suites)],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    match=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-3500:])
    print('PYTHON OK:',match.group(1),flush=True)

def run_js():
    p=subprocess.run(['node','--test',*(str(x) for x in sorted((ROOT/'tests').glob('*.mjs')))],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=60)
    match=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-3500:])
    print('JAVASCRIPT OK:',match.group(1),flush=True)

if __name__=='__main__':
    args=sys.argv[1:]
    verify()
    if '--new' in args:run_python(NEWTESTS)
    if '--javascript' in args:run_js()
    if '--suite' in args:
        n=int(args[args.index('--suite')+1]);assert 1<=n<=12
        tree=ast.parse((ROOT/'verify_package_v21101.py').read_text('utf8'))
        groups=next(ast.literal_eval(item.value) for item in tree.body if isinstance(item,ast.Assign)
          and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in item.targets))
        run_python(groups[n-1].split())
