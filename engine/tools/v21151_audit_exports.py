"""Read-only quality audit of actual generated PNG/SVG artifacts."""
from pathlib import Path
import sys, argparse, json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from smartsvg_governance.artifact_qa import audit_project

def main():
    parser=argparse.ArgumentParser(description='Analyse les exports SmartSVG sans les modifier.')
    parser.add_argument('report',help='Chemin vers RAPPORT_V21_1.json')
    parser.add_argument('--intent',choices=('sticker_contour','carte_rectangle'),default='sticker_contour')
    parser.add_argument('--output',help='Ecrire le rapport d audit JSON ici (nouveau fichier ou ecrasement explicite)')
    args=parser.parse_args()
    quality=audit_project(args.report,requested_intent=args.intent)
    print(json.dumps(quality,indent=2,ensure_ascii=False))
    if args.output:
        out=Path(args.output).resolve()
        if out.is_symlink():parser.error('sortie symbolique refusee')
        out.write_text(json.dumps(quality,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return 1 if quality['status']=='BLOCKED' else 0
if __name__=='__main__':sys.exit(main())
