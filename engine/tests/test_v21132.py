"""Regression: honest SVG-standard QA and isolated deterministic palette."""
from __future__ import annotations
import json,sys,types,importlib,tempfile,unittest,builtins
from pathlib import Path
from unittest.mock import patch
import cv2,numpy as np,torch
ROOT=Path(__file__).resolve().parents[1]
if 'test21132' not in sys.modules:
    pkg=types.ModuleType('test21132');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
vector=importlib.import_module('test21132.smartsvg_vector.layers_v2113')
qa=importlib.import_module('test21132.smartsvg_vector.qa_v21131')
node=importlib.import_module('test21132.node_v21132')
legacy=importlib.import_module('test21132.node_v21131')


def artwork():
    im=np.full((160,180,3),255,dtype=np.uint8)
    mask=np.zeros((160,180),np.float32)
    cv2.ellipse(mask,(85,74),(50,52),15,0,360,1.,-1)
    cv2.ellipse(im,(85,74),(50,52),15,0,360,(160,55,215),-1)
    cv2.circle(im,(95,88),25,(45,140,180),-1)
    return im,mask

class TestV21132(unittest.TestCase):
    def test_deterministic_palette_without_global_numpy_random_reset(self):
        im,mask=artwork()
        np.random.seed(7183);expected=np.random.random();np.random.seed(7183)
        svg1,preview1,a1=vector.vectorize_flat_art(im,mask,colors=5)
        self.assertEqual(float(np.random.random()),float(expected))
        svg2,preview2,a2=vector.vectorize_flat_art(im,mask,colors=5)
        self.assertEqual(svg1,svg2)
        np.testing.assert_array_equal(preview1,preview2)
        self.assertEqual(a1['formes'],a2['formes'])

    def test_svg_standard_renderer_really_used_if_available(self):
        im,mask=artwork();svg,_,audit=vector.vectorize_flat_art(im,mask)
        try:import cairosvg
        except ImportError:self.skipTest('CairoSVG unavailable on target installation')
        image,report=qa.analyse_svg(im,mask,svg,audit)
        self.assertEqual(report['rendu_svg_reconstruit_par'],'CairoSVG (SVG 1.1)')
        self.assertTrue(report['rendu_standard_verifie'])
        self.assertEqual(report['diagnostic'],'A_VERIFIER' if report['iou_silhouette_approx']<.98 or report['pixels_sujet_manquants']>0 or report['erreur_moyenne_couleurs_sur_recouvrement']>35 else 'PRECONTROLE_VISUEL_LOCAL')

    def test_opencv_fallback_marked_approx_and_not_auto_pass(self):
        im,mask=artwork();svg,_,audit=vector.vectorize_flat_art(im,mask)
        with patch.object(qa,'_standard_render',return_value=None):
            _,report=qa.analyse_svg(im,mask,svg,audit)
        self.assertFalse(report['rendu_standard_verifie'])
        self.assertEqual(report['diagnostic'],'A_VERIFIER')
        self.assertTrue(report['mesure_limitee_si_pas_de_rendu_standard'])

    def test_missing_native_cairo_dll_is_safe_fallback(self):
        im,mask=artwork();svg,_,audit=vector.vectorize_flat_art(im,mask)
        original_import=builtins.__import__
        def simulated(name,*args,**kwargs):
            if name=='cairosvg':raise OSError('Cairo DLL not found')
            return original_import(name,*args,**kwargs)
        with patch('builtins.__import__',side_effect=simulated):
            _,report=qa.analyse_svg(im,mask,svg,audit)
        self.assertFalse(report['rendu_standard_verifie'])
        self.assertEqual(report['diagnostic'],'A_VERIFIER')

    def test_disguised_transform_rejected(self):
        im,mask=artwork();svg,_,audit=vector.vectorize_flat_art(im,mask)
        for bad in [svg.replace(b'<g ',b'<g transform="translate(50,50)" ',1),
                    svg.replace(b'<path ',b'<path opacity="0.01" ',1),
                    svg.replace(b'viewBox="0 0 ',b'viewBox="10 0 ',1),
                    svg.replace(b'<svg ',b'<svg style="display:none" ',1)]:
            with self.subTest(bad=bad[:50]):
                with self.assertRaises(qa.QualityRefused):qa.analyse_svg(im,mask,bad,audit)

    def test_new_node_has_same_outputs_and_flags_not_cut_certified(self):
        im,mask=artwork()
        with tempfile.TemporaryDirectory() as t:
            result=node.SmartSVGEditableColorsV21132().run(
                torch.from_numpy(im.astype('float32')/255)[None],
                masque_sujet=torch.from_numpy(mask[None]),dossier_sortie=t)
            self.assertEqual(len(result['result']),4)
            report=json.loads(result['result'][-1]);self.assertIn('source_du_score',report)
            self.assertFalse(report['utilisable_comme_png_print_then_cut'])
            self.assertFalse(report['svg_multicouche_decoupe_physique_certifiee'])
            self.assertTrue(Path(result['result'][2]).exists())
            self.assertIn('SVG multicouche EXPÉRIMENTAL',result['ui']['text'][0])

    def test_all_old_node_identifiers_unchanged(self):
        for k,v in legacy.NODE_CLASS_MAPPINGS.items():self.assertIs(node.NODE_CLASS_MAPPINGS[k],v)
        self.assertEqual(node.SmartSVGEditableColorsV21132.RETURN_TYPES,legacy.SmartSVGEditableColorsV21131.RETURN_TYPES)

if __name__=='__main__':unittest.main()
