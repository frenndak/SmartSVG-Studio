"""G0 corpus provenance, automatic fixture truth and human-review protocol."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

# Original assets are intentionally NOT redistributed with the plugin.
REFERENCE_CASES = [
    ('T-01','Fille manga photographiée','1000077568.jpg','1000077568(2).jpg',1,'opaque_complex','isoler illustration; préserver détails et bordures'),
    ('T-02','Planche de douze escargots','1000077534.jpg','1000077534(2).jpg',12,'white_board','douze sujets isolés; ne pas découper un rectangle'),
    ('T-03','Carte avec texte','1000077454.png','1000077454.png',1,'text_layout','préserver texte; refuser segmentation ambiguë'),
    ('T-04','Portrait fantaisie','1000077462.png','1000077462(2).png',1,'photo_complex','sujet et accessoires; corrections manuelles si besoin'),
    ('T-05','Affiche fantasy A','1000077435.png','1000077435(4).png',1,'scene_complex','ne pas inventer de contours dans le décor'),
    ('T-06','Affiche fantasy B','1000077436.png','1000077436.png',1,'scene_complex','ne pas fusionner des silhouettes de premier plan'),
    ('T-07','Homme et atelier','1000077420.png','1000077420.png',1,'photo_complex','éviter d’inclure le fond comme une silhouette'),
    ('T-08','Couverture illustrée','1000077347.webp','1000077347.webp',1,'text_layout','vérifier texte et aplats; option refus utile'),
    ('T-09','Planche de vingt-quatre personnages','1000077309.png','1000077309(2).png',24,'dark_board','24 sujets distincts sans fusion; petits détails à vérifier'),
]
EXPECTED_SIZE = [(1152,1536),(1536,1024),(1122,1111),(1152,1536),(1087,1536),(1024,1536),(1229,1536),(1074,1536),(1536,1097)]

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1<<20), b''):
            h.update(part)
    return h.hexdigest()


def build_fixtures(destination: Path) -> list[dict]:
    """Create original, unencumbered tiny fixtures and exact truth masks."""
    destination.mkdir(parents=True,exist_ok=True)
    img=Image.new('RGBA',(160,120),(0,0,0,0))
    d=ImageDraw.Draw(img)
    d.ellipse((15,10,143,109),fill=(230,115,62,255))
    d.ellipse((52,38,106,83),fill=(0,0,0,0))
    src=destination/'R-01.png'; target=destination/'R-01_mask.png'
    img.save(src)
    img.getchannel('A').save(target)
    # False-positive adversarial: no subject boundary can be independently established.
    blank=Image.new('RGB',(160,120),(255,255,255))
    d=ImageDraw.Draw(blank)
    d.rectangle((2,2,157,117),outline=(250,250,250),width=1)
    src2=destination/'R-02.png'; gt2=destination/'R-02_mask.png'
    blank.save(src2)
    Image.new('L',blank.size,0).save(gt2)
    return [
        {'id':'R-01','source':src.name,'source_sha256':sha(src),'gt_mask':target.name,'mask_sha256':sha(target),
         'size_px':[160,120], 'decision':'ACCEPT_ALPHA_MASK','origin':'synthetic_generated_in_code',
         'truth_status':'approved_deterministic','expected_components':1,'expected_holes':1},
        {'id':'R-02','source':src2.name,'source_sha256':sha(src2),'gt_mask':gt2.name,'mask_sha256':sha(gt2),
         'size_px':[160,120], 'decision':'REJECT_AUTO_SILHOUETTE','origin':'synthetic_generated_in_code',
         'truth_status':'approved_deterministic','expected_components':0,'expected_holes':0},
    ]


def make_manifest(corpus: Path | None, fixture_dir: Path) -> dict:
    synthetic=build_fixtures(fixture_dir)
    rows=[]
    for i, (case_id,title,original,local,objects,family,goal) in enumerate(REFERENCE_CASES):
        physical = corpus/local if corpus is not None else None
        present = bool(physical and physical.is_file())
        actual_size=None; digest=None; status='SOURCE_NOT_AVAILABLE'
        if present:
            with Image.open(physical) as photo:
                actual_size=list(photo.size)
            digest=sha(physical)
            status='SOURCE_VERIFIED' if actual_size==list(EXPECTED_SIZE[i]) else 'DIMENSION_MISMATCH'
        rows.append({
            'id':case_id,'label':title,'original_filename':original,'current_local_filename':local,
            'sha256':digest,'source_status':status,'expected_size_px':list(EXPECTED_SIZE[i]),
            'actual_size_px':actual_size,'expected_subject_count':objects,'family':family,
            'objective':goal,'mask_truth_status':'PENDING_HUMAN_ANNOTATION',
            'licensing':'user_supplied_internal_evaluation_only; redistribution_not_authorized',
            'measured_cut_status':'NOT_TESTED',
        })
    return {
        'schema_version':'g0-corpus-1','reference':'SmartSVG Studio roadmap v3.2 / G0.2-G0.3',
        'description':'Sources humaines externes, fixtures R synthétiques seulement dans le paquet',
        'real_cases':rows,'synthetic_cases':synthetic,
        'gate':{'g0_2': 'PASS' if all(r['source_status']=='SOURCE_VERIFIED' for r in rows) else 'BLOCKED_SOURCES',
                'g0_3':'BLOCKED_9_HUMAN_MASKS_AND_REVIEWERS',
                'g0_4':'RISKS_LOGGED_NOT_PHYSICAL_VALIDATION',
                'G0_to_G1':'NO_GO_UNTIL_HUMAN_TRUTH_AND_RISK_SIGNOFF'},
        'warnings':['La présence des images ne constitue PAS une vérité terrain.',
                    'Aucun modèle IA ni appareil Cricut testé dans ce protocole.',
                    'Ne pas distribuer les images humaines dans un ZIP public.'],
    }


def make_review_template(manifest: dict) -> dict:
    return {
        'schema_version':'g0-truth-review-1',
        'protocol':{'mask_positive':'sujet blanc 255; fond noir 0','alpha':'pas de masque plein écran accepté sans justification',
          'raters_required':2,'procedure':'noter inclusion accessoires, trous, composants, artefacts, silhouette, incertitude; conserver masques PNG distincts',
          'agreement_rule':'si écart, arbitrage humain documenté; aucun score automatique ne vaut certification',
          'critical_rejections':['rectangular_background_as_subject','unwanted_multiple_cut_paths','cut_width_mismatch','missing_source']},
        'reviews':[
            {'id':r['id'],'annotation_status':'PENDING','mask_file':None,'mask_sha256':None,
             'rater_1':None,'rater_2':None,'resolution':None,'expected_subject_count':r['expected_subject_count'],
             'accessory_notes':'', 'source_sha256':r['sha256']}
            for r in manifest['real_cases']
        ],
        'validated_synthetic':[{'id':r['id'],'mask_sha256':r['mask_sha256'],'decision':r['decision']} for r in manifest['synthetic_cases']],
        'interpretation':'masques T humains manquants : gate G0.3 NON VALIDÉ',
    }


def risk_register() -> dict:
    return {
        'schema_version':'g0-risks-1','validation_environment':'CAAS Linux local - NOT TARGET WINDOWS / RTX 3070',
        'risk_status':'INITIAL_ASSESSMENT_NOT_USER_HARDWARE_TEST',
        'risks':[
          {'code':'P0-01','risk':'alpha inversé ou masque rectangle exporté comme sujet','mitigation':'fixture R-02 + refus explicite avant coupe','verification':'fixture_negative_only'},
          {'code':'P0-02','risk':'déplacement ou échelle mm erronée','mitigation':'contrat mm/pixel indépendant, coupon physique','verification':'physical_test_pending'},
          {'code':'P0-03','risk':'SVG couleur pris pour chemin de coupe','mitigation':'séparer ART, CUT, PRINT_THEN_CUT et alerte','verification':'UI_and_Design_Space_pending'},
          {'code':'P0-04','risk':'regression de noeud historique','mitigation':'inventaire, hash source, tests existants, rollback V21.14.1','verification':'static_and_local_tests_only'},
          {'code':'P0-05','risk':'sauvegarde ou édition destructive','mitigation':'sources conservées, G1.3 checkpoint et hash','verification':'G1.3_pending'},
          {'code':'P1-06','risk':'OOM GPU modèle IA','mitigation':'diagnostic RTX 3070 8Go, mode sans IA','verification':'GPU_pending'},
          {'code':'P1-07','risk':'image non redistribuable dans logiciel public','mitigation':'corpus sources externe, manifest interne avec hash','verification':'public_bundle_without_user_media'},
          {'code':'P1-08','risk':'JS/ComfyUI ne fonctionne pas sous Windows','mitigation':'versions/QA navigateur cibles, G8','verification':'Windows_pending'},
          {'code':'P1-09','risk':'sur-découpe petits chemins','mitigation':'inspecter trajectoires, essais matière','verification':'physical_test_pending'},
        ],
        'evidence_levels':{'static':'executed_on_copy','software_target':'not_executed',
                           'design_space':'not_executed','physical':'not_executed','gpu_ai':'not_executed'},
    }


def save_g0(manifest: dict, output: Path) -> None:
    output.mkdir(parents=True,exist_ok=True)
    for name,data in [('corpus_manifest.json',manifest),('truth_review_template.json',make_review_template(manifest)),('risk_register.json',risk_register())]:
        (output/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
