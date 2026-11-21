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
        self.assertIn("1.0000000000000001e-05",data)
        self.assertNotIn("M 0 0",data)
        self.assertEqual(hashlib.sha256(result.svg).hexdigest(),result.sha256)
