import importlib,types,sys,unittest,tempfile,os,hashlib,json
from pathlib import Path
from unittest.mock import patch
import numpy as np,cv2,torch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
if 'sv205test' not in sys.modules:
    m=types.ModuleType('sv205test');m.__path__=[str(ROOT)];sys.modules['sv205test']=m
q=importlib.import_module('sv205test.cricut_preflight_v205')
n=importlib.import_module('sv205test.node_v205')
base=importlib.import_module('sv205test.node_v203')
def fixture(path):
    p=Path(path);(p/'08_CHOIX_CRICUT').mkdir();(p/'02_ZONE_UTILE').mkdir()
    Image.new('RGB',(100,140),'white').save(p/'02_ZONE_UTILE'/'carte_redressee.png')
    return p
def image(p,kind='ok'):
    a=np.zeros((140,100,4),np.uint8)
    if kind=='ok':a[20:110,20:80,3]=255
    if kind=='two':a[20:55,20:50,3]=255;a[70:100,40:70,3]=255
    if kind=='hole':a[20:110,20:80,3]=255;a[40:50,30:40,3]=0
    if kind=='border':a[20:110,0:80,3]=255
    if kind=='opaque':a[...,3]=255
    Image.fromarray(a).save(p/'08_CHOIX_CRICUT'/q.NAMES['imprimer_decouper_contour'])
def svg(p,d='M0 0 L50 0 Z',width='90mm',height='126mm',operation='decouper_contour_seul'):
    x=p/'08_CHOIX_CRICUT'/q.NAMES[operation]
    x.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="'+width+'" height="'+height+'" viewBox="0 0 100 140"><path d="'+d+'"/></svg>')
    return x
class PreflightTests(unittest.TestCase):
    def test_png_good(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p);r,pre=q.audit_project(p);self.assertEqual(r['statut'],'A_VERIFIER');self.assertIsNotNone(pre)
    def test_two_islands(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p,'two');r,_=q.audit_project(p);self.assertEqual(r['statut'],'RISQUE_ELEVE')
    def test_hole(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p,'hole');r,_=q.audit_project(p);self.assertGreater(r['dimensions']['nombre_trous_transparents'],0)
    def test_border(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p,'border');r,_=q.audit_project(p);self.assertEqual(r['statut'],'RISQUE_ELEVE')
    def test_opaque(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p,'opaque');r,_=q.audit_project(p);self.assertIn('PNG_OPAQUE_RISQUE_DE_COUPE_RECTANGULAIRE',r['avertissements'])
    def test_blank(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p,'blank');r,_=q.audit_project(p);self.assertEqual(r['statut'],'RISQUE_ELEVE')
    def test_scaled_png(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p);r,_=q.audit_project(p,width_mm=90);self.assertEqual(r['dimensions']['largeur_estimee_mm'],90.)
    def test_low_dpi(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p);r,_=q.audit_project(p);self.assertIn('RESOLUTION_ESTIMEE_INFERIEURE_150_PPP',r['avertissements'])
    def test_svg_simple(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);svg(p);r,_=q.audit_project(p,operation='decouper_contour_seul');self.assertEqual(r['dimensions']['sous_chemins'],1)
    def test_svg_open(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);svg(p,'M0 0 L50 0');r,_=q.audit_project(p,operation='decouper_contour_seul');self.assertEqual(r['statut'],'RISQUE_ELEVE')
    def test_svg_paths(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);svg(p,'M0 0 L3 0 Z '*85,operation='decouper_tous_les_traits');r,_=q.audit_project(p,operation='decouper_tous_les_traits');self.assertIn('NOMBREUX_CHEMINS_ATTENTION_PETITES_PIECES',r['avertissements'])
    def test_svg_bad_units(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);svg(p,width='90px');
            with self.assertRaises(q.CricutPreflightError):q.audit_project(p,operation='decouper_contour_seul')
    def test_svg_unsafe(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);f=svg(p);f.write_text('<!DOCTYPE svg [<!ENTITY x "boom">]><svg width="90mm" height="126mm" viewBox="0 0 100 140"><path d="M0 0 Z"/></svg>')
            with self.assertRaises(q.CricutPreflightError):q.audit_project(p,operation='decouper_contour_seul')
    def test_bad_width(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t)
            for bad in (float('nan'),True,1,300):
                with self.assertRaises(q.CricutPreflightError):q.audit_project(p,width_mm=bad)
    def test_bad_paper(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t)
            with self.assertRaises(q.CricutPreflightError):q.audit_project(p,paper='A0')
    def test_paper_overflow(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p);r,_=q.audit_project(p,width_mm=280);self.assertEqual(r['statut'],'RISQUE_ELEVE')
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as other:
            p=fixture(t);(p/'08_CHOIX_CRICUT').rename(p/'old');(p/'08_CHOIX_CRICUT').symlink_to(other,target_is_directory=True)
            with self.assertRaises(q.CricutPreflightError):q.audit_project(p)
    def test_atomic_qa(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);r=q.atomic_qa(p,{'statut':'A_VERIFIER'},Image.new('RGB',(20,20),'white'))
            self.assertTrue(Path(r['rapport_enregistre']).exists());self.assertTrue(Path(r['apercu']).exists())
    def test_old_nodes_registered(self):
        for key in ('SmartSVGLineArtV204','SmartSVGStudioV20Expert','SmartSVGLineArtV205','SmartSVGCricutPreflightV205'):
            self.assertIn(key,n.NODE_CLASS_MAPPINGS)
    def test_standalone(self):
        with tempfile.TemporaryDirectory() as t:
            p=fixture(t);image(p);r=n.SmartSVGCricutPreflightV205().run(str(p));self.assertEqual(json.loads(r['result'][0])['statut'],'A_VERIFIER')
    def test_quality_controls_preserved(self):
        d=n.SmartSVGLineArtV205.INPUT_TYPES()['required'];self.assertIn('controle_contours',d);self.assertIn('controle_cricut',d)
    def test_production_unmodified(self):
        a=np.full((210,175,3),255,np.uint8);cv2.ellipse(a,(87,90),(50,70),0,0,360,(0,0,0),3)
        img=torch.from_numpy(a.astype(np.float32)/255)[None]
        with tempfile.TemporaryDirectory() as t,patch.object(base,'gpu_snapshot',return_value={'cuda_disponible':False}):
            old=n.SmartSVGLineArtV204().run(img,t,segmentation_ia='desactiver',operation_cricut='decouper_tous_les_traits')
            new=n.SmartSVGLineArtV205().run(img,t,segmentation_ia='desactiver',operation_cricut='decouper_tous_les_traits')
            d1=json.loads(old['result'][1]);d2=json.loads(new['result'][1]);self.assertEqual(Path(d1['fichier_mode_choisi']).read_bytes(),Path(d2['fichier_mode_choisi']).read_bytes())
            self.assertTrue(Path(d2['controle_cricut_v20_5']['rapport_enregistre']).exists())
    def test_preflight_failure_preserves_output(self):
        a=np.full((210,175,3),255,np.uint8);img=torch.from_numpy(a.astype(np.float32)/255)[None]
        with tempfile.TemporaryDirectory() as t,patch.object(base,'gpu_snapshot',return_value={'cuda_disponible':False}),patch.object(n,'audit_project',side_effect=OSError('fail')):
            r=n.SmartSVGLineArtV205().run(img,t,segmentation_ia='desactiver');d=json.loads(r['result'][1]);self.assertEqual(d['controle_cricut_v20_5']['statut'],'ECHEC_PREFLIGHT');self.assertTrue(Path(d['fichier_mode_choisi']).exists())
if __name__=='__main__':unittest.main()
