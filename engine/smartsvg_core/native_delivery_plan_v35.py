"""W05/SD0-A: read-only, deterministic delivery-plan admission.

Validates metadata and produces an immutable canonical snapshot. This module
does NOT open or authenticate source files, certify local QA/Design Space,
modify V1 projects, create ZIPs, or grant rights to redistribute assets.
An SD0-B reader must check the real bytes and provenance before publication.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
import unicodedata


SCHEMA = "smartsvg-delivery-plan/1-draft"
QUOTA = "delivery-quota/1-draft"
ROLE_MEDIA = {
    "PNG_PTC": "image/png",
    "SVG_BASIC_CUT": "image/svg+xml",
    "SVG_MULTILAYER_CUT": "image/svg+xml",
    "SVG_EDITABLE": "image/svg+xml",
}
MAX_ITEMS = 500
MAX_ITEM_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
MAX_CANONICAL_BYTES = 2 * 1024 * 1024
_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_WINDOWS_FORBIDDEN = frozenset('<>:"/\\|?*')
_WINDOWS_DEVICE = re.compile(r"(?:CON|PRN|AUX|NUL|(?:COM|LPT)[1-9¹²³]) *(?:\..*)?\Z", re.I)
_OPERATIONS = frozenset(("CUT", "PRINT_THEN_CUT", "SCORE", "DRAW", "FOIL", "EDIT"))
_QA_STATES = frozenset(("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"))


class DeliveryPlanError(ValueError):
    """Stable, non-disclosing error code for invalid delivery metadata."""


@dataclass(frozen=True)
class DeliveryPlan:
    canonical_json: bytes
    sha256: str
    admission: str
    reasons: tuple[str, ...]
    selected_item_ids: tuple[str, ...]

    def as_dict(self):
        """Fresh copy; callers cannot mutate the immutable canonical snapshot."""
        return json.loads(self.canonical_json)


def _keys(record, required, *, where):
    if type(record) is not dict or set(record) != set(required):
        raise DeliveryPlanError("INVALID_" + where)
    return record


def _text(value, *, code, limit=4096, empty=False):
    if type(value) is not str or len(value) > limit or (not empty and not value):
        raise DeliveryPlanError(code)
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise DeliveryPlanError(code)
    return value


def _identifier(value, code):
    if type(value) is not str or not _ID.fullmatch(value):
        raise DeliveryPlanError(code)
    return value


def _digest(value):
    if type(value) is not str or not _SHA.fullmatch(value):
        raise DeliveryPlanError("INVALID_DIGEST")
    return value


def _target_path(value):
    _text(value, code="UNSAFE_PATH", limit=180)
    parts = value.split("/")
    if len(parts) > 8 or not parts or any(
            not p or p in (".", "..") or p.endswith((" ", "."))
            or _WINDOWS_DEVICE.fullmatch(p)
            or any(ch in _WINDOWS_FORBIDDEN or unicodedata.category(ch)[0] == "C"
                   for ch in p) for p in parts):
        raise DeliveryPlanError("UNSAFE_PATH")
    return value


def _dimension(value):
    if value is None:
        return None
    if type(value) not in (int, float):
        raise DeliveryPlanError("INVALID_DIMENSIONS")
    try:
        finite = math.isfinite(value)
    except (OverflowError, ValueError) as exc:
        raise DeliveryPlanError("INVALID_DIMENSIONS") from exc
    if not finite or value <= 0:
        raise DeliveryPlanError("INVALID_DIMENSIONS")
    return value


def _positive_px(value):
    if type(value) is not int or value <= 0:
        raise DeliveryPlanError("INVALID_DIMENSIONS")
    return value


def _project_ref(value):
    if type(value) is not dict or value.get("kind") not in ("project", "generation"):
        raise DeliveryPlanError("INVALID_PROJECT_REF")
    if value["kind"] == "project":
        _keys(value, ("kind", "project_id", "sha256"), where="PROJECT_REF")
        _identifier(value["project_id"], "INVALID_PROJECT_REF")
        _digest(value["sha256"])
    else:
        _keys(value, ("kind", "producer", "version", "sha256"), where="PROJECT_REF")
        _identifier(value["producer"], "INVALID_PROJECT_REF")
        _text(value["version"], code="INVALID_PROJECT_REF", limit=80)
        _digest(value["sha256"])
    return dict(value)


def _item(record):
    fields = ("item_id", "source_locator", "size_bytes", "sha256", "media_type",
              "role", "target_relpath", "dimensions", "operation_context",
              "qa", "machine_context", "share_decision", "guidance")
    _keys(record, fields, where="ITEM")
    item_id = _identifier(record["item_id"], "INVALID_ITEM")
    locator = _text(record["source_locator"], code="INVALID_SOURCE_LOCATOR")
    if type(record["size_bytes"]) is not int or not 0 < record["size_bytes"] <= MAX_ITEM_BYTES:
        raise DeliveryPlanError("BUDGET_EXCEEDED")
    digest = _digest(record["sha256"])
    role = record["role"]
    if type(role) is not str or role not in ROLE_MEDIA or record["media_type"] != ROLE_MEDIA[role]:
        raise DeliveryPlanError("INVALID_ARTIFACT_ROLE")
    target = _target_path(record["target_relpath"])
    if not target.casefold().endswith(".png" if role == "PNG_PTC" else ".svg"):
        raise DeliveryPlanError("INVALID_ARTIFACT_ROLE")
    dims = record["dimensions"]
    dimension_keys = ("width_mm", "height_mm", "confirmed", "provenance")
    if role == "PNG_PTC":
        dimension_keys += ("width_px", "height_px")
    _keys(dims, dimension_keys, where="DIMENSIONS")
    if type(dims["confirmed"]) is not bool:
        raise DeliveryPlanError("INVALID_DIMENSIONS")
    width, height = _dimension(dims["width_mm"]), _dimension(dims["height_mm"])
    if dims["confirmed"] and (width is None or height is None):
        raise DeliveryPlanError("INVALID_DIMENSIONS")
    provenance = dims["provenance"]
    if provenance is not None:
        _text(provenance, code="INVALID_DIMENSIONS", limit=80)
    if dims["confirmed"] and provenance is None:
        raise DeliveryPlanError("INVALID_DIMENSIONS")
    if role == "PNG_PTC":
        _positive_px(dims["width_px"])
        _positive_px(dims["height_px"])

    op = _keys(record["operation_context"],
               ("operations", "attach_required", "mirror_required"),
               where="OPERATIONS")
    if (type(op["operations"]) is not list or not op["operations"]
            or len(op["operations"]) > 16
            or any(type(x) is not str or x not in _OPERATIONS for x in op["operations"])
            or len(set(op["operations"])) != len(op["operations"])
            or type(op["attach_required"]) is not bool
            or type(op["mirror_required"]) is not bool):
        raise DeliveryPlanError("INVALID_OPERATIONS")
    declared = set(op["operations"])
    if (role == "PNG_PTC" and declared != {"PRINT_THEN_CUT"}) or (
            role == "SVG_BASIC_CUT" and declared != {"CUT"}) or (
            role == "SVG_MULTILAYER_CUT" and "CUT" not in declared) or (
            role != "PNG_PTC" and "PRINT_THEN_CUT" in declared):
        raise DeliveryPlanError("INVALID_OPERATIONS")

    qa = record["qa"]
    if type(qa) is not list or len(qa) > 64:
        raise DeliveryPlanError("INVALID_QA")
    seen_qa = set()
    for check in qa:
        _keys(check, ("check_id", "status", "reason"), where="QA")
        cid = _identifier(check["check_id"], "INVALID_QA")
        if cid in seen_qa or type(check["status"]) is not str or check["status"] not in _QA_STATES:
            raise DeliveryPlanError("INVALID_QA")
        seen_qa.add(cid)
        if check["reason"] is not None:
            _text(check["reason"], code="INVALID_QA", limit=256)
        if check["status"] in ("FAIL", "UNKNOWN", "NOT_APPLICABLE") and not check["reason"]:
            raise DeliveryPlanError("INVALID_QA")

    machine = _keys(record["machine_context"],
                    ("capability", "availability", "profile"), where="MACHINE")
    if (machine["capability"] not in ("SUPPORTED", "UNSUPPORTED", "UNKNOWN")
            or machine["availability"] not in ("AVAILABLE", "UNAVAILABLE", "UNKNOWN")):
        raise DeliveryPlanError("INVALID_MACHINE")
    if machine["profile"] is not None:
        _text(machine["profile"], code="INVALID_MACHINE", limit=120)

    share = _keys(record["share_decision"], ("status", "basis"), where="RIGHTS")
    if share["status"] not in ("ALLOWED", "REVIEW_REQUIRED", "DENIED"):
        raise DeliveryPlanError("INVALID_RIGHTS")
    _text(share["basis"], code="INVALID_RIGHTS", limit=512)
    guide = _keys(record["guidance"], ("steps", "optional_html"), where="GUIDANCE")
    if type(guide["optional_html"]) is not bool or type(guide["steps"]) is not list or len(guide["steps"]) > 64:
        raise DeliveryPlanError("INVALID_GUIDANCE")
    for step in guide["steps"]:
        _text(step, code="INVALID_GUIDANCE", limit=512)
        if not step.strip():
            raise DeliveryPlanError("INVALID_GUIDANCE")
    # HTML is optional, but the manual transfer instructions are not.
    # The metadata planner cannot certify their semantic correctness.
    manual_transfer = (bool(declared & {"SCORE", "DRAW", "FOIL"})
                       or op["attach_required"] or op["mirror_required"])
    if manual_transfer and not guide["steps"]:
        raise DeliveryPlanError("INVALID_GUIDANCE")

    reasons = []
    if not dims["confirmed"]:
        reasons.append("PHYSICAL_SIZE_UNCONFIRMED")
    if share["status"] == "DENIED":
        reasons.append("RIGHTS_DENIED")
    elif share["status"] == "REVIEW_REQUIRED":
        reasons.append("RIGHTS_REVIEW_REQUIRED")
    if any(check["status"] == "FAIL" for check in qa):
        reasons.append("QA_BLOCKED")
    if machine["capability"] == "UNSUPPORTED":
        reasons.append("MACHINE_OPERATION_UNSUPPORTED")
    if not qa or any(check["status"] == "UNKNOWN" for check in qa):
        reasons.append("QA_UNVERIFIED")
    if machine["capability"] == "UNKNOWN":
        reasons.append("MACHINE_CAPABILITY_UNKNOWN")
    # Metadata alone never verifies the actual source SHA, contents or licence.
    if not reasons or all(x in ("QA_UNVERIFIED", "MACHINE_CAPABILITY_UNKNOWN") for x in reasons):
        reasons.append("SOURCE_NOT_VERIFIED")
    blocking = any(x in ("PHYSICAL_SIZE_UNCONFIRMED", "RIGHTS_DENIED",
                         "RIGHTS_REVIEW_REQUIRED", "QA_BLOCKED",
                         "MACHINE_OPERATION_UNSUPPORTED") for x in reasons)
    result = dict(record)
    result["admission"] = "BLOCKED" if blocking else "EXPORT_UNVERIFIED"
    result["reasons"] = sorted(set(reasons))
    result["verification_state"] = "METADATA_ONLY"
    return result


def plan_delivery(*, items, selection, context):
    """Plan an explicit selection without opening, copying or writing files.

    No metadata-only item can claim LOCAL_QA_PASSED; SD0-B will verify bytes.
    canonical_json retains private source locators and must not be published
    as a portable delivery manifest.
    """
    if type(context) is not dict or set(context) != {
            "plan_id", "project_ref", "policy_version"}:
        raise DeliveryPlanError("INVALID_CONTEXT")
    _identifier(context["plan_id"], "INVALID_CONTEXT")
    if context["policy_version"] != QUOTA:
        raise DeliveryPlanError("UNSUPPORTED_POLICY")
    project = _project_ref(context["project_ref"])
    if type(items) is not list or not 1 <= len(items) <= MAX_ITEMS:
        raise DeliveryPlanError("BUDGET_EXCEEDED")
    if (type(selection) is not list or not selection
            or any(type(s) is not str for s in selection)
            or len(set(selection)) != len(selection)):
        raise DeliveryPlanError("INVALID_SELECTION")
    selected = set(selection)
    validated = []
    by_id = set()
    by_path = set()
    total = 0
    for raw in items:
        item = _item(raw)
        if item["item_id"] in by_id:
            raise DeliveryPlanError("DUPLICATE_ITEM")
        by_id.add(item["item_id"])
        norm = unicodedata.normalize("NFC", item["target_relpath"]).casefold()
        if norm in by_path or any(
                norm.startswith(x + "/") or x.startswith(norm + "/") for x in by_path):
            raise DeliveryPlanError("DUPLICATE_TARGET")
        by_path.add(norm)
        validated.append(item)
        if item["item_id"] in selected:
            total += item["size_bytes"]
        if total > MAX_TOTAL_BYTES:
            raise DeliveryPlanError("BUDGET_EXCEEDED")
    if any(s not in by_id for s in selection):
        raise DeliveryPlanError("INVALID_SELECTION")
    blocked = sorted({reason for item in validated if item["item_id"] in selected
                      and item["admission"] == "BLOCKED" for reason in item["reasons"]})
    status = "BLOCKED" if blocked else "EXPORT_UNVERIFIED"
    data = {
        "schema": SCHEMA, "plan_id": context["plan_id"],
        "policy_version": QUOTA, "project_ref": project,
        "items": validated, "selected_item_ids": list(selection),
        "omitted_item_ids": sorted(by_id - selected),
        "admission": status, "reasons": blocked or ["SOURCE_NOT_VERIFIED"],
        "actual_source_verified": False,
        "design_space_import_tested": False, "physical_cut_tested": False,
    }
    try:
        encoded = json.dumps(data, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise DeliveryPlanError("INVALID_PLAN") from exc
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise DeliveryPlanError("BUDGET_EXCEEDED")
    return DeliveryPlan(encoded, sha256(encoded).hexdigest(), status,
                        tuple(data["reasons"]), tuple(selection))
