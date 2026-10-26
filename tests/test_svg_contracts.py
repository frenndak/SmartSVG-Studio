"""Deterministic checks for original, non-copyrighted SVG examples."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_svg_contracts import inspect_svg, SVGRejected


class SVGContractTests(unittest.TestCase):
    def write(self, content):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        p = Path(self.temp.name) / "case.svg"
        p.write_text(content, encoding="utf-8")
        return p

    def base(self, children, width="20mm", height="25mm", view="0 0 200 250"):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="' + width +
                '" height="' + height + '" viewBox="' + view + '">' + children + '</svg>')

    def test_all_original_examples_parse(self):
        files = sorted((ROOT / "examples" / "synthetic").glob("*.svg"))
        self.assertGreaterEqual(len(files), 5)
        for file in files:
            with self.subTest(file=file.name):
                result = inspect_svg(file)
                self.assertFalse(result["physical_cut_verified"])
                self.assertFalse(result["design_space_import_verified"])
                self.assertGreater(result["vector_elements"], 0)

    def test_multilayer_preflight_not_certification(self):
        p = ROOT / "examples" / "synthetic" / "03_multicouche_editable.svg"
        result = inspect_svg(p, profile="editable")
        self.assertGreater(result["vector_elements"], 2)
        self.assertFalse(result["vector_editability_guaranteed"])
        self.assertEqual(result["width_mm"], 110)

    def test_missing_namespace(self):
        p = self.write('<svg width="20mm" height="25mm" viewBox="0 0 20 25"><path d="M0 0 L1 1"/></svg>')
        with self.assertRaisesRegex(SVGRejected, "NOT_SVG_NAMESPACE"):
            inspect_svg(p)

    def test_relative_size_rejected(self):
        p = self.write(self.base('<circle r="8"/>', width="100%"))
        with self.assertRaisesRegex(SVGRejected, "EXPLICIT_MM_REQUIRED"):
            inspect_svg(p)

    def test_invalid_viewbox(self):
        p = self.write(self.base('<circle r="8"/>', view="0 0 nan 25"))
        with self.assertRaisesRegex(SVGRejected, "INVALID_VIEWBOX"):
            inspect_svg(p)

    def test_script_forbidden(self):
        p = self.write(self.base("<script>alert('x')</script><circle r='8'/>"))
        with self.assertRaisesRegex(SVGRejected, "EMBEDDED_RESOURCE"):
            inspect_svg(p)

    def test_embedded_image_forbidden(self):
        p = self.write(self.base('<image href="https://example.invalid/x.png" width="8"/>'))
        with self.assertRaisesRegex(SVGRejected, "EMBEDDED_RESOURCE"):
            inspect_svg(p)

    def test_external_url_forbidden(self):
        p = self.write(self.base('<path d="M1 1 L2 2" style="fill:url(https://example.invalid/x)"/>'))
        with self.assertRaisesRegex(SVGRejected, "EVENT_OR_EXTERNAL"):
            inspect_svg(p)

    def test_xml_event_handler(self):
        p = self.write(self.base('<circle r="4" onload="alert(1)"/>'))
        with self.assertRaisesRegex(SVGRejected, "EVENT_OR_EXTERNAL"):
            inspect_svg(p)

    def test_xml_stylesheet_processing_instruction_rejected(self):
        p = self.write('<?xml version="1.0"?>\\n<?xml-stylesheet href="https://example.invalid/evil.css"?>' +
                       self.base('<circle r="8"/>'))
        with self.assertRaisesRegex(SVGRejected, "PROCESSING_INSTRUCTION"):
            inspect_svg(p)

    def test_internal_processing_instruction_rejected(self):
        p = self.write(self.base('<?danger data?><circle r="8"/>'))
        with self.assertRaisesRegex(SVGRejected, "PROCESSING_INSTRUCTION"):
            inspect_svg(p)

    def test_style_element_rejected(self):
        p = self.write(self.base('<style>@import "https://example.invalid/evil.css";</style>' +
                                 '<circle r="8"/>'))
        with self.assertRaisesRegex(SVGRejected, "EMBEDDED_RESOURCE"):
            inspect_svg(p)

    def test_link_element_rejected(self):
        p = self.write(self.base('<a><circle r="8"/></a>'))
        with self.assertRaisesRegex(SVGRejected, "EMBEDDED_RESOURCE"):
            inspect_svg(p)

    def test_xml_declaration_and_comment_still_allowed(self):
        p = self.write('<?xml version="1.0" encoding="utf-8"?>' +
                       self.base('<!-- <?not-an-instruction?> --><circle r="8"/>'))
        self.assertEqual(inspect_svg(p)["vector_elements"], 1)

    def test_dtd_rejected(self):
        p = self.write('<!DOCTYPE svg [<!ENTITY x "hi">]>' + self.base('<path d="M1 1"/>'))
        with self.assertRaisesRegex(SVGRejected, "DTD_OR_ENTITY"):
            inspect_svg(p)

    def test_rasterized_wrapped_svg_not_accepted(self):
        p = self.write(self.base('<image href="data:image/png;base64,abc"/>'))
        with self.assertRaisesRegex(SVGRejected, "EMBEDDED_RESOURCE"):
            inspect_svg(p)

    def test_editable_profile_needs_separate_objects(self):
        p = self.write(self.base('<path d="M1 1 L2 2 Z"/>'))
        with self.assertRaisesRegex(SVGRejected, "INSUFFICIENT_SEPARATE"):
            inspect_svg(p, profile="editable")

    def test_empty_cut_path(self):
        p = self.write(self.base('<path d=" "/>'))
        with self.assertRaisesRegex(SVGRejected, "EMPTY_PATH"):
            inspect_svg(p)


if __name__ == "__main__":
    unittest.main()
