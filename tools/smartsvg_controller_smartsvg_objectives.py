"""SmartSVG adapter for a reviewed, partial qualification graph.

Sources are pinned, not parsed as commands. These micro-slices are advisory
proof labels, not new tickets, normative acceptance criteria, or full W-lot
completion. Missing source or revision evidence never blocks ordinary R13.
"""
from dataclasses import dataclass, replace
from http.client import HTTPException
from sqlite3 import Error as SQLiteError

from .smartsvg_controller_missions import MissionResumePlan, plan_mission_resumption
from .smartsvg_controller_objectives import (
    Objective, Profile, SHA, _matches, _validate_profile,
)

REPOSITORY = "frenndak/SmartSVG-Studio"
POLICY_PATH = "docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md"
POLICY_PIN = "d18aa357a8954ef4091f5219ad938cdc3f30846a"
BACKLOG_PATH = "docs/roadmap-v3.5/BACKLOG_AND_DEPENDENCIES.md"
SOURCE_PINS = (
    (BACKLOG_PATH, "8f8a858481d921fbd1a54d1a1f37aa65b613453d"),
    ("docs/roadmap-v3.5/MASTER_PRIORISE.md", "ec4f2e1dc5102840697c466b86fdc2ce99726f4b"),
    ("docs/roadmap-v3.5/DELIVERY_EXECUTION_PLAN.md", "1eea917780d8317a98c8521a43ae215f8b7a4347"),
    ("docs/roadmap-v3.5/SMART_DELIVERY_EXECUTION_CONTRACT.md", "637176f9348d22cd5ef0d1937710c9990c00442f"),
)

# key, routing role hint, proof labels, minimal qualification dependencies,
# advisory rank, explicitly independent fixture preparation.
# W01→W02/W03, W03→W04/W08, W05+one qualified export→W06:
# BACKLOG §3, MASTER §3, DELIVERY_EXECUTION_PLAN critical path.
# SD0-A/B and SD1-A/B/SD2: SMART_DELIVERY_EXECUTION_CONTRACT micro-lot table.
# No dependency on all W03 formats, physical calibration, W00 audit, or IA.
SLICES = (
    ("W01-V1-CORE", "B", ("v1-cas-recovery", "source-preservation"), (), 10, False),
    ("W02-MANUAL-SUBJECT", "A", ("manual-subject", "undo-reopen"),
     ("W01-V1-CORE",), 20, False),
    ("W03-BASIC-CUT-BACKEND", "B", ("real-v1-basic-cut", "svg-readback"),
     ("W01-V1-CORE",), 30, False),
    ("W03-PTC-BACKEND", "B", ("real-v1-ptc", "png-readback"),
     ("W01-V1-CORE",), 30, False),
    # An OR proof is explicit: one real typed output, independently verified.
    # Never infer its PASS from a sibling's branch, label, or all-format gate.
    ("W03-ONE-TYPED-EXPORT", "B", ("one-real-qualified-typed-artifact",),
     ("W01-V1-CORE",), 30, False),
    ("W04-PREFLIGHT", "B", ("typed-artifact-preflight", "unknown-profile-visible"),
     ("W03-ONE-TYPED-EXPORT",), 30, True),
    ("W03-EXPORT-UI", "A", ("ui-consent-no-clobber", "ui-output-readback"),
     ("W02-MANUAL-SUBJECT", "W03-ONE-TYPED-EXPORT"), 30, False),
    # SD0-A is pure schema/fixture work. It does not wait for W03.
    ("W05-SD0-A", "B", ("pure-plan-validation", "admission-fixtures"), (), 40, False),
    # SD0-B has an actual export/QA dependency. The adapter and its UI
    # consumer are separate planning slices, not new normative tickets.
    ("W05-SD0-B-ADAPTER", "B", ("readonly-real-artifact-plan",),
     ("W03-ONE-TYPED-EXPORT", "W04-PREFLIGHT"), 40, False),
    ("W05-SD0-B-UI", "A", ("readonly-plan-diagnostics",),
     ("W05-SD0-B-ADAPTER",), 40, False),
    ("W06-SD1-A", "B", ("zip-staging-stream-hash", "zip-readback-no-clobber"),
     ("W05-SD0-A", "W05-SD0-B-ADAPTER", "W05-SD0-B-UI",
      "W03-ONE-TYPED-EXPORT"), 40, False),
    ("W06-SD1-B", "A", ("destination-consent-recovery", "minimal-guide-receipt"),
     ("W06-SD1-A",), 40, False),
    ("W06-SD2", "A", ("offline-html-accessibility",), ("W06-SD1-B",), 45, False),
    ("W07-DIAGNOSTIC", "B", ("descriptive-geometry-diagnostic",),
     ("W03-ONE-TYPED-EXPORT", "W04-PREFLIGHT"), 50, True),
    ("W08-PTC-ASSISTANT", "A", ("ptc-manual-transfer-guide",),
     ("W03-PTC-BACKEND",), 50, False),
    ("W09-WEEDING-DIAGNOSTIC", "B", ("nondestructive-weeding-preview",),
     ("W04-PREFLIGHT", "W07-DIAGNOSTIC"), 90, False),
    ("W13-ACCESSIBILITY", "A", ("keyboard-focus-dpi",), (), 20, False),
)

# These are deliberately outside this reduced graph. They are not removed
# from the roadmap, not declared complete, and not implicit global blockers.
UNMAPPED = (
    "W00-transverse-coverage", "W03-other-format-contracts",
    "CAL-CUT", "CAL-PTC", "W09-physical-path-generation",
    "CP0-CP6", "W10", "W11", "W12", "W13-framework-benchmark",
    "W14", "W15-release", "W16", "SD3",
)


@dataclass(frozen=True)
class AdapterResult:
    status: str
    main: str
    objectives: tuple = ()
    missing_revisions: tuple = ()
    unmapped: tuple = UNMAPPED
    qualification: str = "PARTIAL_ADVISORY_GRAPH"
    merge_authorized: bool = False
    agent_work_executed: bool = False
    mission_plan: MissionResumePlan | None = None


def observe_smartsvg_objectives(get, profile, main, revisions):
    """Check immutable reviewed sources and construct an optional graph.

    revisions are supplied by an independently verified caller. Their syntax
    is not provenance or proof. Unobserved revisions remain missing, and
    downstream qualification is unknown rather than silently freed.
    No source change, scheduler call, mutation or live acceptance is inferred.
    """
    try:
        _validate_profile(profile)
        if (profile.project != "smartsvg" or profile.repository != REPOSITORY
                or profile.branch != "main" or not _matches(SHA, main)):
            return AdapterResult("PROFILE_MISMATCH", main)
        if (profile.policy_blob != POLICY_PIN
                or profile.roadmap_blob != dict(SOURCE_PINS)[BACKLOG_PATH]):
            return AdapterResult("SOURCE_REVIEW_REQUIRED", main)
        keys = {row[0] for row in SLICES}
        if (type(revisions) is not dict or not set(revisions) <= keys
                or any(not _matches(SHA, v) for v in revisions.values())):
            return AdapterResult("REVISION_INPUT_INVALID", main)
        if get("/branches/main")["commit"]["sha"] != main:
            return AdapterResult("CONTEXT_CHANGED", main)
        for path, pin in ((POLICY_PATH, POLICY_PIN), *SOURCE_PINS):
            if get(f"/contents/{path}?ref={main}").get("sha") != pin:
                return AdapterResult("SOURCE_REVIEW_REQUIRED", main)
        if get("/branches/main")["commit"]["sha"] != main:
            return AdapterResult("CONTEXT_CHANGED", main)
        objectives = tuple(Objective(key, revisions[key], role, criteria, deps,
                                     priority=rank, preparation_allowed=prep)
                           for key, role, criteria, deps, rank, prep in SLICES
                           if key in revisions)
        return AdapterResult("OBSERVED_PARTIAL_GRAPH", main, objectives,
                             tuple(sorted(keys - set(revisions))))
    except (KeyError, TypeError, ValueError, AttributeError, OSError,
            RuntimeError, HTTPException):
        return AdapterResult("UNAVAILABLE", main)


def observe_smartsvg_mission_resumption(get, journal, profile, main, revisions, *,
                                        role, receipts=()):
    """Revalidate the reviewed graph before offering local checkpoint advice."""
    graph = observe_smartsvg_objectives(get, profile, main, revisions)
    if graph.status != "OBSERVED_PARTIAL_GRAPH":
        return graph
    try:
        plan = plan_mission_resumption(journal, profile, main, graph.objectives,
                                       role=role, receipts=receipts)
    except SQLiteError:
        return AdapterResult("LOCAL_JOURNAL_UNAVAILABLE", main)
    try:
        current_main = get("/branches/main")["commit"]["sha"]
    except (KeyError, TypeError, ValueError, AttributeError, OSError,
            RuntimeError, HTTPException):
        return AdapterResult("UNAVAILABLE", main)
    if current_main != main:
        return AdapterResult("CONTEXT_CHANGED", main)
    return replace(graph, mission_plan=plan)
