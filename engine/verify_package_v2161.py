"""SmartSVG V21.6.1 package integrity, legacy compatibility and isolated test runners."""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys
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
          'tests/test_v216_frontend.mjs','tests/test_v216_runtime.mjs',
          'tests/test_v2161_viewport.mjs')
ALLOWED_CHANGES={
 'web/js/smartsvg_editor_v216.js',
 'web/js/smartsvg_editor_model_v216.mjs',
 'tests/test_v216_runtime.mjs',
}

def integrity():
    doc=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_6_1.json').read_text(encoding='utf-8'))
    files=doc['fichiers_sha256']
    if doc['version']!='21.6.1' or doc['nombre_fichiers']!=len(files):
        raise SystemExit('Invalid manifest header or count')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    expected=set(files)|{'INSTALLATION_MANIFEST_V21_6_1.json'}
    if expected!=actual:raise SystemExit(f'Missing/extra archive files: {sorted(expected^actual)[:20]}')
    for rel,digest in files.items():
        path=ROOT/rel
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise SystemExit('Corrupt or unsafe package file: '+rel)
    older=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_6.json').read_text(encoding='utf-8'))
    changed=set()
    for rel,digest in older['fichiers_sha256'].items():
        if rel not in files:raise SystemExit('Legacy file missing: '+rel)
        if files[rel]!=digest:changed.add(rel)
    if changed!=ALLOWED_CHANGES:raise SystemExit('Unexpected V21.6 changes: '+repr(changed^ALLOWED_CHANGES))
    spec=importlib.util.spec_from_file_location('smartsvg2161verify',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    for name in ('SmartSVGMaskEditorV216','SmartSVGExpressV2151','SmartSVGInstancesV2151'):
        if name not in mod.NODE_CLASS_MAPPINGS:raise SystemExit('Missing node: '+name)
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_6_*.json'))
    if len(workflows)!=2:raise SystemExit('Expected two V21.6 workflows')
    for path in workflows:
        data=json.loads(path.read_text(encoding='utf-8'))
        nodes={n['id']:n for n in data['nodes']}
        if len(nodes)!=len(data['nodes']):raise SystemExit('Duplicate node ids')
        for n in nodes.values():
            if n['type'] not in mod.NODE_CLASS_MAPPINGS:continue
            cls=mod.NODE_CLASS_MAPPINGS[n['type']]
            contract=list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
            if [i['name'] for i in n['inputs']]!=contract or [o['type'] for o in n['outputs']]!=list(cls.RETURN_TYPES):
                raise SystemExit('Workflow contract mismatch: '+path.name)
        for identity,src,slot,dst,port,datatype in data['links']:
            if (src not in nodes or dst not in nodes or
                nodes[src]['outputs'][slot]['type']!=datatype or
                nodes[dst]['inputs'][port]['type']!=datatype or
                nodes[dst]['inputs'][port]['link']!=identity):
                raise SystemExit('Invalid connection: '+path.name)
    print(f'V21.6.1 integrity: {len(files)} SHA256 OK, {len(older["fichiers_sha256"])-len(changed)} V21.6 files unchanged, 2 workflows OK',flush=True)

def suite(n):
    if n not in SUITES:raise SystemExit('Select suite 1..5')
    os.chdir(ROOT)
    os.execv(sys.executable,[sys.executable,'-m','unittest','-q',*('tests.'+i for i in SUITES[n].split())])

def javascript():
    js=shutil.which('node')
    if not js:raise SystemExit('Node >=18 required for JS tests')
    result=subprocess.run([js,'--test',*JS_FILES],cwd=ROOT,text=True,capture_output=True,timeout=90)
    found=re.search(r'^# pass (\d+)$',result.stdout,re.M)
    if result.returncode or not found or int(found.group(1))!=35:
        raise SystemExit(result.stdout[-4000:]+result.stderr[-1500:])
    print(f'JavaScript: {found.group(1)} tests passed',flush=True)

if __name__=='__main__':
    if '--suite' in sys.argv:
        try: n=int(sys.argv[sys.argv.index('--suite')+1])
        except (ValueError,IndexError):raise SystemExit('Suite 1..5 required')
        suite(n)
    else:
        if '--javascript' in sys.argv:javascript()
        integrity()
        if not any(s in sys.argv for s in ('--integrity-only','--javascript')):
            print('Use --integrity-only, --suite 1..5 or --javascript')
