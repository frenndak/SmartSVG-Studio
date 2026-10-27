import tempfile,unittest,sys
from pathlib import Path
from PIL import Image,ImageDraw
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from smartsvg_governance.artifact_qa import audit_project,QAError
class Tests(unittest.TestCase):
 def make(self,rect=False):
  self.tmp=tempfile.TemporaryDirectory();p=Path(self.tmp.name)
  im=Image.new('RGBA',(180,150),(255,255,255,0));d=ImageDraw.Draw(im)
  if rect:d.rounded_rectangle((20,20,160,130),radius=2,fill=(255,255,255,255))
  else:d.ellipse((40,15,142,136),fill=(200,0,0,255))
  im.save(p/'a.png')
  (p/'a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="30mm" height="30mm"><path d="M0 0 L30 0 L30 30 L0 30 Z"/></svg>')
  data={'objets':[{'png':str(p/'a.png'),'svg_contour':str(p/'a.svg'),'contour_nombre_chemins':1,'largeur_finale_avec_marge_mm':30}], 'planches_cricut':[]}
  (p/'RAPPORT_V21_1.json').write_text(json.dumps(data))
  return p
 def test_silhouette_passes_geometry_but_requires_external_proof(self):
  p=self.make();try_:str= 'unused'
  try:
   r=audit_project(p/'RAPPORT_V21_1.json')
   self.assertEqual(r['status'],'REVIEW_REQUIRED');self.assertEqual(r['external_validation']['physical_cut'],'NOT_TESTED')
  finally:self.tmp.cleanup()
 def test_rectangle_rejected_for_sticker(self):
  p=self.make(rect=True)
  try:self.assertIn('SILHOUETTE_RECTANGULAIRE_NON_FIABLE',audit_project(p/'RAPPORT_V21_1.json')['blocking_codes'])
  finally:self.tmp.cleanup()
 def test_rectangle_accepted_only_as_manual_card_review(self):
  p=self.make(rect=True)
  try:self.assertEqual(audit_project(p/'RAPPORT_V21_1.json',requested_intent='carte_rectangle')['status'],'REVIEW_REQUIRED')
  finally:self.tmp.cleanup()
 def test_escape_path_blocked(self):
  p=self.make();data=json.loads((p/'RAPPORT_V21_1.json').read_text());data['objets'][0]['png']='/etc/passwd';(p/'RAPPORT_V21_1.json').write_text(json.dumps(data))
  try:self.assertEqual(audit_project(p/'RAPPORT_V21_1.json')['status'],'BLOCKED')
  finally:self.tmp.cleanup()
 def test_svg_not_markup_script(self):
  p=self.make();(p/'a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
  try:self.assertIn('FICHIER_NON_VERIFIABLE',audit_project(p/'RAPPORT_V21_1.json')['blocking_codes'])
  finally:self.tmp.cleanup()
if __name__=='__main__':unittest.main(verbosity=2)
