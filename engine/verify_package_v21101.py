"""V21.10 SHA-256, port/workflow checks and isolated regressions.

python verify_package_v2110.py --integrity-only
python verify_package_v2110.py --javascript
python verify_package_v2110.py --run-all
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_10_1.json'
SUITES=[
 'test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',
 'test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',
 'test_v204 test_v205 test_v206 test_v21 test_v211',
 'test_v212 test_v213 test_v2131 test_v2132 test_svg_root_v2132',
 'test_v214 test_v215 test_v2151','test_v216','test_v217','test_v2171','test_v218','test_v219','test_v2191','test_v2110'
]

def integrity():
    manifest=json.loads((ROOT/MANIFEST).read_text('utf8'))
    entries=manifest['fichiers_sha256']
    assert manifest['version']=='21.10.1' and manifest['nombre_fichiers']==len(entries)
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink()
        and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert actual==set(entries)|{MANIFEST},f'Files changed/missing: {actual ^ (set(entries)|{MANIFEST})}'
    for rel,digest in entries.items():
        path=ROOT/rel
        assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT.resolve()),rel
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,rel
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_10.json').read_text('utf8'))['fichiers_sha256']
    changed=[name for name,sha in old.items() if name not in entries or entries[name]!=sha]
    assert set(changed)=={'__init__.py','smartsvg_native/inspector.py','web/js/smartsvg_unified_v2110.js','tests/test_v2110.py','tests/test_v2110_frontend.mjs'},f'Unexpected historical modifications: {changed}'
    spec=importlib.util.spec_from_file_location('ss2110_test_package',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    mapping=module.NODE_CLASS_MAPPINGS
    for cls in ('SmartSVGUnifiedEditorV2110','SmartSVGNativeInspectorV219','SmartSVGMaskEditorV216','SmartSVGExpressV218','SmartSVGExpressV2151'):
        assert cls in mapping,cls
    assert mapping['SmartSVGExpressV218'].INPUT_TYPES()==mapping['SmartSVGExpressV2151'].INPUT_TYPES()
    for path in sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_10_*.json')):
        workflow=json.loads(path.read_text('utf8'));nodes={n['id']:n for n in workflow['nodes']}
        assert len(nodes)==len(workflow['nodes'])
        assert sum(n['type']=='SmartSVGUnifiedEditorV2110' for n in nodes.values())==1
        for n in nodes.values():
            cls=mapping.get(n['type'])
            if cls is None:continue
            actual_inputs=[x['name'] for x in n['inputs']]
            expected=list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
            assert actual_inputs==expected,(path.name,n['type'],actual_inputs,expected)
            assert [x['type'] for x in n['outputs']]==list(cls.RETURN_TYPES),(path.name,n['type'])
        for ident,src,slot,dst,port,typ in workflow['links']:
            assert src in nodes and dst in nodes
            assert nodes[src]['outputs'][slot]['type']==typ
            assert nodes[dst]['inputs'][port]['type']==typ
            assert nodes[dst]['inputs'][port]['link']==ident
            assert ident in (nodes[src]['outputs'][slot].get('links') or [])
    assert len(list((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_10_*.json')))==3
    print(f'Intégrité V21.10.1 : {len(entries)}/{len(entries)} fichiers SHA-256 ; {len(old)-len(changed)}/{len(old)} fichiers historiques inchangés ; 3 workflows',flush=True)

def run_python():
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    total=0
    for i,group in enumerate(SUITES,1):
        cmd=[sys.executable,'-m','unittest','-q',*('tests.'+t for t in group.split())]
        p=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=120)
        found=re.search(r'Ran (\d+) tests',p.stdout+p.stderr)
        if p.returncode or not found:raise RuntimeError(f'Suite {i} échouée: {(p.stdout+p.stderr)[-3000:]}')
        amount=int(found.group(1));total+=amount;print(f'Suite Python {i}/{len(SUITES)}: {amount} tests OK',flush=True)
    print(f'TOTAL PYTHON : {total} tests OK',flush=True)
    return total

def run_js():
    files=sorted((ROOT/'tests').glob('*.mjs'))
    p=subprocess.run(['node','--test',*(str(x) for x in files)],cwd=ROOT,text=True,capture_output=True,timeout=120)
    found=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not found:raise RuntimeError('JavaScript tests failed: '+(p.stdout+p.stderr)[-3000:])
    print('JavaScript :',found.group(1),'tests OK',flush=True)

if __name__=='__main__':
    integrity()
    selected=[arg for arg in sys.argv if arg.startswith('--suite')]
    if selected:
        n=int(selected[0].split('=',1)[1]) if '=' in selected[0] else int(sys.argv[sys.argv.index('--suite')+1])
        if n<1 or n>len(SUITES):raise SystemExit('Numéro de suite invalide (1..12)')
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
        group=SUITES[n-1]
        cmd=[sys.executable,'-m','unittest','-q',*('tests.'+t for t in group.split())]
        result=subprocess.run(cmd,cwd=ROOT,env=env,timeout=120)
        if result.returncode:raise SystemExit(result.returncode)
        print(f'Suite Python {n}/{len(SUITES)} terminée avec succès',flush=True)
        raise SystemExit(0)
    if '--run-all' in sys.argv:run_python();run_js()
    elif '--javascript' in sys.argv:run_js()
    elif '--integrity-only' not in sys.argv:print('Options : --integrity-only, --javascript, --run-all')
