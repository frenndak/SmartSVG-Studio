"""Run: python tools/v2115_governance.py [--corpus path] [--output path]"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from smartsvg_governance.corpus import make_manifest,save_g0
from smartsvg_governance.inventory import write_inventory

def main() -> int:
    p=argparse.ArgumentParser(description='G0 documentary + G1.1 read-only compatibility pre-inventory')
    p.add_argument('--corpus',type=Path,default=None,help='Private images, never copied to the package')
    p.add_argument('--output',type=Path,default=ROOT/'governance'/'evidence')
    args=p.parse_args()
    out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    # The source directory is an explicit opt-in, never auto-index home pictures.
    manifest=make_manifest(args.corpus, ROOT/'governance'/'fixtures')
    save_g0(manifest,out)
    summary=write_inventory(ROOT,out)
    print(json.dumps({'g0':manifest['gate'], 'workflows':summary['workflow_count'],
                      'registered_nodes':summary['node_registration_count'],
                      'unresolved_types':summary['unresolved_types'],
                      'anomalies':len(summary['warnings']),
                      'G1_1':'PRE_INVENTORY_ONLY'},ensure_ascii=False,indent=2))
    return 0 if summary['workflow_parsed']==summary['workflow_count'] and not summary['unresolved_types'] else 2
if __name__=='__main__':
    raise SystemExit(main())
