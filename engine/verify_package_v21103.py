"""SmartSVG V21.10.3: independently validate the distributed archive.

--integrity-only: hash exact files, legacy changes, imports and V21.10 workflows.
--suite N: one historical unittest group in a child process (N = 1..12).
--targeted: all cross-module and V21.10.3 audit tests.
--javascript: browser-model and frontend simulation tests.

Execute suites in separate commands on the target ComfyUI environment. This
avoids the intermittent numerical-runtime shutdown stalls of monolithic suites.
"""
import hashlib, importlib.util, json, os, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NAME='INSTALLATION_MANIFEST_V21_10_3.json'
CHANGED={'__init__.py','node_v2171.py','node_v2110.py',
         'smartsvg_quality/auto_hd.py','web/js/smartsvg_unified_v2110.js'}

def check_integrity():
    doc=json.loads((ROOT/NAME).read_text('utf8'))
    entries=doc['fichiers_sha256']
    assert doc['version']=='21.10.3' and doc['nombre_fichiers']==len(entries)
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert actual == set(entries)|{NAME},f'Différence paquet / manifeste : {actual ^ (set(entries)|{NAME})}'
    for rel,digest in entries.items():
        p=ROOT/rel
        assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT.resolve()),rel
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_10_2.json').read_text('utf8'))['fichiers_sha256']
    diff={k for k,v in old.items() if entries.get(k)!=v}
    assert diff==CHANGED,f'Modifications historiques inattendues : {diff ^ CHANGED}'
    spec=importlib.util.spec_from_file_location('ss21103verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    cls=module.NODE_CLASS_MAPPINGS
    for key in ('SmartSVGExpressV218','SmartSVGExpressV2151','SmartSVGUnifiedEditorV2110','SmartSVGNativeInspectorV219','SmartSVGMaskEditorV216'):
        assert key in cls,key
    assert cls['SmartSVGExpressV218'].INPUT_TYPES()==cls['SmartSVGExpressV2151'].INPUT_TYPES()
    assert cls['SmartSVGExpressV218'].RETURN_TYPES==cls['SmartSVGExpressV2151'].RETURN_TYPES
    paths=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_10_*.json'))
    assert len(paths)==3
    for path in paths:
        workflow=json.loads(path.read_text('utf8'))
        nodes={n['id']:n for n in workflow['nodes']}
        assert len(nodes)==len(workflow['nodes'])
        for n in nodes.values():
            if n['type'] not in cls:continue
            c=cls[n['type']]
            assert [v['name'] for v in n['inputs']]==list(c.INPUT_TYPES()['required'])+list(c.INPUT_TYPES().get('optional',{})),(path.name,n['type'])
            assert [v['type'] for v in n['outputs']]==list(c.RETURN_TYPES)
        for ident,src,slot,dst,port,t in workflow['links']:
            assert nodes[src]['outputs'][slot]['type']==t
            assert nodes[dst]['inputs'][port]['type']==t
            assert nodes[dst]['inputs'][port]['link']==ident
    print(f'Intégrité validée : {len(entries)} fichiers ; {len(old)-len(diff)}/{len(old)} fichiers V21.10.2 inchangés ; trois workflows',flush=True)

def run_python(files):
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    call=[sys.executable,'-m','unittest','-q',*('tests.'+f for f in files)]
    p=subprocess.run(call,cwd=ROOT,env=env,capture_output=True,text=True,timeout=150)
    match=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-3000:])
    print(f'Tests Python : {match.group(1)} réussis',flush=True)

def run_javascript():
    suite=sorted((ROOT/'tests').glob('*.mjs'))
    p=subprocess.run(['node','--test',*(str(x) for x in suite)],cwd=ROOT,text=True,capture_output=True,timeout=120)
    match=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not match:raise RuntimeError((p.stdout+p.stderr)[-3000:])
    print(f'Tests JavaScript : {match.group(1)} réussis',flush=True)

if __name__=='__main__':
    if '--suite' in sys.argv:
        i=sys.argv.index('--suite')
        if i+1>=len(sys.argv) or not sys.argv[i+1].isdigit() or not 1<=int(sys.argv[i+1])<=12:
            raise SystemExit('Utiliser --suite N où 1 <= N <= 12')
        import verify_package_v21101
        run_python(verify_package_v21101.SUITES[int(sys.argv[i+1])-1].split())
    if '--targeted' in sys.argv:
        run_python(['test_v21102_global','test_v21103_audit','test_v218','test_v2191','test_v2110','test_v2171'])
    if '--javascript' in sys.argv:run_javascript()
    check_integrity()
