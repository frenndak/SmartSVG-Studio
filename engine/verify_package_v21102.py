"""V21.10.2 post-extraction integrity, graph contracts, targeted and full tests."""
import hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_10_2.json'
CHANGED={'__init__.py','node_v218.py','smartsvg_cricut/direct_import_v218.py',
         'web/js/smartsvg_unified_v2110.js','tests/test_v2110_frontend.mjs','tests/test_v2191.py'}
def integrity():
    doc=json.loads((ROOT/MANIFEST).read_text('utf8'))
    entries=doc['fichiers_sha256']
    assert doc['version']=='21.10.2' and doc['nombre_fichiers']==len(entries)
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert actual==set(entries)|{MANIFEST},f'Invalid package contents: {actual ^ (set(entries)|{MANIFEST})}'
    for rel,digest in entries.items():
        p=ROOT/rel; assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_10_1.json').read_text('utf8'))['fichiers_sha256']
    diff={k for k,v in old.items() if entries.get(k)!=v}
    assert diff==CHANGED,f'Unplanned historical edits: {diff ^ CHANGED}'
    spec=importlib.util.spec_from_file_location('ss21102audit',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    mapping=module.NODE_CLASS_MAPPINGS
    for cls in ('SmartSVGUnifiedEditorV2110','SmartSVGNativeInspectorV219','SmartSVGMaskEditorV216','SmartSVGExpressV218','SmartSVGExpressV2151'):
        assert cls in mapping
    assert mapping['SmartSVGExpressV218'].INPUT_TYPES()==mapping['SmartSVGExpressV2151'].INPUT_TYPES()
    assert mapping['SmartSVGExpressV218'].RETURN_TYPES==mapping['SmartSVGExpressV2151'].RETURN_TYPES
    workflows=list((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_10_*.json'))
    assert len(workflows)==3
    for path in workflows:
        w=json.loads(path.read_text('utf8'));nodes={n['id']:n for n in w['nodes']}
        assert len(nodes)==len(w['nodes'])
        for n in nodes.values():
            cls=mapping.get(n['type'])
            if cls is not None:
                assert [x['name'] for x in n['inputs']]==list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
                assert [o['type'] for o in n['outputs']]==list(cls.RETURN_TYPES)
        for ident,src,slot,dst,port,kind in w['links']:
            assert nodes[src]['outputs'][slot]['type']==kind
            assert nodes[dst]['inputs'][port]['type']==kind
            assert nodes[dst]['inputs'][port]['link']==ident
    print(f'OK SHA-256 : {len(entries)} fichiers ; {len(old)-len(diff)} fichiers V21.10.1 inchangés ; 3 workflows',flush=True)
def run_group(files):
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    cmd=[sys.executable,'-m','unittest','-q',*('tests.'+s for s in files)]
    p=subprocess.run(cmd,cwd=ROOT,env=env,encoding='utf8',capture_output=True,timeout=150)
    found=re.search(r'Ran (\d+) tests',p.stderr+p.stdout)
    if p.returncode or not found:raise RuntimeError((p.stdout+p.stderr)[-3000:])
    print(f'Python {found.group(1)} tests : OK',flush=True)
    return int(found.group(1))
def js():
    files=sorted((ROOT/'tests').glob('*.mjs'))
    p=subprocess.run(['node','--test',*(str(f) for f in files)],cwd=ROOT,encoding='utf8',capture_output=True,timeout=120)
    found=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not found:raise RuntimeError((p.stdout+p.stderr)[-2000:])
    print(f'JavaScript {found.group(1)} tests : OK',flush=True)
def main():
    # Test suites are launched one at a time, each in a fresh verifier process.
    # A monolithic runner has shown intermittent stalls with numerical runtimes.
    if '--run-all' in sys.argv:
        raise SystemExit('Lancement groupe indisponible : utiliser --suite N (N=1..12) séparément puis --targeted et --javascript.')
    if '--suite' in sys.argv or any(a.startswith('--suite=') for a in sys.argv):
        selected=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--suite=')),None)
        if selected is None:
            idx=sys.argv.index('--suite');selected=sys.argv[idx+1] if idx+1<len(sys.argv) else ''
        if not selected.isdigit() or not 1<=int(selected)<=12:
            raise SystemExit('Suite invalide : utiliser --suite N (N=1..12)')
        import verify_package_v21101 as old
        run_group(old.SUITES[int(selected)-1].split())
    if '--javascript' in sys.argv:js()
    if '--targeted' in sys.argv:run_group(['test_v21102_global','test_v218','test_v2191','test_v2110'])
    integrity()
if __name__=='__main__':main()
