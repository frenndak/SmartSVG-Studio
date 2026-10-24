"""SmartSVG V21.11.1 archive validator: isolate numerical tests in subprocesses."""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MANIFEST='INSTALLATION_MANIFEST_V21_11_1.json'
BASE='INSTALLATION_MANIFEST_V21_11.json'
MODIFIED={
    '__init__.py', 'node_v2111.py', 'smartsvg_ai/auto_masks_v2111.py',
    'smartsvg_cricut/direct_import_v218.py', 'verify_package_v2111.py',
    'example_workflows/SmartSVG_Studio_V21_11_01_Auto_Simple.json',
    'example_workflows/SmartSVG_Studio_V21_11_02_Auto_Corriger_Exporter.json',
    'example_workflows/SmartSVG_Studio_V21_11_03_Capture_Auto_Correction.json',
}
ENV=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
         MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')


def integrity():
    doc=json.loads((ROOT/MANIFEST).read_text('utf8'))
    files=doc['fichiers_sha256']
    assert doc['version']=='21.11.1' and doc['nombre_fichiers']==len(files)
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts
            and p.suffix!='.pyc'}
    assert actual==set(files)|{MANIFEST},f'Différence avec manifeste : {actual^(set(files)|{MANIFEST})}'
    for rel,h in files.items():
        p=ROOT/rel
        assert p.is_file() and not p.is_symlink()
        assert p.resolve().is_relative_to(ROOT.resolve()),rel
        assert hashlib.sha256(p.read_bytes()).hexdigest()==h,rel
    old=json.loads((ROOT/BASE).read_text('utf8'))['fichiers_sha256']
    changed={p for p in old if files.get(p)!=old[p]}
    assert changed<=MODIFIED, f'Fichiers historiques modifies hors périmètre : {changed-MODIFIED}'
    assert not(set(old)-set(files)), 'Fichiers historiques manquants'
    # Read canonical node schema and validate all links in the three supplied workflows.
    sp=importlib.util.spec_from_file_location('ss21111check',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
    pkg=importlib.util.module_from_spec(sp);sys.modules[sp.name]=pkg;sp.loader.exec_module(pkg)
    reg=pkg.NODE_CLASS_MAPPINGS
    from importlib import import_module
    oldreg=import_module('ss21111check.node_v2110').NODE_CLASS_MAPPINGS
    assert all(reg[k] is v for k,v in oldreg.items())
    assert 'SmartSVGAutoMasksV2111' in reg and 'SmartSVGAutoExpressV2111' in reg
    assert len(reg['SmartSVGAutoExpressV2111'].INPUT_TYPES()['required'])==6
    assert len(reg['SmartSVGAutoExpressV2111'].INPUT_TYPES()['optional'])==2
    for wf_path in sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_11_*.json')):
        wf=json.loads(wf_path.read_text('utf8'))
        nodes={n['id']:n for n in wf['nodes']}
        assert len(nodes)==len(wf['nodes'])
        for n in nodes.values():
            cls=reg.get(n['type'])
            if cls is None:continue
            spec=cls.INPUT_TYPES()
            expected=list(spec.get('required',{}))+list(spec.get('optional',{}))
            assert [x['name'] for x in n['inputs']]==expected,(wf_path.name,n['type'])
            assert [x['type'] for x in n['outputs']]==list(cls.RETURN_TYPES)
        for lid,src,src_port,dst,dst_port,typ in wf['links']:
            assert nodes[src]['outputs'][src_port]['type']==typ
            assert nodes[dst]['inputs'][dst_port]['type']==typ
            assert nodes[dst]['inputs'][dst_port]['link']==lid
            assert lid in (nodes[src]['outputs'][src_port].get('links') or [])
    print(f'INTEGRITE OK : {len(files)} fichiers ; {len(old)-len(changed)}/{len(old)} historiques inchangés ; 3 workflows',flush=True)


def py_tests(group):
    proc=subprocess.run([sys.executable,'-m','unittest','-q',*('tests.'+n for n in group)],
                        cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    match=re.search(r'Ran (\d+) tests',proc.stdout+proc.stderr)
    if proc.returncode or match is None:
        raise RuntimeError((proc.stdout+proc.stderr)[-2500:])
    print(f'PYTHON OK : {match.group(1)} tests',flush=True)


def js_tests():
    paths=sorted((ROOT/'tests').glob('*.mjs'))
    proc=subprocess.run(['node','--test',*(str(p) for p in paths)],
                        cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    m=re.search(r'^# pass (\d+)$',proc.stdout,re.M)
    if proc.returncode or m is None:raise RuntimeError((proc.stdout+proc.stderr)[-2500:])
    print(f'JAVASCRIPT OK : {m.group(1)} tests',flush=True)


def main():
    args=sys.argv[1:]
    if '--suite' in args:
        pos=args.index('--suite')
        if len(args)<=pos+1 or not args[pos+1].isdigit() or not 1<=int(args[pos+1])<=12:
            raise SystemExit('--suite attend un numero de 1 à 12')
        spec=importlib.util.spec_from_file_location('oldchecks',ROOT/'verify_package_v21101.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        py_tests(mod.SUITES[int(args[pos+1])-1].split())
    if '--new' in args:
        py_tests(['test_v21102_global','test_v21103_audit','test_v2111','test_v21111_correctifs'])
    if '--javascript' in args:js_tests()
    integrity()

if __name__=='__main__':main()
