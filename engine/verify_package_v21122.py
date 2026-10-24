"""V21.12.2 package verifier: exact SHA-256 manifest and safe regression runners."""
import ast,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_12_2.json'
OLD='INSTALLATION_MANIFEST_V21_12_1.json'
CHANGED={'__init__.py','multi_subject_v21.py','production_v211.py',
         'web/js/smartsvg_steps_v21112.js','tests/test_v21112_steps.mjs'}
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')

def verify():
    info=json.loads((ROOT/MANIFEST).read_text(encoding='utf8'));sha=info['fichiers_sha256']
    assert info['version']=='21.12.2' and info['nombre_fichiers']==len(sha)
    actual={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink()
            and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert set(actual)==set(sha)|{MANIFEST},f'Paquet incomplet / surplus : {set(actual)^(set(sha)|{MANIFEST})}'
    for name,digest in sha.items():
        p=actual[name]
        assert p.resolve().is_relative_to(ROOT.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
    previous=json.loads((ROOT/OLD).read_text(encoding='utf8'))['fichiers_sha256']
    changed={name for name,h in previous.items() if sha.get(name)!=h}
    assert changed==CHANGED, f'Modifications historiques inattendues : {changed^CHANGED}'
    assert not (set(previous)-set(sha))
    spec=importlib.util.spec_from_file_location('sverify21122', ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pkg;spec.loader.exec_module(pkg)
    from importlib import import_module
    legacy=import_module('sverify21122.node_v21121').NODE_CLASS_MAPPINGS
    for name,klass in legacy.items():assert pkg.NODE_CLASS_MAPPINGS[name] is klass,name
    cls=pkg.NODE_CLASS_MAPPINGS['SmartSVGAutoExpressV21122']
    parent=pkg.NODE_CLASS_MAPPINGS['SmartSVGAutoExpressV21121']
    assert list(cls.INPUT_TYPES()['required'])==list(parent.INPUT_TYPES()['required'])
    assert list(cls.INPUT_TYPES()['optional'])==list(parent.INPUT_TYPES()['optional'])
    assert cls.RETURN_TYPES==parent.RETURN_TYPES
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_12_2_*.json'))
    assert len(workflows)==5
    for path in workflows:
        workflow=json.loads(path.read_text(encoding='utf8'))
        nodes={n['id']:n for n in workflow['nodes']};assert len(nodes)==len(workflow['nodes'])
        links=set()
        for n in nodes.values():
            node=pkg.NODE_CLASS_MAPPINGS.get(n['type'])
            if node is None:continue
            spec=node.INPUT_TYPES()
            fields=list(spec.get('required',{}))+list(spec.get('optional',{}))
            assert [x['name'] for x in n['inputs']]==fields,(path.name,n['type'],fields)
            assert [x['type'] for x in n['outputs']]==list(node.RETURN_TYPES),(path.name,n['type'])
        for ident,src,so,dst,di,typ in workflow['links']:
            assert ident not in links;links.add(ident)
            assert nodes[src]['outputs'][so]['type']==typ and nodes[dst]['inputs'][di]['type']==typ
            assert nodes[dst]['inputs'][di]['link']==ident
            assert ident in (nodes[src]['outputs'][so].get('links') or [])
    print(f'INTEGRITE OK : {len(sha)} fichiers ; {len(previous)-len(changed)} anciens fichiers inchangés ; 5 workflows')

def tests(names):
    out=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+name for name in names)],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    found=re.search(r'Ran (\d+) tests',out.stderr+out.stdout)
    if out.returncode or not found:raise RuntimeError((out.stderr+out.stdout)[-1600:])
    print('PYTHON OK :',found.group(1))

def javascript():
    out=subprocess.run(['node','--test',*(str(f) for f in sorted((ROOT/'tests').glob('*.mjs')))],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    found=re.search(r'^# pass (\d+)$',out.stdout,re.M)
    if out.returncode or not found:raise RuntimeError((out.stderr+out.stdout)[-1600:])
    print('JAVASCRIPT OK :',found.group(1))

if __name__=='__main__':
    arguments=sys.argv[1:];verify()
    if '--new' in arguments:
        tests(['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs','test_v21112_stabilisation','test_v2112_ai','test_v21121_routing','test_v21122_batch'])
    if '--javascript' in arguments:javascript()
    if '--suite' in arguments:
        ix=arguments.index('--suite');n=int(arguments[ix+1]);assert 1<=n<=12
        tree=ast.parse((ROOT/'verify_package_v21101.py').read_text('utf8'))
        groups=next(ast.literal_eval(a.value) for a in tree.body if isinstance(a,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUITES' for t in a.targets))
        tests(groups[n-1].split())
