"""Architecture V21.4, pure-module contracts and byte-equivalent production."""
import hashlib
import importlib
import json
import math
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
PKG='sv214test'
if PKG not in sys.modules:
    package=types.ModuleType(PKG)
    package.__path__=[str(ROOT)]
    sys.modules[PKG]=package
core=importlib.import_module(PKG+'.smartsvg_core.contracts')
reporting=importlib.import_module(PKG+'.smartsvg_core.reporting')
registry=importlib.import_module(PKG+'.smartsvg_compat.registry')
cricut=importlib.import_module(PKG+'.smartsvg_cricut.inspection')
svg=importlib.import_module(PKG+'.smartsvg_vector.metadata')
node=importlib.import_module(PKG+'.node_v214')
old=importlib.import_module(PKG+'.node_v2132')


def sha(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()

class V214Contracts(unittest.TestCase):
    def intent(self,**kwargs):
        return core.ExpressRequest.from_widgets(projet=kwargs.get('projet',core.PROJECTS[0]),
            largeur_mm=kwargs.get('width',40),qualite_ppp=kwargs.get('dpi','300'),
            ia_locale=kwargs.get('ai','Desactivee'),masques_objets=kwargs.get('mask',None))

    def test_defaults(self):
        x=self.intent();self.assertEqual(x.dpi,300);self.assertFalse(x.external_masks)
        self.assertEqual(x.expected_mask_source,'AUCUNE_INFÉRENCE_INTERNE_DEMANDÉE')
    def test_explicit_provenance(self):
        self.assertEqual(self.intent(mask=object()).expected_mask_source,'MASQUES_EXTERNES_FOURNIS')
        self.assertIn('NON_PROUVÉE',self.intent(ai='Obligatoire').expected_mask_source)
    def test_project_unknown(self):
        with self.assertRaises(core.ContractError):self.intent(projet='autre')
    def test_invalid_width_types(self):
        for value in (float('nan'),float('inf'),-1,0,9,181,True,'garbage'):
            with self.subTest(value=value),self.assertRaises(core.ContractError):self.intent(width=value)
    def test_invalid_dpi(self):
        with self.assertRaises(core.ContractError):self.intent(dpi='600')
    def test_invalid_ia(self):
        with self.assertRaises(core.ContractError):self.intent(ai='ENABLED')
    def test_summary_not_proof_inference(self):
        text=reporting.render_express_report({'nombre_objets_exportes':3},self.intent(ai='Si disponible'),'')
        self.assertIn('exécution à confirmer',text)
        self.assertIn('NON CERTIFIÉE',text)
    def test_summary_bad_qa_values_are_ignored(self):
        payload={'nombre_objets_exportes':1,'controle_v212':{'alertes':{'test':'str','ok':2}}}
        self.assertIn('2 alerte(s)',reporting.render_express_report(payload,self.intent(),''))
    def test_summary_is_bounded(self):
        self.assertLess(len(reporting.render_express_report({'nombre_objets_exportes':0},self.intent(),'a'*90000)),1550)
    def test_parse_safe(self):
        self.assertEqual(reporting.checked_report('{"a":1}'),{'a':1})
        for data in ('[]','"foo"','{', 'x'*99):
            with self.subTest(data=data),self.assertRaises((ValueError,json.JSONDecodeError)):
                reporting.checked_report(data,max_characters=50)
    def test_registry_preserves_id(self):
        current={'future':(object(),'Future')}
        classes,names=registry.merge_registry({'old':int},{'old':'Old'},current)
        self.assertIs(classes['old'],int);self.assertEqual(names['old'],'Old')
        with self.assertRaises(ValueError):registry.merge_registry({'old':int},{'old':'Old'},{'old':(int,'wrong')})
    def test_registry_mismatched_legacy_rejected(self):
        with self.assertRaises(ValueError):registry.merge_registry({'old':int},{}, {})
    def test_svg_root_width_and_no_spoof(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'one.svg'
            p.write_text('<!-- <svg width="1mm"/> --><svg width="42.5mm"/>',encoding='utf8')
            self.assertEqual(svg.svg_physical_width(p),42.5)
            p.write_text('<!DOCTYPE svg><svg width="99mm"/>',encoding='utf8')
            with self.assertRaises(ValueError):svg.svg_physical_width(p)
            p.write_text('<svg width="500px"/>',encoding='utf8')
            self.assertIsNone(svg.svg_physical_width(p))
    def test_svg_reject_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'valid.svg';p.write_text('<svg width="40mm"/>')
            link=Path(d)/'link.svg';link.symlink_to(p)
            with self.assertRaises(ValueError):svg.svg_physical_width(link)
    def test_png_svg_inspection_readonly(self):
        d={'objets':[{'controle_physique_v211':{'largeur_png_mm_si_ppp_respectes':40,'largeur_svg_mm':40.2}},
                     {'controle_physique_v211':{'largeur_png_mm_si_ppp_respectes':40,'largeur_svg_mm':90}}]}
        self.assertEqual(cricut.report_dimension_disagreements(d),['OBJET_2_PNG_SVG_TAILLES_INCOHERENTES'])
    def test_current_nodes_legacy_unchanged(self):
        self.assertEqual(set(node.NODE_CLASS_MAPPINGS)-set(old.NODE_CLASS_MAPPINGS),
                         {'SmartSVGExpressV214','SmartSVGInstancesV214','SmartSVGDiagnosticV214'})
        for k,c in old.NODE_CLASS_MAPPINGS.items():self.assertIs(node.NODE_CLASS_MAPPINGS[k],c)
    def test_current_ports_identical(self):
        for a,b in [(node.SmartSVGExpressV214,old.SmartSVGExpressV2132),
                    (node.SmartSVGInstancesV214,old.SmartSVGInstancesV2132),
                    (node.SmartSVGDiagnosticV214,old.SmartSVGDiagnosticV2132)]:
            self.assertEqual(a.INPUT_TYPES(),b.INPUT_TYPES())
            self.assertEqual(a.RETURN_TYPES,b.RETURN_TYPES)
            self.assertEqual(a.FUNCTION,b.FUNCTION)
    def test_diagnostic_no_models_loaded(self):
        from sv214test.smartsvg_ai.hardware import diagnostic_report,summary
        result=diagnostic_report({},None)
        self.assertFalse(result['modeles_poids_charges_et_testes'])
        self.assertIn('Aucun modèle',summary(result))
    def test_new_workflows_have_matching_ports(self):
        files=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_4_*.json'))
        self.assertEqual(len(files),8)
        for wf in files:
            graph=json.loads(wf.read_text(encoding='utf8'))
            for item in graph['nodes']:
                if item['type'] not in node.NODE_CLASS_MAPPINGS:continue
                cls=node.NODE_CLASS_MAPPINGS[item['type']]
                self.assertEqual([x['name'] for x in item['inputs']],
                  list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{})))
                self.assertEqual([o['type'] for o in item['outputs']],list(cls.RETURN_TYPES))

class V214Output(unittest.TestCase):
    def test_no_legacy_export_changes(self):
        # Output comparison across actual old/current ComfyUI nodes, no mocked exporter.
        im=np.ones((1,84,64,3),np.float32)
        im[:,18:70,12:55,:]=[.75,.45,.2]
        tensor=torch.from_numpy(im)
        with tempfile.TemporaryDirectory() as d:
            args=dict(image=tensor,projet='Carte - visuel rectangulaire',largeur_mm=40.,qualite_ppp='300',ia_locale='Desactivee')
            oldresult=old.SmartSVGExpressV2132().run(dossier_sortie=d+'/old',**args)
            result=node.SmartSVGExpressV214().run(dossier_sortie=d+'/new',**args)
            a=json.loads(oldresult['result'][2]);b=json.loads(result['result'][2]);
            def prod_hashes(r):
                p=Path(r['dossier'])
                return sorted((f.name,sha(f)) for f in p.rglob('*') if f.suffix.lower() in ('.png','.svg'))
            self.assertEqual(prod_hashes(a),prod_hashes(b))
            self.assertIn('NON CERTIFIÉE',result['result'][1]);self.assertEqual(a['nombre_objets_exportes'],b['nombre_objets_exportes'])

if __name__=='__main__':unittest.main()
