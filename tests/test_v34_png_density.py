"""V34-129 / T-V34-17-02 partial: do not approve contradictory PNG PPI.

Run the actual dependency-free production helper as in the handoff tests.
Real PNG decode/copy is additionally exercised by the CPU workflow.
"""
import ast
import math
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1]/'engine/smartsvg_cricut/direct_import_v218.py'


def density_helper():
    module = ast.parse(SOURCE.read_text())
    function = next(node for node in module.body
                    if isinstance(node, ast.FunctionDef) and node.name == '_check_png_density')
    class ImportAuditError(ValueError): pass
    namespace = dict(math=math, ImportAuditError=ImportAuditError)
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace['_check_png_density'], ImportAuditError


class PNGDensityTests(unittest.TestCase):
    def test_native_png_rounding_of_both_supported_densities_is_accepted(self):
        check, _ = density_helper()
        for axes, dpi in [((299.9994,299.9994),300),((450.0118,450.0118),450)]:
            with self.subTest(dpi=dpi):
                result = check(axes, dpi)
                self.assertEqual(result['densite_metadata_axes_ppp'], [round(v,2) for v in axes])
                self.assertEqual(result['densite_metadata_ppp'], round(axes[0],2))

    def test_conflicting_or_anisotropic_density_fails_closed(self):
        check, error = density_helper()
        for axes in [(450,450),(300,450),(450,300),(72,72)]:
            with self.subTest(axes=axes):
                with self.assertRaisesRegex(error, 'Densite PNG incoherente'): check(axes,300)

    def test_missing_metadata_retains_legacy_explicit_manufacturing_ppi_with_warning(self):
        check, _ = density_helper()
        result = check(None, 300)
        self.assertIsNone(result['densite_metadata_ppp'])
        self.assertIsNone(result['densite_metadata_axes_ppp'])
        self.assertIn('absentes', result['densite_avertissement'])
        self.assertIn('fabrication', result['densite_avertissement'])

    def test_malformed_metadata_is_not_silently_treated_as_absent(self):
        check, error = density_helper()
        for metadata in ['', '300', {}, [], [300], [300,300,300], (True,300),
                         (0,300),(-1,300),(float('nan'),300),(300,float('inf')),(10**500,300)]:
            with self.subTest(metadata=repr(metadata)):
                with self.assertRaisesRegex(error, 'Metadonnees PPP PNG invalides'): check(metadata,300)

    def test_density_inspection_without_manufacturing_ppi_retains_both_axes(self):
        check, _ = density_helper()
        result = check((300,450),None)
        self.assertEqual(result['densite_metadata_axes_ppp'], [300,450])
