"""Adversarial V19.5.1 review tests. No real Florence/SAM/GPU inference."""
import importlib, sys,types,tempfile,unittest,json,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
NAME='smartsvg_v1951_audit'
if NAME not in sys.modules:
    pkg=types.ModuleType(NAME);pkg.__path__=[str(ROOT)];sys.modules[NAME]=pkg
v=importlib.import_module(NAME+'.photo_contacts_v195')

def sample():
    rgb=np.full((240,380,3),(231,224,205),dtype=np.uint8)
    masks=[]
    for x in (102,185,255):
        m=np.zeros(rgb.shape[:2],np.uint8)
        cv2.circle(m,(x,115),62,255,-1)
        masks.append(m)
    return rgb,masks

class HardenedOverlapTests(unittest.TestCase):
    def test_multiobject_overlap_bounded_assignment_preserves_input(self):
        _,ms=sample(); originals=[x.copy() for x in ms]
        out,q=v.propose_exclusive_masks(ms)
        self.assertTrue(q['proposition_valide'],q)
        self.assertEqual(q['distance_memory_strategy'],'two_best_maps_not_full_stack')
        self.assertEqual(q['pixels_partages_attribues']+q['pixels_restant_ambigus'],q['pixels_partages'])
        cover=np.zeros(ms[0].shape,np.uint8)
        for mask in out:cover+=(mask>=128).astype('uint8')
        self.assertFalse(np.any(cover>1))
        for old,new in zip(originals,ms):np.testing.assert_array_equal(old,new)
        for i,(m,d) in enumerate(zip(ms,out)):
            own=(m>=128)&(sum((x>=128).astype('uint8') for x in ms)==1)
            np.testing.assert_array_equal(d[own],m[own])

    def test_reject_incorrect_or_huge_masks_without_distance_maps(self):
        base=np.zeros((9,12),np.uint8)
        for bad in ((base,np.zeros((8,12),np.uint8)),(base,np.zeros((9,12),np.float32)),
                    (base,np.zeros((9,12,1),np.uint8)),
                    (np.zeros((0,12),np.uint8),),
                    tuple(base for _ in range(17))):
            with self.assertRaises(v.PhotoExtractionError):v.propose_exclusive_masks(list(bad))
            with self.assertRaises(v.PhotoExtractionError):v.analyze_overlaps(list(bad),.5)

    def test_finite_unit_restrictions(self):
        _,masks=sample()
        for mm in (0,-.1,float('nan'),float('inf'),11):
            with self.assertRaises(v.PhotoExtractionError):v.analyze_overlaps(masks,mm)

    def test_reject_identical_and_no_overlap(self):
        _,m=sample(); out,q=v.propose_exclusive_masks([m[0],m[0]])
        self.assertIsNone(out)
        shifted=np.roll(m[0],205,axis=1)
        out,q=v.propose_exclusive_masks([m[0],shifted])
        self.assertIsNone(out)
        self.assertIn('aucun chevauchement',q['motif'])

    def test_safe_mask_path(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'03_MASQUES').mkdir()
            (root/'03_MASQUES'/'foo.png').touch()
            self.assertEqual(v._mask_path_inside_root(root,'03_MASQUES/foo.png'),(root/'03_MASQUES'/'foo.png').resolve())
            for bad in ('../secret.png','03_MASQUES/../secret.png','/tmp/out.png','',
                        '02_OBJETS_PNG/detoure.png'):
                with self.assertRaises(v.PhotoExtractionError):v._mask_path_inside_root(root,bad)

    def test_preview_and_core_sha_preservation(self):
        rgb,masks=sample()
        with tempfile.TemporaryDirectory() as td:
            prev,_=v.process_photo_v194(rgb,str(Path(td)/'old'),masks=np.stack(masks).astype('float32')/255,
                                         labels='person;glass;other',mode='masques_requis',width_mm=100)
            new,_=v.process_photo_v195(rgb,str(Path(td)/'new'),masks=np.stack(masks).astype('float32')/255,
                                        labels='person;glass;other',mode='masques_requis',width_mm=100,
                                        contact_mode='proposer_separation')
            a=Path(prev['output']);b=Path(new['output'])
            qa=new['audit_v195']
            self.assertTrue(qa['proposition_separation']['proposition_valide'])
            self.assertTrue((b/qa['apercu_proposition_experimentale']).is_file())
            self.assertEqual(qa['controle_attribution']['pixels_initiaux_partages'],qa['contacts']['pixels_en_commun'])
            self.assertEqual(qa['controle_attribution']['pixels_restants_non_attribues'],qa['proposition_separation']['pixels_restant_ambigus'])
            for entry in prev['audit_v19']['objets']:
                for k in ('fichier_rgba','fichier_cricut_test','fichier_masque'):
                    f=entry[k]
                    self.assertEqual(hashlib.sha256((a/f).read_bytes()).hexdigest(),hashlib.sha256((b/f).read_bytes()).hexdigest())
            ready=json.loads((b/'PRET_V19_5_2.json').read_text())
            for f,entry in ready['fichiers'].items():
                self.assertEqual(hashlib.sha256((b/f).read_bytes()).hexdigest(),entry['sha256'])
            self.assertFalse((b/'PRET_V19_5.json').exists())

    def test_conservative_does_not_make_proposal(self):
        rgb,masks=sample()
        with tempfile.TemporaryDirectory() as td:
            r,_=v.process_photo_v195(rgb,td,masks=np.stack(masks).astype('float32')/255,
                                      mode='masques_requis')
            p=Path(r['output'])
            self.assertIsNone(r['audit_v195']['apercu_proposition_experimentale'])
            self.assertFalse((p/'05_PROPOSITIONS_CONTACTS').exists())

    def test_automatic_failure_still_atomic(self):
        rgb,masks=sample()
        with tempfile.TemporaryDirectory() as td,patch.object(v,'_proposal_preview',side_effect=RuntimeError('crash QA')):
            with self.assertRaises(v.PhotoExtractionError):
                v.process_photo_v195(rgb,td,masks=np.stack(masks).astype('float32')/255,
                                     mode='masques_requis',contact_mode='proposer_separation')
            self.assertFalse(list(Path(td).glob('SmartSVG_V19_5_2_PHOTO_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V1952_*')))

if __name__=='__main__':unittest.main()
