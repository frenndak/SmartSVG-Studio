"""Verify complete archive, legacy byte preservation, and CPU/JS tests.

Run suites separately when possible to isolate runtime/memory use.
"""
from __future__ import annotations
import hashlib, importlib.util, json, re, subprocess, sys, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SUITES={
 1:'test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',
 2:'test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',
 3:'test_v204 test_v205 test_v206 test_v21 test_v211 test_v212 test_v213 test_v2131 test_v2132 test_svg_root_v2132',
 4:'test_v214 test_v215 test_v2151',
 5:'test_v216',
}
JS_FILES=('tests/test_v215_frontend.mjs','tests/test_v215_frontend_runtime.mjs',
          'tests/test_v2151_frontend.mjs','tests/test_v2151_runtime.mjs',
          'tests/test_v216_frontend.mjs','tests/test_v216_runtime.mjs')

def integrity():
    doc=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_6.json').read_text(encoding='utf-8'))
    files=doc['fichiers_sha256']
    if doc['nombre_fichiers']!=len(files):raise SystemExit('Manifest count mismatch')
    for rel,digest in files.items():
        path=ROOT/rel
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise SystemExit('Corrupt or unsafe package file: '+rel)
    old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_5_1.json').read_text(encoding='utf-8'))
    same=0
    for rel,digest in old['fichiers_sha256'].items():
        if rel=='__init__.py':continue
        path=ROOT/rel
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise SystemExit('Existing V21.5.1 file changed: '+rel)
        same+=1
    spec=importlib.util.spec_from_file_location('smartsvg216verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    for name in ('SmartSVGMaskEditorV216','SmartSVGExpressV2151','SmartSVGInstancesV2151'):
        if name not in mod.NODE_CLASS_MAPPINGS:raise SystemExit('Missing ComfyUI node: '+name)
    paths=list((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_6_*.json'))
    if len(paths)!=2:raise SystemExit('Missing V21.6 example workflows')
    for p in paths:
        d=json.loads(p.read_text(encoding='utf-8'));nodes={n['id']:n for n in d['nodes']}
        if len(nodes)!=len(d['nodes']):raise SystemExit('Duplicate node ID')
        for n in nodes.values():
            if n['type'] not in mod.NODE_CLASS_MAPPINGS:continue
            cls=mod.NODE_CLASS_MAPPINGS[n['type']]
            names=list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
            if [inp['name'] for inp in n['inputs']]!=names:raise SystemExit('Input mismatch in '+p.name)
            if [out['type'] for out in n['outputs']]!=list(cls.RETURN_TYPES):raise SystemExit('Output mismatch in '+p.name)
        for identity,src,slot,dst,port,datatype in d['links']:
            if (src not in nodes or dst not in nodes or
                nodes[src]['outputs'][slot]['type']!=datatype or
                nodes[dst]['inputs'][port]['type']!=datatype or
                nodes[dst]['inputs'][port]['link']!=identity):raise SystemExit('Bad graph link in '+p.name)
    print(f'V21.6 integrity: {len(files)} files SHA-256 OK, {same} older files preserved, 2 workflows OK.',flush=True)

def python_suite(which):
    # Execute only one bounded suite per process (PyTorch test isolation).
    import os
    if which not in SUITES:raise SystemExit('Use --suite 1..5')
    os.chdir(ROOT)
    args=[sys.executable,'-m','unittest','-q',*['tests.'+x for x in SUITES[which].split()]]
    os.execv(sys.executable,args)

def js_tests():
    js=shutil.which('node')
    if not js:raise SystemExit('Node.js >=18 required for testing only')
    p=subprocess.run([js,'--test',*JS_FILES],cwd=ROOT,capture_output=True,text=True,timeout=90)
    m=re.search(r'^# pass (\d+)$',p.stdout,re.M)
    if p.returncode or not m or int(m.group(1))!=25:raise SystemExit(p.stdout[-4000:]+p.stderr[-500:])
    print(f'JavaScript: {m.group(1)} tests OK',flush=True)

if __name__=='__main__':
    # Keep heavyweight torch imports (used during registration verification)
    # out of the Python test subprocess launcher on constrained hosts.
    if '--suite' in sys.argv:
        try: n=int(sys.argv[sys.argv.index('--suite')+1])
        except (ValueError,IndexError): raise SystemExit('Use --suite 1..5')
        python_suite(n)
    else:
        if '--javascript' in sys.argv:js_tests()
        integrity()
    if not any(s in sys.argv for s in ('--integrity-only','--suite','--javascript')):
        print('Use --integrity-only, --suite 1..5 or --javascript')
