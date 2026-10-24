"""V21.5 verifier: packaging, legacy code, ComfyUI ports, Python + JS."""
from __future__ import annotations
import hashlib,importlib.util,json,re,subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SUITES={
 1:('test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',50),
 2:('test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 '
    'test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 '
    'test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',300),
 3:('test_v204 test_v205 test_v206 test_v21 test_v211 test_v212 '
    'test_v213 test_v2131 test_v2132 test_svg_root_v2132',227),
 4:('test_v214 test_v215',39),
}
JS_FILES=('tests/test_v215_frontend.mjs','tests/test_v215_frontend_runtime.mjs')

def integrity():
    manifest=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_5.json').read_text(encoding='utf8'))
    checks=manifest['fichiers_sha256']
    if manifest['nombre_fichiers']!=len(checks):raise SystemExit('Manifest count mismatch')
    for path,want in checks.items():
        f=ROOT/path
        if not f.is_file() or f.is_symlink() or not f.resolve().is_relative_to(ROOT.resolve()):
            raise SystemExit('Missing or unsafe file '+path)
        if hashlib.sha256(f.read_bytes()).hexdigest()!=want:
            raise SystemExit('SHA256 mismatch '+path)
    # V21.4 production modules and tests must remain untouched.
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_4.json').read_text(encoding='utf8'))
    kept=0
    for relative,want in old['fichiers_sha256'].items():
        if relative in ('__init__.py','README.md'):continue
        p=ROOT/relative
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=want:
            raise SystemExit('Unintended legacy modification '+relative)
        kept+=1
    name='smartsvg215_archived'
    spec=importlib.util.spec_from_file_location(name,ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
    if pkg.WEB_DIRECTORY!='./web/js':raise SystemExit('Frontend asset mapping missing')
    for key in ('SmartSVGExpressV214','SmartSVGInstancesV214','SmartSVGDiagnosticV214',
                'SmartSVGExpressV215','SmartSVGInstancesV215','SmartSVGDiagnosticV215'):
        if key not in pkg.NODE_CLASS_MAPPINGS:raise SystemExit('Missing node '+key)
    files=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_5_*.json'))
    if len(files)!=8:raise SystemExit('Expected eight V21.5 workflows')
    for path in files:
        data=json.loads(path.read_text(encoding='utf8'))
        nodes={x['id']:x for x in data.get('nodes',[])}
        if len(nodes)!=len(data.get('nodes',[])):raise SystemExit('Duplicate workflow nodes')
        for n in nodes.values():
            cls=pkg.NODE_CLASS_MAPPINGS.get(n['type'])
            if cls is None:continue
            fields=cls.INPUT_TYPES()
            ins=list(fields['required'])+list(fields.get('optional',{}))
            if [x['name'] for x in n['inputs']]!=ins:
                raise SystemExit('ComfyUI inputs incompatible: '+path.name)
            if [x['type'] for x in n['outputs']]!=list(cls.RETURN_TYPES):
                raise SystemExit('ComfyUI outputs incompatible: '+path.name)
            widget=[x['name'] for x in n['inputs'] if x.get('widget')]
            if len(widget)!=len(n.get('widgets_values',[])):
                raise SystemExit('Widgets_values incompatible: '+path.name)
            for k,v in zip(widget,n['widgets_values']):
                choices=fields['required'][k][0]
                if isinstance(choices,(list,tuple)) and v not in choices:
                    raise SystemExit('Invalid widget choice: '+path.name)
        for link in data.get('links',[]):
            if link[1] not in nodes or link[3] not in nodes:raise SystemExit('Dangling link')
            a,b=nodes[link[1]],nodes[link[3]]
            if link[2]>=len(a['outputs']) or link[4]>=len(b['inputs']):raise SystemExit('Bad link index')
            if a['outputs'][link[2]]['type']!=link[5] or b['inputs'][link[4]]['type']!=link[5]:
                raise SystemExit('Link type mismatch')
    print(f'Integrity OK: {len(checks)} files; {kept} V21.4 files unchanged; '
          f'{len(pkg.NODE_CLASS_MAPPINGS)} ComfyUI nodes; 8 workflows; JS exported',flush=True)


def suite(n):
    cases,count=SUITES[n]
    run=subprocess.run([sys.executable,'-m','unittest','-q',*['tests.'+x for x in cases.split()]],
                       cwd=ROOT,capture_output=True,text=True,timeout=180)
    if run.returncode:
        raise SystemExit('Unit suite failed:\n'+run.stderr[-2500:])
    match=re.search(r'Ran (\d+) tests?',run.stderr)
    if not match or int(match.group(1))!=count:
        raise SystemExit('Bad test count; '+run.stderr[-400:])
    print(f'Python suite {n}: {count} succeeded')


def javascript():
    node=shutil.which('node')
    if not node:raise SystemExit('Node.js >=18 required for JavaScript tests (not for ComfyUI runtime)')
    run=subprocess.run([node,'--test',*JS_FILES],cwd=ROOT,text=True,capture_output=True,timeout=60)
    if run.returncode:raise SystemExit('JavaScript tests failed:\n'+run.stdout[-2500:]+run.stderr[-1000:])
    match=re.search(r'^# pass (\d+)$',run.stdout,re.M)
    if not match or int(match.group(1))!=9:
        raise SystemExit('Unexpected JS pass count '+run.stdout[-600:])
    print('JavaScript tests: 9 succeeded')

if __name__=='__main__':
    integrity()
    if '--suite' in sys.argv:
        try:
            n=int(sys.argv[sys.argv.index('--suite')+1]);assert n in SUITES
        except (ValueError,IndexError,AssertionError):raise SystemExit('--suite 1, 2, 3 or 4')
        suite(n)
    elif '--javascript' in sys.argv:javascript()
    elif '--integrity-only' not in sys.argv:
        print('Run separately: --suite 1, --suite 2, --suite 3, --suite 4, --javascript')
