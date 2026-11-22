"""W04 vector geometry, physical units, topology and fail-closed readback."""
import hashlib
import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from smartsvg_core.native_basic_cut_v35 import BasicCutError,preview_basic_cut

OUTER=((0,0),(20,0),(20,10),(0,10))
HOLE=((5,2),(10,2),(10,6),(5,6))

class BasicCutTests(unittest.TestCase):
    def test_mm_vector_hole_readback(self):
        result=preview_basic_cut(rings=(OUTER,HOLE),width_mm=20,height_mm=10)
        root=ET.fromstring(result.svg)
        path=root.find("{http://www.w3.org/2000/svg}path")
        self.assertEqual((root.get("width"),root.get("height"),root.get("viewBox")),("20mm","10mm","0 0 20 10"))
        self.assertEqual(path.get("fill-rule"),"evenodd")
        self.assertEqual(path.get("d").count(" Z"),2)
        self.assertEqual(hashlib.sha256(result.svg).hexdigest(),result.sha256)
        self.assertTrue(result.verified_readback)
        self.assertFalse(result.physical_cut_tested)

    def test_invalid_geometry_then_recovery(self):
        invalid=[(((0,0),(10,10),(0,10),(10,0)),),
                 (OUTER,((25,1),(26,1),(26,2))),
                 (OUTER,((5,0),(10,0),(10,4),(5,4))),
                 (OUTER,HOLE,((6,3),(7,3),(7,4),(6,4)))]
        for rings in invalid:
            with self.subTest(rings=rings),self.assertRaises(BasicCutError):
                preview_basic_cut(rings=rings,width_mm=20,height_mm=10)
            self.assertTrue(preview_basic_cut(rings=(OUTER,),width_mm=20,height_mm=10).verified_readback)

    def test_nonfinite_bool_and_bounds(self):
        for width in (True,float("nan"),float("inf"),0,-1,10001,19):
            with self.subTest(width=width),self.assertRaises(BasicCutError):
                preview_basic_cut(rings=(OUTER,),width_mm=width,height_mm=10)

    def test_fractional_coordinates_survive_svg_readback(self):
        """SVG serialization must not silently quantize sub-0.1 mm contours."""
        contour=((0.00001,0.00001),(19.99999,0.00001),(19.99999,9.99999),(0.00001,9.99999))
        result=preview_basic_cut(rings=(contour,),width_mm=20,height_mm=10)
        root=ET.fromstring(result.svg)
        path=root.find("{http://www.w3.org/2000/svg}path")
        data=path.get("d")
        coords = data.replace("M ", "").replace(" L ", " ").replace(" Z", "").split()
        self.assertEqual(len(coords), 8)
        self.assertEqual(float(coords[0]), contour[0][0])
        self.assertEqual(float(coords[1]), contour[0][1])
        self.assertEqual(float(coords[2]), contour[1][0])
        self.assertNotEqual(float(coords[0]), 0.0)
        self.assertNotEqual(float(coords[2]), float(coords[0]))
        self.assertEqual(hashlib.sha256(result.svg).hexdigest(),result.sha256)

    def test_close_vertices_preserved_without_rounding_collapse(self):
        """A valid narrow cut must not collapse during SVG serialization."""
        ring=((1,1),(1.00002,1),(1.00002,2),(1,2))
        result=preview_basic_cut(rings=(ring,),width_mm=20,height_mm=10)
        path=ET.fromstring(result.svg).find("{http://www.w3.org/2000/svg}path")
        # Float serialization may use an equivalent long decimal spelling.
        coords = path.get("d").replace("M ", "").replace(" L ", " ").replace(" Z", "").split()
        self.assertAlmostEqual(float(coords[2]), 1.00002, places=12)
        self.assertGreater(float(coords[2]) - float(coords[0]), 0.0000199999)
        self.assertEqual(path.get("d").count(" L "),3)
        self.assertTrue(result.verified_readback)

    def test_total_topology_budget_rejects_large_ring_before_quadratic_scan(self):
        """An oversized yet finite contour must fail fast and not poison later work."""
        import math
        huge = tuple((10 + 9 * math.cos(2 * math.pi * i / 513),
                      5 + 4 * math.sin(2 * math.pi * i / 513))
                     for i in range(513))
        with self.assertRaisesRegex(BasicCutError, "GEOMETRY_TOO_COMPLEX"):
            preview_basic_cut(rings=(huge,), width_mm=20, height_mm=10)
        self.assertTrue(preview_basic_cut(
            rings=(OUTER, HOLE), width_mm=20, height_mm=10).verified_readback)

    def test_many_rings_share_one_global_budget(self):
        """Small individual rings must not bypass the aggregate edge ceiling."""
        outer = tuple((10 + 9 * __import__("math").cos(2 * __import__("math").pi * i / 500),
                       5 + 4 * __import__("math").sin(2 * __import__("math").pi * i / 500))
                      for i in range(500))
        with self.assertRaisesRegex(BasicCutError, "GEOMETRY_TOO_COMPLEX"):
            preview_basic_cut(rings=(outer, HOLE, HOLE, HOLE, HOLE),
                              width_mm=20, height_mm=10)

    def test_tiny_but_nonzero_hole_and_recovery_after_boundary_contact(self):
        """Preserve a thin disjoint hole; reject a touching hole fail-closed."""
        thin=((5,2),(5.00002,2),(5.00002,4),(5,4))
        valid=preview_basic_cut(rings=(OUTER,thin),width_mm=20,height_mm=10)
        self.assertEqual(valid.ring_count,2)
        self.assertIn("5.00002",ET.fromstring(valid.svg).find("{http://www.w3.org/2000/svg}path").get("d"))
        touching=((0,2),(1,2),(1,4),(0,4))
        with self.assertRaises(BasicCutError):
            preview_basic_cut(rings=(OUTER,touching),width_mm=20,height_mm=10)
        self.assertEqual(preview_basic_cut(rings=(OUTER,HOLE),width_mm=20,height_mm=10).ring_count,2)


    def test_multiple_disjoint_holes_and_touching_holes_rejected(self):
        """Independent cutouts are valid; shared vertex/edge must fail closed."""
        left=((2,2),(5,2),(5,5),(2,5))
        right=((12,2),(15,2),(15,5),(12,5))
        result=preview_basic_cut(rings=(OUTER,left,right),width_mm=20,height_mm=10)
        self.assertEqual(result.ring_count,3)
        self.assertEqual(ET.fromstring(result.svg).find(
            "{http://www.w3.org/2000/svg}path").get("d").count(" Z"),3)
        self.assertEqual(hashlib.sha256(result.svg).hexdigest(),result.sha256)
        touching_vertex=((5,5),(8,5),(8,8),(5,8))
        touching_edge=((5,2),(8,2),(8,5),(5,5))
        for second in (touching_vertex,touching_edge):
            with self.subTest(second=second),self.assertRaisesRegex(
                    BasicCutError,"RINGS_INTERSECT"):
                preview_basic_cut(rings=(OUTER,left,second),width_mm=20,height_mm=10)
            self.assertTrue(preview_basic_cut(
                rings=(OUTER,left,right),width_mm=20,height_mm=10).verified_readback)

    def test_concave_outer_rejects_hole_edges_crossing_open_notch(self):
        """All hole vertices may be inside while an edge crosses outside."""
        outer = ((0, 0), (20, 0), (20, 20), (14, 20),
                 (14, 6), (6, 6), (6, 20), (0, 20))
        valid = ((1, 10), (3, 10), (3, 12), (1, 12))
        crossing = ((4, 12), (16, 12), (16, 14), (4, 14))
        self.assertTrue(preview_basic_cut(
            rings=(outer, valid), width_mm=20, height_mm=20).verified_readback)
        with self.assertRaisesRegex(BasicCutError, "RINGS_INTERSECT"):
            preview_basic_cut(rings=(outer, crossing), width_mm=20, height_mm=20)
        recovered = preview_basic_cut(
            rings=(outer, valid), width_mm=20, height_mm=20)
        self.assertEqual(hashlib.sha256(recovered.svg).hexdigest(), recovered.sha256)

    def test_deterministic_readback_does_not_mutate_input_rings(self):
        """Repeated previews preserve caller geometry and stable SVG/SHA."""
        outer = [[0, 0], [20, 0], [20, 10], [0, 10]]
        hole = [[5, 2], [10, 2], [10, 6], [5, 6]]
        rings = [outer, hole]
        before = [list(map(list, ring)) for ring in rings]
        first = preview_basic_cut(rings=rings, width_mm=20, height_mm=10)
        second = preview_basic_cut(rings=rings, width_mm=20, height_mm=10)
        self.assertEqual(rings, before)
        self.assertEqual(first.svg, second.svg)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(hashlib.sha256(first.svg).hexdigest(), first.sha256)
        self.assertTrue(first.verified_readback)
        self.assertFalse(first.physical_cut_tested)

    def test_disjoint_holes_with_narrow_gap_remain_distinct(self):
        """A narrow positive gap is not an edge touch or nested hole."""
        left = ((2, 2), (5, 2), (5, 5), (2, 5))
        right = ((5.001, 2), (8, 2), (8, 5), (5.001, 5))
        result = preview_basic_cut(rings=(OUTER, left, right),
                                   width_mm=20, height_mm=10)
        path = ET.fromstring(result.svg).find("{http://www.w3.org/2000/svg}path")
        self.assertEqual(path.get("d").count(" Z"), 3)
        self.assertEqual(result.ring_count, 3)
        self.assertEqual(hashlib.sha256(result.svg).hexdigest(), result.sha256)
