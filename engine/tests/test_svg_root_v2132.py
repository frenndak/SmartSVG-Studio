"""Reproduction of SVG root-width spoofing and its fix."""
import importlib,sys,types,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if 'sv2132root' not in sys.modules:
    pkg=types.ModuleType('sv2132root');pkg.__path__=[str(ROOT)];sys.modules['sv2132root']=pkg
m=importlib.import_module('sv2132root.controle_export_v212')
class SVGParserAudit(unittest.TestCase):
    def check_file(self,content):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.svg';p.write_text(content,encoding='utf8')
            return m._svg_width_mm(p)
    def test_real_root_not_fake_comment(self):
        self.assertEqual(self.check_file('<!-- <svg width="42mm" --> <svg xmlns="http://www.w3.org/2000/svg" width="140mm"/>'),140)
    def test_read_real_svg_with_xml_decl(self):
        self.assertEqual(self.check_file('<?xml version="1.0"?><svg width="36.3mm" height="30mm"><path d="M0 0"/></svg>'),36.3)
    def test_reject_entities(self):
        with self.assertRaises(m.QAError):
            self.check_file('<!DOCTYPE svg [<!ENTITY x "bad">]><svg width="40mm"/>')
    def test_invalid_svg_fails(self):
        with self.assertRaises(m.QAError):self.check_file('<svg width="42mm"><path></svg>')
    def test_wrong_root_not_accepted(self):
        self.assertIsNone(self.check_file('<x><svg width="42mm"/></x>'))
    def test_no_mm_is_unverified(self):
        self.assertIsNone(self.check_file('<svg width="120px"/>'))
