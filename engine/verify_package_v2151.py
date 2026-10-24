"""Integrity and split test verifier for SmartSVG V21.5.1."""
from __future__ import annotations
import hashlib,importlib.util,json,re,subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SUITES={
 1:('test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',50),
 2:('test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',300),
 3:('test_v204 test_v205 test_v206 test_v21 test_v211 test_v212 test_v213 test_v2131 test_v2132 test_svg_root_v2132',227),
 4:('test_v214 test_v215 test_v2151',52),
}
JS_FILES=('tests/test_v215_frontend.mjs','tests/test_v215_frontend_runtime.mjs',
          'tests/test_v2151_frontend.mjs','tests/test_v2151_runtime.mjs')

def integrity():
    man=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_5_1.json').read_text(encoding='utf8'))
    files=man['fichiers_sha256']
    if man['nombre_fichiers']!=len(files):raise SystemExit('Manifest count mismatch')
    for name,digest in files.items():
        p=ROOT/name
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(ROOT.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise SystemExit('Bad file checksum or unsafe file: '+name)
    legacy=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_5.json').read_text(encoding='utf8'))
    preserved=0
    for rel,digest in legacy['fichiers_sha256'].items():
        if rel=='__init__.py':continue
        p=ROOT/rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise SystemExit('V21.5 legacy changed: '+rel)
        preserved+=1
    name='smartsvg2151verify'
    spec=importlib.util.spec_from_file_location(name,ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    if package.WEB_DIRECTORY!='./web/js':raise SystemExit('WEB_DIRECTORY missing')
    for key in ('SmartSVGExpressV214','SmartSVGExpressV215','SmartSVGExpressV2151',
                'SmartSVGInstancesV2151','SmartSVGDiagnosticV2151'):
        if key not in package.NODE_CLASS_MAPPINGS:raise SystemExit('Node not found '+key)
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_5_1_*.json'))
    if len(workflows)!=8:raise SystemExit('Expected 8 workflows')
    for p in workflows:
        d=json.loads(p.read_text(encoding='utf8'))
        nodes={node['id']:node for node in d['nodes']}
        if len(nodes)!=len(d['nodes']):raise SystemExit('Duplicate node ID')
        for n in nodes.values():
            cls=package.NODE_CLASS_MAPPINGS.get(n['type'])
            if cls is None:continue
            types=cls.INPUT_TYPES();ports=list(types['required'])+list(types.get('optional',{}))
            if [x['name'] for x in n['inputs']]!=ports:raise SystemExit('Input ports mismatch '+p.name)
            if [x['type'] for x in n['outputs']]!=list(cls.RETURN_TYPES):raise SystemExit('Output ports mismatch '+p.name)
            widgets=[x['name'] for x in n['inputs'] if x.get('widget')]
            if len(widgets)!=len(n.get('widgets_values',[])):raise SystemExit('Widget count mismatch '+p.name)
            for name,value in zip(widgets,n['widgets_values']):
                enum=types['required'][name][0]
                if isinstance(enum,(list,tuple)) and value not in enum:raise SystemExit('Invalid enum '+p.name)
        for l in d['links']:
            if l[1] not in nodes or l[3] not in nodes:raise SystemExit('Dangling link '+p.name)
            a,b=nodes[l[1]],nodes[l[3]]
            if l[2]>=len(a['outputs']) or l[4]>=len(b['inputs']):raise SystemExit('Link port out of range')
            if a['outputs'][l[2]]['type']!=l[5] or b['inputs'][l[4]]['type']!=l[5]:raise SystemExit('Link type error')
    print(f'Integrity OK: {len(files)} files, {preserved} old files byte-identical, 8 workflows.',flush=True)

def run_python(n):
    arg,count=SUITES[n]
    p=subprocess.run([sys.executable,'-m','unittest','-q',*['tests.'+x for x in arg.split()]],
                     cwd=ROOT,capture_output=True,text=True,timeout=180)
    if p.returncode:raise SystemExit('Tests failed: '+p.stderr[-3000:])
    m=re.search(r'Ran (\d+) tests?',p.stderr)
    if not m or int(m.group(1))!=count:raise SystemExit('Test count mismatch: '+p.stderr[-500:])
    print(f'Python suite {n}: {count} tests passed',flush=True)

def javascript():
    node=shutil.which('node')
    if not node:raise SystemExit('Node.js >=18 needed for tests only')
    p=subprocess.run([node,'--test',*JS_FILES],cwd=ROOT,capture_output=True,text=True,timeout=60)
    if p.returncode:raise SystemExit('JS failed: '+p.stdout[-2500:]+p.stderr[-1000:])
    m=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if not m or int(m.group(1))!=19:raise SystemExit('JS count mismatch: '+p.stdout[-500:])
    print('JavaScript tests: 19 passed',flush=True)

if __name__=='__main__':
    integrity()
    if '--suite' in sys.argv:
        try:n=int(sys.argv[sys.argv.index('--suite')+1]);assert n in SUITES
        except (ValueError,IndexError,AssertionError):raise SystemExit('Use --suite 1..4')
        run_python(n)
    elif '--javascript' in sys.argv:javascript()
    elif '--integrity-only' not in sys.argv:
        print('Run separately: --suite 1, 2, 3, 4 and --javascript')
