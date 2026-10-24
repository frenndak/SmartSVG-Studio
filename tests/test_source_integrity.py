"""Exact reproducible source-integrity acceptance test on the imported distribution."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_source_integrity import check_source


class ImportedV21152Tests(unittest.TestCase):
    def test_original_zip_and_complete_engine_are_identical(self):
        result = check_source(ROOT)
        self.assertEqual(result["status"], "source_integrity_passed")
        self.assertEqual(result["manifest_file_hashes_verified"], 651)
        self.assertEqual(result["extracted_files_compared"], 652)
        self.assertEqual(result["original_zip_sha256"],
                         "9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54")
        self.assertFalse(result["complete_runtime_tests"])
        self.assertFalse(result["physical_cricut_verified"])
        self.assertFalse(result["gpu_inference_verified"])


if __name__ == "__main__":
    unittest.main()
