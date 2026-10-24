"""V21.7.1: post-extraction integrity, native workflow contracts and split test runners."""
from __future__ import annotations
import hashlib,importlib.util,json,os,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
VERSION='21.7.1'
MANIFEST='INSTALLATION_MANIFEST_V21_7_1.json'
SUITES={
  1:'test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',
  2:'test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',
  3:'test_v204 test_v205 test_v206 test_v21 test_v211 test_v212 test_v213 test_v2131 test_v2132 test_svg_root_v2132',
  4:'test_v214 test_v215 test_v2151',
  5:'test_v216',
  6:'test_v217',
  7:'test_v2171',
}
JS_FILES=('tests/test_v215_frontend.mjs','tests/test_v215_frontend_runtime.mjs',
          'tests/test_v2151_frontend.mjs','tests/test_v2151_runtime.mjs',
          'tests/test_v216_frontend.mjs','tests/test_v216_runtime.mjs',
          'tests/test_v2161_viewport.mjs')

def integrity():
    doc=json.loads((ROOT/MANIFEST).read_text('utf-8'))
    entries=doc['fichiers_sha256']
    if doc['version']!=VERSION or doc['nombre_fichiers']!=len(entries):
        raise SystemExit('Manifest header mismatch')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    expected=set(entries)|{MANIFEST}
    if actual!=expected:
        raise SystemExit('Missing/extra files: '+repr(sorted(actual ^ expected)[:20]))
    for rel,digest in entries.items():
        file=ROOT/rel
        if file.is_symlink() or not file.resolve().is_relative_to(ROOT.resolve()):
            raise SystemExit('Unsafe file: '+rel)
        if hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
            raise SystemExit('SHA-256 mismatch: '+rel)
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_7.json').read_text('utf-8'))
    unchanged=0
    for rel,digest in old['fichiers_sha256'].items():
        if rel not in entries:raise SystemExit('Missing legacy file: '+rel)
        if entries[rel]!=digest:
            if rel != '__init__.py':raise SystemExit('Legacy file unexpectedly edited: '+rel)
        else:unchanged+=1
    spec=importlib.util.spec_from_file_location('sv2171verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    for cls in ('SmartSVGExpressV2171','SmartSVGExpressV2151','SmartSVGPrepareV217','SmartSVGQualityV217','SmartSVGMaskEditorV216'):
        if cls not in module.NODE_CLASS_MAPPINGS:raise SystemExit('Missing node: '+cls)
    cls=module.NODE_CLASS_MAPPINGS['SmartSVGExpressV2171']
    legacy=module.NODE_CLASS_MAPPINGS['SmartSVGExpressV2151']
    if cls.INPUT_TYPES()!=legacy.INPUT_TYPES() or cls.RETURN_TYPES!=legacy.RETURN_TYPES:
        raise SystemExit('Express input/output compatibility broken')
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_7_1_*.json'))
    if len(workflows)!=3:raise SystemExit('Expected 3 new V21.7.1 workflows')
    for file in workflows:
        workflow=json.loads(file.read_text('utf-8'))
        nodes={n['id']:n for n in workflow['nodes']}
        if len(nodes)!=len(workflow['nodes']) or not any(n['type']=='SmartSVGExpressV2171' for n in nodes.values()):
            raise SystemExit('Missing HD Express or duplicate id: '+file.name)
        for n in nodes.values():
            if n['type'] not in module.NODE_CLASS_MAPPINGS:continue
            typ=module.NODE_CLASS_MAPPINGS[n['type']]
            expected_inputs=list(typ.INPUT_TYPES()['required'])+list(typ.INPUT_TYPES().get('optional',{}))
            if [p['name'] for p in n['inputs']]!=expected_inputs or [o['type'] for o in n['outputs']]!=list(typ.RETURN_TYPES):
                raise SystemExit('Incompatible node port: '+file.name+' / '+n['type'])
        for ident,src,slot,dst,port,kind in workflow['links']:
            if (src not in nodes or dst not in nodes or slot>=len(nodes[src]['outputs']) or
                port>=len(nodes[dst]['inputs']) or nodes[src]['outputs'][slot]['type']!=kind or
                nodes[dst]['inputs'][port]['type']!=kind or nodes[dst]['inputs'][port]['link']!=ident or
                ident not in (nodes[src]['outputs'][slot]['links'] or [])):
                raise SystemExit('Broken workflow link: '+file.name)
    print(f'V{VERSION}: {len(entries)} SHA-256 files; {unchanged} legacy files unchanged; 3 workflows verified',flush=True)

def suite(n):
    if n not in SUITES:raise SystemExit('Choose suite 1..7')
    os.chdir(ROOT)
    os.execv(sys.executable,[sys.executable,'-m','unittest','-q',*('tests.'+x for x in SUITES[n].split())])

def javascript():
    js=shutil.which('node')
    if not js:raise SystemExit('Node.js >=18 required for JS tests')
    result=subprocess.run([js,'--test',*JS_FILES],cwd=ROOT,text=True,capture_output=True,timeout=100)
    found=re.search(r'^# pass (\d+)$',result.stdout,re.M)
    if result.returncode or not found or int(found.group(1))!=35:
        raise SystemExit(result.stdout[-4000:]+result.stderr[-2000:])
    print('JavaScript: 35 passed',flush=True)

if __name__=='__main__':
    if '--suite' in sys.argv:
        try: number=int(sys.argv[sys.argv.index('--suite')+1])
        except (ValueError,IndexError):raise SystemExit('Suite 1..7')
        suite(number)
    else:
        if '--javascript' in sys.argv:javascript()
        integrity()
        if not any(flag in sys.argv for flag in ('--integrity-only','--javascript')):
            print('Use --integrity-only, --suite 1..7 or --javascript')
