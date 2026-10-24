"""Reproducible post-unzip V21.9.1 checks. Suites should execute as separate processes."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
VERSION='21.9.1'
MANIFEST='INSTALLATION_MANIFEST_V21_9_1.json'
SUITES={
    '1':'test_v141 test_v15 test_v16 test_v17 test_v18 test_v181',
    '2':'test_v19 test_v191 test_v192 test_v193 test_v194 test_v1951 test_v195 test_v1952 test_v196 test_v197 test_v1971 test_v198 test_v199 test_v20 test_v201 test_v2011 test_v2012 test_v202 test_v202_merge test_v203',
    '3a':'test_v204 test_v205 test_v206 test_v21 test_v211',
    '3b':'test_v212 test_v213 test_v2131 test_v2132 test_svg_root_v2132',
    '4':'test_v214 test_v215 test_v2151',
    '5':'test_v216',
    '6':'test_v217',
    '7':'test_v2171',
    '8':'test_v218',
    '9':'test_v219',
    '10':'test_v2191',
}
JS_FILES=('test_v215_frontend.mjs','test_v215_frontend_runtime.mjs','test_v2151_frontend.mjs',
    'test_v2151_runtime.mjs','test_v216_frontend.mjs','test_v216_runtime.mjs',
    'test_v2161_viewport.mjs','test_v219_native.mjs','test_v219_runtime.mjs')


def check_integrity():
    doc=json.loads((ROOT/MANIFEST).read_text('utf-8'))
    entries=doc['fichiers_sha256']
    if doc['version']!=VERSION or doc['nombre_fichiers']!=len(entries):
        raise SystemExit('Incorrect V21.9 manifest header')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and '.pyc'!=p.suffix and '__pycache__' not in p.parts}
    if actual!=(set(entries)|{MANIFEST}):raise SystemExit('Files absent or unexpected: '+repr(sorted(actual^(set(entries)|{MANIFEST}))[:20]))
    for relative,digest in entries.items():
        path=ROOT/relative
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):raise SystemExit('Unsafe archive path '+relative)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit('SHA-256 does not match '+relative)
    older=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_9.json').read_text('utf-8'))
    allowed_changed={'smartsvg_native/inspector.py','smartsvg_cricut/direct_import_v218.py',
                     'web/js/smartsvg_native_v219.js','tests/test_v219_runtime.mjs'}
    unchanged=[]
    for relative,digest in older['fichiers_sha256'].items():
        if relative not in entries:raise SystemExit('Legacy file removed '+relative)
        if entries[relative]!=digest:
            if relative not in allowed_changed:raise SystemExit('Legacy file unexpectedly edited '+relative)
        else:unchanged.append(relative)
    spec=importlib.util.spec_from_file_location('sv219verifier',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    for cls in ('SmartSVGNativeInspectorV219','SmartSVGExpressV218','SmartSVGMaskEditorV216',
                'SmartSVGQualityV217','SmartSVGPrepareV217','SmartSVGExpressV2151'):
        if cls not in module.NODE_CLASS_MAPPINGS:raise SystemExit('Missing node '+cls)
    curr=module.NODE_CLASS_MAPPINGS['SmartSVGExpressV218'];legacy=module.NODE_CLASS_MAPPINGS['SmartSVGExpressV2151']
    if curr.INPUT_TYPES()!=legacy.INPUT_TYPES() or curr.RETURN_TYPES!=legacy.RETURN_TYPES:raise SystemExit('Express ports changed')
    workflows=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_9_*.json'))
    if len(workflows)!=3:raise SystemExit('3 expected V21.9 workflows')
    for path in workflows:
        w=json.loads(path.read_text('utf-8'));nodes={n['id']:n for n in w['nodes']}
        if len(nodes)!=len(w['nodes']):raise SystemExit('Duplicate node IDs')
        if len([n for n in nodes.values() if n['type']=='SmartSVGNativeInspectorV219'])!=1:
            raise SystemExit('Missing V21.9 inspection node in '+path.name)
        for n in nodes.values():
            cls=module.NODE_CLASS_MAPPINGS.get(n['type'])
            if cls is None:continue
            input_names=list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
            if [x['name'] for x in n['inputs']]!=input_names or [x['type'] for x in n['outputs']]!=list(cls.RETURN_TYPES):
                raise SystemExit('Port order changed '+path.name+' '+n['type'])
        for ident,src,slot,dst,port,typ in w['links']:
            if src not in nodes or dst not in nodes or slot>=len(nodes[src]['outputs']) or port>=len(nodes[dst]['inputs']) or \
                nodes[src]['outputs'][slot]['type']!=typ or nodes[dst]['inputs'][port]['type']!=typ or \
                nodes[dst]['inputs'][port]['link']!=ident or ident not in (nodes[src]['outputs'][slot]['links'] or []):
                raise SystemExit('Broken workflow connection '+path.name+f' link {ident}')
    print(f'Integrity: {len(entries)} files; {len(unchanged)} V21.9 files unchanged; 3 workflows',flush=True)


def suite(id):
    if id not in SUITES:raise SystemExit('Expected --suite 1,2,3a,3b,4,5,6,7,8,9,10')
    os.chdir(ROOT)
    os.execv(sys.executable,[sys.executable,'-m','unittest','-q',*('tests.'+v for v in SUITES[id].split())])


def js():
    path=shutil.which('node')
    if not path:raise SystemExit('Node >= 18 required for JS tests only')
    cmd=[path,'--test',*('tests/'+file for file in JS_FILES)]
    out=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=120)
    found=re.search(r'^# pass (\d+)$',out.stdout,re.M)
    if out.returncode or not found or int(found.group(1))!=41:raise SystemExit('JS failure: '+out.stdout[-2000:]+out.stderr[-1000:])
    print('JavaScript: 41 passed',flush=True)

if __name__=='__main__':
    if '--suite' in sys.argv:
        suite(sys.argv[sys.argv.index('--suite')+1])
    else:
        check_integrity()
        if '--javascript' in sys.argv:js()
        if not any(x in sys.argv for x in ('--javascript','--integrity-only')):
            print('Use --integrity-only, --javascript or --suite X')
