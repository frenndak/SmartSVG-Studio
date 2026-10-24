"""V21.7 independent integrity, non-regression and separated CPU/UI test runners."""
from __future__ import annotations
import hashlib,importlib.util,json,os,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SUITES={
 1:'test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',
 2:'test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',
 3:'test_v204 test_v205 test_v206 test_v21 test_v211 test_v212 test_v213 test_v2131 test_v2132 test_svg_root_v2132',
 4:'test_v214 test_v215 test_v2151',
 5:'test_v216',
 6:'test_v217',
}
JS_FILES=('tests/test_v215_frontend.mjs','tests/test_v215_frontend_runtime.mjs',
          'tests/test_v2151_frontend.mjs','tests/test_v2151_runtime.mjs',
          'tests/test_v216_frontend.mjs','tests/test_v216_runtime.mjs',
          'tests/test_v2161_viewport.mjs')


def integrity():
    doc=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_7.json').read_text('utf-8'))
    files=doc['fichiers_sha256']
    if doc['version']!='21.7' or doc['nombre_fichiers']!=len(files):
        raise SystemExit('Manifest header invalid')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    expected=set(files)|{'INSTALLATION_MANIFEST_V21_7.json'}
    if actual!=expected:raise SystemExit('Missing/extra package files: '+repr(sorted(actual^expected)[:20]))
    for name,digest in files.items():
        p=ROOT/name
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise SystemExit('Corrupted file: '+name)
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_6_1.json').read_text('utf-8'))
    unchanged=0
    for name,hashcode in old['fichiers_sha256'].items():
        if name not in files:raise SystemExit('Missing legacy file: '+name)
        if files[name]!=hashcode:
            if name!='__init__.py':raise SystemExit('Unexpected historical modification: '+name)
        else:unchanged+=1
    spec=importlib.util.spec_from_file_location('sv217verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    for name in ('SmartSVGPrepareV217','SmartSVGQualityV217','SmartSVGMaskEditorV216','SmartSVGExpressV2151'):
        if name not in module.NODE_CLASS_MAPPINGS:raise SystemExit('Missing class: '+name)
    paths=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_7_*.json'))
    if len(paths)!=3:raise SystemExit('Expected 3 V21.7 workflows')
    for p in paths:
        doc=json.loads(p.read_text(encoding='utf-8'))
        nodes={n['id']:n for n in doc['nodes']}
        if len(nodes)!=len(doc['nodes']):raise SystemExit('Duplicate workflow node ID')
        for n in nodes.values():
            if n['type'] not in module.NODE_CLASS_MAPPINGS:continue
            cls=module.NODE_CLASS_MAPPINGS[n['type']]
            contract=list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
            if [port['name'] for port in n['inputs']]!=contract or [out['type'] for out in n['outputs']]!=list(cls.RETURN_TYPES):
                raise SystemExit('Workflow node contract mismatch: '+p.name+' '+n['type'])
        for ident,src,slot,dst,port,kind in doc['links']:
            if (src not in nodes or dst not in nodes or
                nodes[src]['outputs'][slot]['type']!=kind or nodes[dst]['inputs'][port]['type']!=kind or
                nodes[dst]['inputs'][port]['link']!=ident or ident not in (nodes[src]['outputs'][slot]['links'] or [])):
                raise SystemExit('Broken link: '+p.name)
    print(f'V21.7 SHA-256: {len(files)} files; {unchanged} historic files unchanged; 3 workflows valid',flush=True)


def suite(n):
    if n not in SUITES:raise SystemExit('Choose suite 1..6')
    os.chdir(ROOT)
    os.execv(sys.executable,[sys.executable,'-m','unittest','-q',*('tests.'+k for k in SUITES[n].split())])


def javascript():
    js=shutil.which('node')
    if not js:raise SystemExit('Node.js >=18 required for JS tests')
    result=subprocess.run([js,'--test',*JS_FILES],cwd=ROOT,text=True,capture_output=True,timeout=100)
    found=re.search(r'^# pass (\d+)$',result.stdout,re.M)
    if result.returncode or not found or int(found.group(1))!=35:
        raise SystemExit(result.stdout[-4000:]+result.stderr[-2000:])
    print('JavaScript: 35 tests passed',flush=True)

if __name__=='__main__':
    if '--suite' in sys.argv:
        try:n=int(sys.argv[sys.argv.index('--suite')+1])
        except (ValueError,IndexError):raise SystemExit('Suite 1..6 required')
        suite(n)
    else:
        if '--javascript' in sys.argv:javascript()
        integrity()
        if not any(flag in sys.argv for flag in ('--integrity-only','--javascript')):
            print('Use --integrity-only, --suite 1..6 or --javascript')
