"""V21.11: strict auto-mask decision, 5-control Express, no fake cutouts."""
import importlib,sys,tempfile,types,unittest,json
from pathlib import Path
import cv2,numpy as np,torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv2111test' not in sys.modules:
    pkg=types.ModuleType('sv2111test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
core=importlib.import_module('sv2111test.smartsvg_ai.auto_masks_v2111')
node=importlib.import_module('sv2111test.node_v2111')
old=importlib.import_module('sv2111test.node_v2110')


def sheet(cols=2,rows=2,size=140):
    h=rows*size;w=cols*size
    a=np.full((h,w,3),255,dtype=np.uint8)
    for y in range(rows):
        for x in range(cols):
            X=x*size;Y=y*size
            cv2.circle(a,(X+size//2,Y+size//2),size//3, (185,45+30*x,80+30*y),-1)
            cv2.circle(a,(X+size//2,Y+size//2),size//7, (15,10,20),4)
    return a

class TestAutomaticMasksV2111(unittest.TestCase):
    def test_four_isolated_coloured_shapes(self):
        masks,rep=core.generate_masks(sheet())
        self.assertEqual(masks.shape,(4,280,280))
        self.assertEqual(rep['methode'],'ILLUSTRATION_FOND_BLANC')
        self.assertEqual(rep['statut'],'MASQUES_PROPOSES_A_VERIFIER')
        self.assertFalse(rep['certification_cricut'])
        for m in masks:
            self.assertEqual(cv2.connectedComponents(np.uint8(m),8)[0]-1,1)

    def test_dark_or_non_uniform_background_fails_closed(self):
        a=sheet();a[:]=np.linspace(0,250,a.shape[1],dtype=np.uint8)[None,:,None]
        mask,r=core.generate_masks(a)
        self.assertIsNone(mask);self.assertEqual(r['statut'],'CORRECTION_NECESSAIRE')

    def test_white_page_without_colours_fails_closed(self):
        mask,_=core.generate_masks(np.full((170,190,3),255,dtype=np.uint8))
        self.assertIsNone(mask)

    def test_rectangle_not_accepted_as_cutout(self):
        a=np.full((170,190,4),255,dtype=np.uint8)
        a[:,:,3]=0;a[30:140,30:140,3]=255
        m,rep=core.generate_masks(a)
        self.assertIsNone(m);self.assertEqual(rep['statut'],'CORRECTION_NECESSAIRE')

    def test_nonlinear_alpha_accepted(self):
        a=np.full((170,190,4),255,dtype=np.uint8);a[:,:,3]=0
        cv2.circle(a[:,:,3].copy(),(80,80),30,255,-1)  # numpy view below
        alpha=np.zeros((170,190),np.uint8);cv2.circle(alpha,(80,80),30,255,-1);a[:,:,3]=alpha
        m,rep=core.generate_masks(a)
        self.assertEqual(m.shape,(1,170,190));self.assertEqual(rep['methode'],'ALPHA_ORIGINAL')

    def test_good_injected_ai_is_explicitly_uncertified(self):
        a=np.zeros((170,190,3),dtype=np.uint8)
        mask=np.zeros((170,190),np.float32);cv2.ellipse(mask,(100,90),(28,45),0,0,360,1,-1)
        def supplier(img):return {'masks':mask,'audit':{'mock':True}}
        masks,rep=core.generate_masks(a,allow_ai=True,provider=supplier)
        self.assertEqual(masks.shape,(1,170,190));self.assertFalse(rep['certification_cricut'])
        self.assertIn('SORTIE_IA_NON_CERTIFIEE_HUMAINEMENT',rep['avertissements'])

    def test_unsafe_ai_rejected(self):
        a=np.zeros((170,190,3),dtype=np.uint8)
        def supplier(img):return {'masks':np.full((170,190),np.nan,dtype=np.float32)}
        m,r=core.generate_masks(a,allow_ai=True,provider=supplier)
        self.assertIsNone(m);self.assertIn('MASQUES_FORMAT_INVALIDE',r['avertissements'])

    def test_forced_ai_never_falls_back_to_colour(self):
        m,r=core.generate_masks(sheet(),allow_ai=True,force_ai=True,provider=lambda img:{'masks':None})
        self.assertIsNone(m);self.assertEqual(r['statut'],'CORRECTION_NECESSAIRE')

    def test_old_identifiers_and_port_types_unchanged(self):
        for key in old.NODE_CLASS_MAPPINGS:self.assertIs(old.NODE_CLASS_MAPPINGS[key],node.NODE_CLASS_MAPPINGS[key])
        self.assertEqual(node.SmartSVGAutoExpressV2111.RETURN_TYPES,old.NODE_CLASS_MAPPINGS['SmartSVGExpressV218'].RETURN_TYPES)
        self.assertEqual(list(node.SmartSVGAutoExpressV2111.INPUT_TYPES()['required']),
                         list(old.NODE_CLASS_MAPPINGS['SmartSVGExpressV218'].INPUT_TYPES()['required']))
        self.assertEqual(node.SmartSVGAutoExpressV2111.INPUT_TYPES()['required']['ia_locale'][1]['default'],'Si disponible')

    def test_auto_node_masks_are_aligned(self):
        img=torch.from_numpy(sheet().astype('float32')/255.)[None]
        m,im,raw=node.SmartSVGAutoMasksV2111().run(img,'Desactivee')['result']
        self.assertEqual(tuple(m.shape),(4,280,280));self.assertIs(img,im)
        self.assertEqual(json.loads(raw)['nombre_sujets'],4)

    def test_no_model_no_files_no_fabricated_rectangle(self):
        img=torch.from_numpy(np.zeros((170,190,3),dtype='float32'))[None]
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(core.AutoMaskError):
                node.SmartSVGAutoExpressV2111().run(img,dossier_sortie=folder,ia_locale='Desactivee')
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_explicit_rectangle_card_keeps_original_mode(self):
        img=torch.from_numpy(sheet(1,1,120).astype("float32")/255.)[None]
        with tempfile.TemporaryDirectory() as folder:
            response=node.SmartSVGAutoExpressV2111().run(img,dossier_sortie=folder,
                projet='Carte - visuel rectangulaire',largeur_mm=30.,qualite_ppp='300',
                ia_locale='Desactivee')
            data=json.loads(response['result'][2])
            self.assertIn('dossier',data)
            self.assertNotIn('detourage_automatique_v2111',data)

    def test_real_auto_manufacturing_and_cricut_handoff(self):
        img=torch.from_numpy(sheet(2,1,120).astype('float32')/255.)[None]
        with tempfile.TemporaryDirectory() as folder:
            response=node.SmartSVGAutoExpressV2111().run(img,dossier_sortie=folder,
                projet='Sticker - contour du sujet',largeur_mm=20.,qualite_ppp='300',ia_locale='Desactivee')
            info=json.loads(response['result'][2]);rec=info['import_direct_cricut_v218']
            self.assertEqual(info['nombre_objets_exportes'],2)
            self.assertEqual(rec['fichiers_prets'],2)
            self.assertEqual(rec['cartes_rectangulaires'],0)
            self.assertTrue(all(Path(x['fichier_import']).is_file() for x in rec['objets']))
            self.assertTrue(all(x['type_decoupe_presumee']=='SILHOUETTE_ALPHA_UNE_ZONE' for x in rec['objets']))
            self.assertIn('amelioration_hd_v2171',info)
            self.assertFalse(info['detourage_automatique_v2111']['certification_cricut'])

if __name__=='__main__':unittest.main()
