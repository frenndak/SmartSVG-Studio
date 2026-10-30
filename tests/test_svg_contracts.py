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

    def test_non_finite_explicit_mm_rejected(self):
        # A decimal with hundreds of digits converts to float('inf').
        huge_mm = "9" * 400 + "mm"
        for width, height in ((huge_mm, "25mm"), ("20mm", huge_mm)):
            with self.subTest(width=width[:12], height=height[:12]):
                p = self.write(self.base('<circle r="8"/>', width=width, height=height))
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

    def test_escaped_css_url_rejected_in_inline_style(self):
        # CSS consumers decode \72 and \75 to 'r' and 'u' respectively.
        for css in (
            r"fill:u\72l(https://example.invalid/x)",
            r"fill:\75rl(https://example.invalid/x)",
            r"fill:u\000072l(https://example.invalid/x)",
        ):
            with self.subTest(css=css):
                p = self.write(self.base('<circle r="8" style="' + css + '"/>'))
                with self.assertRaisesRegex(SVGRejected, "OBFUSCATED_CSS_REFERENCE"):
                    inspect_svg(p)

    def test_escaped_css_url_rejected_in_presentation_attribute(self):
        p = self.write(self.base(r'<circle r="8" fill="u\72l(https://example.invalid/x)"/>'))
        with self.assertRaisesRegex(SVGRejected, "OBFUSCATED_CSS_REFERENCE"):
            inspect_svg(p)

    def test_css_comment_obfuscation_rejected(self):
        p = self.write(self.base('<circle r="8" style="fill:u/**/rl(https://example.invalid/x)"/>'))
        with self.assertRaisesRegex(SVGRejected, "OBFUSCATED_CSS_REFERENCE"):
            inspect_svg(p)

    def test_safe_inline_css_remains_accepted(self):
        p = self.write(self.base('<circle r="8" style="fill:#123456;stroke:none;opacity:.5"/>'))
        self.assertEqual(inspect_svg(p)["vector_elements"], 1)

    def test_xml_event_handler(self):
        p = self.write(self.base('<circle r="4" onload="alert(1)"/>'))
        with self.assertRaisesRegex(SVGRejected, "EVENT_OR_EXTERNAL"):
            inspect_svg(p)

    def test_xml_stylesheet_processing_instruction_rejected(self):
        p = self.write('<?xml version="1.0"?>\n<?xml-stylesheet href="https://example.invalid/evil.css"?>' +
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

    def test_definition_only_svg_is_not_counted_as_cut_geometry(self):
        # SVG declarations and clip/mask/marker/pattern geometry are not
        # rendered directly. They cannot qualify an empty cut file.
        for container in ("defs", "symbol", "clipPath", "mask", "pattern", "marker"):
            with self.subTest(container=container):
                body = (f'<{container} id="unused">'
                        '<path d="M0 0 L10 0 L10 10 Z"/>'
                        f'</{container}>')
                p = self.write(self.base(body))
                with self.assertRaisesRegex(SVGRejected, "NO_VECTOR_GEOMETRY"):
                    inspect_svg(p)

    def test_visible_shapes_count_excludes_definition_descendants(self):
        body = ('<defs><g><path d="M0 0 L10 0 L10 10 Z"/></g></defs>'
                '<g><circle cx="5" cy="5" r="2"/></g>')
        p = self.write(self.base(body))
        result = inspect_svg(p)
        self.assertEqual(result["vector_elements"], 1)
        self.assertFalse(result["physical_cut_verified"])
        with self.assertRaisesRegex(SVGRejected, "INSUFFICIENT_SEPARATE"):
            inspect_svg(p, profile="editable")

    def test_display_none_group_does_not_fake_visible_cut_geometry(self):
        # A group or the root can hide all descendants, despite valid paths.
        hidden = (
            '<g display="none"><circle r="8"/></g>',
            '<g style="fill:red; display : none !important"><path d="M0 0 L2 0 Z"/></g>',
            '<path d="M0 0 L2 0 Z" style="display:none;stroke:red"/>',
        )
        for body in hidden:
            with self.subTest(body=body):
                p = self.write(self.base(body))
                with self.assertRaisesRegex(SVGRejected, "NO_VECTOR_GEOMETRY"):
                    inspect_svg(p)

    def test_visible_sibling_is_kept_after_hidden_group(self):
        p = self.write(self.base(
            '<g style="display:none"><circle r="4"/></g>'
            '<g><rect width="5" height="5"/></g>'))
        self.assertEqual(inspect_svg(p)["vector_elements"], 1)

    def test_empty_cut_path(self):
        p = self.write(self.base('<path d=" "/>'))
        with self.assertRaisesRegex(SVGRejected, "EMPTY_PATH"):
            inspect_svg(p)


    def test_malformed_path_commands_rejected(self):
        bad_paths = (
            'garbage', 'L1 2', 'M0 0 L', 'M0 0 L1',
            'M0 0 L1 2 garbage', 'M0 0 L1e999 2',
            'M0 0 A 4 4 0 2 1 2 3', 'M0 0 A 4 4 0 0 2 2 3',
            'M0 0 A4 4 0 20 2 3', 'M0 0 A4 4 0 02 2 3',
            'M0 0 L1 2 Z 4 5', 'M0 0 L1 2,,3 4',
            'M,0 0 L1 2', 'M0 0,L1 2', 'M0 0 L1 2,Z',
            'M0 0 L1 2,M3 4',
        )
        for data in bad_paths:
            with self.subTest(data=data):
                p = self.write(self.base('<path d="' + data + '"/>'))
                with self.assertRaisesRegex(SVGRejected, 'INVALID_PATH_DATA|NONFINITE_PATH_DATA'):
                    inspect_svg(p)

    def test_move_only_path_is_not_cut_geometry(self):
        for data in ('M0 0', 'M0 0 Z'):
            with self.subTest(data=data):
                p = self.write(self.base('<path d="' + data + '"/>'))
                with self.assertRaisesRegex(SVGRejected, 'NO_DRAWING_PATH'):
                    inspect_svg(p)

    def test_valid_path_grammar_still_accepted(self):
        paths = (
            'M0 0 L10 10 Z',
            'M 40 680 Q 330 530 550 660 T 1060 665 L1060 790 Z',
            'M10-5h10v-5z',
            'm0 0 1 1 2 2',
            'M0 0 A 4 4 0 1 0 10 10',
            'M0 0 C0 0 2 2 3 3 S5 5 8 8',
            'M0 0 A4 4 0 01 2 3',       # adjacent arc flags
            'M0 0 A4 4 0 0110 10',     # flags and x adjacent
            'M0 0 A4 4 0 0 110 10',    # sweep flag and x adjacent
            'M0 0 A4 4 0 01-10 10',    # signed x adjacent
            'M0 0 A0 4 0 01 2 3',      # zero radius becomes line
            'M0 0 A-4 4 0 01 2 3',     # negative radius normalized
            'M0 0 A4 4 0 01 2 3 4 4 0 10 5 6',  # repeated arc
        )
        for data in paths:
            with self.subTest(data=data):
                p = self.write(self.base('<path d="' + data + '"/>'))
                result = inspect_svg(p)
                self.assertTrue(result['path_syntax_checked'])
                self.assertFalse(result['geometry_verified'])
                self.assertFalse(result['blade_path_verified'])

    def test_unverified_transform_rejected(self):
        for body in (
            '<path d="M0 0 L2 2" transform="scale(2)"/>',
            '<g transform="rotate(foo)"><circle r="8"/></g>',
        ):
            with self.subTest(body=body):
                p = self.write(self.base(body))
                with self.assertRaisesRegex(SVGRejected, 'UNVERIFIED_TRANSFORM'):
                    inspect_svg(p)

    def test_css_geometry_transforms_rejected(self):
        # CSS transforms can move cut paths just like SVG transform attributes.
        styles = (
            'transform:scale(2)',
            'fill:red; TRANSFORM : rotate(30deg)',
            'translate:10px 5px',
            'rotate:45deg',
            'scale:2',
            'offset-path:path(&quot;M0 0 L10 0&quot;)',
        )
        for style in styles:
            with self.subTest(style=style):
                p = self.write(self.base(
                    '<path d="M0 0 L2 2" style="' + style + '"/>'))
                with self.assertRaisesRegex(SVGRejected, 'UNVERIFIED_TRANSFORM'):
                    inspect_svg(p)

    def test_static_path_gate_never_certifies_geometry(self):
        p = self.write(self.base('<path d="M0 0 L0 0"/>'))
        result = inspect_svg(p)
        self.assertTrue(result['path_syntax_checked'])
        self.assertFalse(result['geometry_verified'])
        self.assertFalse(result['blade_path_verified'])
        self.assertFalse(result['design_space_import_verified'])
        self.assertFalse(result['physical_cut_verified'])



    def test_polygon_polyline_point_lists(self):
        # Syntax-only: point pairs must be finite and sufficiently numerous.
        valid = (
            ('polygon', '0,0 10,0 10,10'),
            ('polygon', '0 0, 10 0, 10 10, 0 10'),
            ('polyline', '0,0 10,10'),
            ('polyline', '-1.5,2e1 10,0 20,5'),
        )
        for tag, points in valid:
            with self.subTest(tag=tag, points=points):
                p = self.write(self.base(f'<{tag} points="{points}"/>'))
                result = inspect_svg(p)
                self.assertEqual(result['vector_elements'], 1)
                self.assertFalse(result['geometry_verified'])

    def test_malformed_polygon_polyline_point_lists_rejected(self):
        invalid = (
            ('polygon', 'garbage'),
            ('polygon', ''),
            ('polygon', '0,0 10,10'),        # fewer than three pairs
            ('polygon', '0,0 10,0 10'),     # odd coordinate count
            ('polygon', '0,0 10,0 10,nan'),
            ('polygon', '0,0 10,0 10,1e999'),
            ('polygon', '0,0,,10,0 10,10'),
            ('polygon', '0,0 10,0 10,10,'),
            ('polyline', '0,0'),            # fewer than two pairs
            ('polyline', '0,0 10,foo'),
        )
        for tag, points in invalid:
            with self.subTest(tag=tag, points=points):
                p = self.write(self.base(f'<{tag} points="{points}"/>'))
                with self.assertRaisesRegex(
                    SVGRejected, 'INVALID_POINTS_DATA|NONFINITE_POINTS_DATA'
                ):
                    inspect_svg(p)




if __name__ == "__main__":
    unittest.main()
