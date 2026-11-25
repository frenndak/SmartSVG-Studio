"""W05 SD0-A: pure metadata planning; no fictional export or physical QA."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_delivery_plan_v35 import (
    DeliveryPlanError, plan_delivery, MAX_ITEM_BYTES, MAX_TOTAL_BYTES,
)


def fixture(role="PNG_PTC", *, item_id="a", target=None):
    png = role == "PNG_PTC"
    return {
        "item_id": item_id,
        "source_locator": "/local/private/not-published.png",
        "size_bytes": 1024,
        "sha256": "a" * 64,
        "media_type": "image/png" if png else "image/svg+xml",
        "role": role,
        "target_relpath": target or (item_id + (".png" if png else ".svg")),
        "dimensions": dict(width_mm=60.0, height_mm=40.0, confirmed=True,
                           provenance="USER_CONFIRMED",
                           **({"width_px": 600, "height_px": 400} if png else {})),
        "operation_context": dict(
            operations=["PRINT_THEN_CUT" if png else ("EDIT" if role == "SVG_EDITABLE" else "CUT")],
            attach_required=False, mirror_required=False),
        "qa": [dict(check_id="schema", status="PASS", reason=None)],
        "machine_context": dict(capability="UNKNOWN", availability="UNKNOWN", profile=None),
        "share_decision": dict(status="ALLOWED", basis="OWNER_DECLARED"),
        "guidance": dict(steps=["Vérifier dans Design Space."], optional_html=False),
    }


def context():
    return dict(plan_id="plan-001",
                project_ref=dict(kind="project", project_id="proj-01", sha256="b" * 64),
                policy_version="delivery-quota/1-draft")


def planned(items, selection=None):
    return plan_delivery(items=items,
                         selection=selection or [i["item_id"] for i in items],
                         context=context())


class DeliveryPlanSchemaTests(unittest.TestCase):
    def test_png_only_no_svg_required_and_no_fabricated_pass(self):
        p = planned([fixture()])
        d = p.as_dict()
        self.assertEqual(d["schema"], "smartsvg-delivery-plan/1-draft")
        self.assertEqual(d["admission"], "EXPORT_UNVERIFIED")
        self.assertEqual(d["items"][0]["admission"], "EXPORT_UNVERIFIED")
        self.assertFalse(d["actual_source_verified"])
        self.assertFalse(d["physical_cut_tested"])
        self.assertFalse(d["design_space_import_tested"])
        self.assertIn("SOURCE_NOT_VERIFIED", d["items"][0]["reasons"])

    def test_four_roles_remain_distinct(self):
        roles = ("PNG_PTC", "SVG_BASIC_CUT", "SVG_MULTILAYER_CUT", "SVG_EDITABLE")
        items = [fixture(role, item_id="i" + str(i)) for i, role in enumerate(roles)]
        p = planned(items)
        self.assertEqual([i["role"] for i in p.as_dict()["items"]], list(roles))
        self.assertEqual(len(p.as_dict()["selected_item_ids"]), 4)

    def test_digest_is_deterministic_and_returned_data_cannot_mutate_snapshot(self):
        p = planned([fixture()])
        again = planned([fixture()])
        self.assertEqual(p.sha256, again.sha256)
        self.assertEqual(p.canonical_json, again.canonical_json)
        p.as_dict()["items"][0]["source_locator"] = "/modified"
        self.assertEqual(p.sha256, again.sha256)
        self.assertEqual(p.as_dict()["items"][0]["source_locator"],
                         "/local/private/not-published.png")
        self.assertEqual(json.dumps(p.as_dict(), ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode(), p.canonical_json)

    def test_omissions_are_explicit_and_selection_cannot_silently_invent_id(self):
        p = planned([fixture(item_id="a"), fixture(item_id="b")], selection=["b"])
        self.assertEqual(p.as_dict()["omitted_item_ids"], ["a"])
        self.assertEqual(p.selected_item_ids, ("b",))
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_SELECTION"):
            planned([fixture()], selection=["a", "nonexistent"])
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_SELECTION"):
            planned([fixture()], selection=["a", "a"])

    def test_unconfirmed_physical_size_is_blocked_not_zero_or_false_pass(self):
        a = fixture()
        a["dimensions"].update(width_mm=None, height_mm=None, confirmed=False, provenance=None)
        p = planned([a])
        self.assertEqual(p.admission, "BLOCKED")
        self.assertIn("PHYSICAL_SIZE_UNCONFIRMED", p.reasons)
        for invalid in (0, -1, True, float("nan"), float("inf"), 10 ** 400):
            b = fixture()
            b["dimensions"]["width_mm"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(DeliveryPlanError):
                planned([b])

    def test_rights_denied_and_review_required_never_qualify(self):
        for right, code in (("DENIED", "RIGHTS_DENIED"),
                            ("REVIEW_REQUIRED", "RIGHTS_REVIEW_REQUIRED")):
            a = fixture()
            a["share_decision"]["status"] = right
            with self.subTest(right=right):
                self.assertIn(code, planned([a]).reasons)
                self.assertEqual(planned([a]).admission, "BLOCKED")

    def test_qa_fail_is_blocked_unknown_remains_unverified(self):
        for status, reason in (("FAIL", "BROKEN_SVG"), ("UNKNOWN", "NOT_TESTED"),
                               ("NOT_APPLICABLE", "OTHER_ROLE")):
            a = fixture()
            a["qa"][0].update(status=status, reason=reason)
            p = planned([a])
            self.assertEqual(p.admission, "BLOCKED" if status == "FAIL" else "EXPORT_UNVERIFIED")
            if status == "FAIL":
                self.assertIn("QA_BLOCKED", p.reasons)
        b = fixture()
        b["qa"][0].update(status="UNKNOWN", reason=None)
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_QA"):
            planned([b])

    def test_machine_unsupported_blocks_but_unknown_is_not_certificate(self):
        a = fixture()
        self.assertIn("MACHINE_CAPABILITY_UNKNOWN", planned([a]).as_dict()["items"][0]["reasons"])
        a["machine_context"]["capability"] = "UNSUPPORTED"
        self.assertIn("MACHINE_OPERATION_UNSUPPORTED", planned([a]).reasons)

    def test_unsafe_paths_and_case_nfc_duplicates(self):
        for target in ("../a.png", "/root/a.png", "C:/a.png", "CON.png",
                       "CON .png", "COM¹.png", "LPT².png", "COM³.png",
                       "foo\\bar.png", "x//a.png", "x/./a.png", "a?.png",
                       "a .png ", "a.png\x00", "a.png\n"):
            a = fixture(target=target)
            with self.subTest(target=repr(target)), self.assertRaises(DeliveryPlanError):
                planned([a])
        a = fixture(item_id="a", target="Résumé.png")
        b = fixture(item_id="b", target="Re\u0301sume\u0301.PNG")
        with self.assertRaisesRegex(DeliveryPlanError, "DUPLICATE_TARGET"):
            planned([a, b])
        with self.assertRaisesRegex(DeliveryPlanError, "DUPLICATE_TARGET"):
            planned([fixture(item_id="a", target="One.png"),
                     fixture(item_id="b", target="one.PNG")])

    def test_quota_boundaries_and_invalid_role(self):
        a = fixture()
        a["size_bytes"] = MAX_ITEM_BYTES
        self.assertEqual(planned([a]).admission, "EXPORT_UNVERIFIED")
        a["size_bytes"] = MAX_ITEM_BYTES + 1
        with self.assertRaisesRegex(DeliveryPlanError, "BUDGET_EXCEEDED"):
            planned([a])
        many = []
        for i in range(5):
            f = fixture(item_id="q" + str(i))
            f["size_bytes"] = MAX_ITEM_BYTES
            many.append(f)
        self.assertEqual(planned(many, selection=["q0"]).admission, "EXPORT_UNVERIFIED")
        self.assertEqual(len(planned(many, selection=["q0"]).as_dict()["omitted_item_ids"]), 4)
        with self.assertRaisesRegex(DeliveryPlanError, "BUDGET_EXCEEDED"):
            planned(many)
        a = fixture()
        a["role"] = "PRINT_THEN_CUT"
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_ARTIFACT_ROLE"):
            planned([a])
        with self.assertRaisesRegex(DeliveryPlanError, "BUDGET_EXCEEDED"):
            planned([fixture()] * 501)

    def test_strict_shapes_and_no_unexpected_fields(self):
        a = fixture()
        a["secret_override"] = "danger"
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_ITEM"):
            planned([a])
        c = context()
        c["policy_version"] = "delivery-quota/unbounded"
        with self.assertRaisesRegex(DeliveryPlanError, "UNSUPPORTED_POLICY"):
            plan_delivery(items=[fixture()], selection=["a"], context=c)
        c = context()
        c["project_ref"]["sha256"] = "bad"
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_DIGEST"):
            plan_delivery(items=[fixture()], selection=["a"], context=c)

    def test_print_then_cut_is_not_an_svg_operation_and_basic_cut_is_cut_only(self):
        basic = fixture("SVG_BASIC_CUT")
        basic["operation_context"]["operations"].append("PRINT_THEN_CUT")
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_OPERATIONS"):
            planned([basic])
        editable = fixture("SVG_EDITABLE")
        editable["operation_context"]["operations"] = ["EDIT", "PRINT_THEN_CUT"]
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_OPERATIONS"):
            planned([editable])
        png = fixture()
        png["operation_context"]["operations"].append("CUT")
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_OPERATIONS"):
            planned([png])
        multilayer = fixture("SVG_MULTILAYER_CUT")
        multilayer["operation_context"]["operations"] = ["CUT", "SCORE", "DRAW"]
        self.assertEqual(planned([multilayer]).admission, "EXPORT_UNVERIFIED")

    def test_unhashable_role_and_qa_status_fail_with_public_error(self):
        a = fixture()
        a["role"] = ["SVG_BASIC_CUT"]
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_ARTIFACT_ROLE"):
            planned([a])
        b = fixture()
        b["qa"][0]["status"] = ["FAIL"]
        with self.assertRaisesRegex(DeliveryPlanError, "INVALID_QA"):
            planned([b])

    def test_manual_transfer_guidance_required_even_without_html(self):
        for operation in ("SCORE", "DRAW", "FOIL"):
            a = fixture("SVG_MULTILAYER_CUT")
            a["operation_context"]["operations"] = ["CUT", operation]
            a["guidance"]["steps"] = []
            with self.subTest(operation=operation), self.assertRaisesRegex(
                    DeliveryPlanError, "INVALID_GUIDANCE"):
                planned([a])
            a["guidance"]["steps"] = ["Assign " + operation + " in Design Space."]
            p = planned([a])
            self.assertEqual(p.admission, "EXPORT_UNVERIFIED")
            self.assertFalse(p.as_dict()["items"][0]["guidance"]["optional_html"])
            self.assertEqual(p.as_dict()["items"][0]["guidance"]["steps"],
                             a["guidance"]["steps"])
        for flag in ("attach_required", "mirror_required"):
            a = fixture("SVG_BASIC_CUT")
            a["operation_context"][flag] = True
            for steps in ([], ["   "]):
                a["guidance"]["steps"] = steps
                with self.subTest(flag=flag, steps=steps), self.assertRaisesRegex(
                        DeliveryPlanError, "INVALID_GUIDANCE"):
                    planned([a])
            a["guidance"]["steps"] = ["Confirm " + flag + " before import."]
            self.assertEqual(planned([a]).admission, "EXPORT_UNVERIFIED")
        simple = fixture("SVG_BASIC_CUT")
        simple["guidance"]["steps"] = []
        self.assertEqual(planned([simple]).admission, "EXPORT_UNVERIFIED")

    def test_no_file_open_or_write_during_plan(self):
        from unittest.mock import patch
        import builtins
        with patch.object(builtins, "open", side_effect=AssertionError("I/O forbidden")):
            p = planned([fixture()])
            self.assertEqual(p.admission, "EXPORT_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
