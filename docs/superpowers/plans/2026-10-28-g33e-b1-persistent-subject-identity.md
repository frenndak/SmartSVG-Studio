# G3.3e-b1 Persistent Subject Identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Explicitly register a durable G1.2 `Subject` for one verified G2.4 float32 mask, save it transactionally, expose it in the Atelier, and preserve all mask bytes.

**Architecture:** Add one server-side identity service that validates the pinned archive revision and exact ordered float32 slice, derives the G2.6 threshold bbox, then appends a `Subject` through the existing managed workspace and `save_with_recovery`. Expose the command through the existing opt-in G2.2 same-origin route and a small browser module used by the existing subject cards. Existing snapshots that have persistent subjects cannot be replaced with different bytes without an explicit later rebinding design.

**Tech Stack:** Python 3.11 standard library, existing SmartSVG archive/workspace/recovery modules, browser ES modules, Node test runner, unittest.

**Spec:** GitHub issue #69 and the attached “MISSION CODEX — SMARTSVG STUDIO V3.3”.

## Global Constraints

- Roadmap V3.3 is the only active roadmap.
- Do not modify protected governance, workflow, frozen archive, ComfyUI node ID/port, or SVG/PNG output contracts.
- Float32 bytes are authoritative; PNG L8 is preview only.
- No mask pixel edit, inference, queue execution, automatic migration, or arbitrary filesystem path.
- Every write requires explicit confirmation and `expected_sha256`.
- PR remains Draft and is never merged automatically.

## Review Focus

- Reordered or replaced snapshot must not inherit a persisted subject identity.
- Duplicate float32 content must fail closed rather than choose by position.
- Concurrent requests from two tabs must allow at most one revision-pinned write.
- Save failure or interruption must leave recovery evidence and never report success.
- Late browser responses must not update a replaced/expired inspection.

---

### Task 1: Persistent identity engine and transaction

**Files:**
- Create: `engine/smartsvg_core/subject_identity_g33e.py`
- Modify: `engine/smartsvg_core/project_workspace_g22.py`
- Create: `tests/test_g33e_persistent_subject_identity.py`

**Interfaces:**
- Produces: `register_subject_identity(project, *, mask_index, mask_id, mask_sha256_float32, source_id, source_sha256, subject_id_factory) -> (LoadedProject, Subject, bool)`
- Produces: `ManagedWorkspace.register_subject_identity(name, ..., expected_sha256, confirmed, expires_at_ms) -> dict`

- [ ] Write integration tests for create/reopen/idempotent recognition, exact bbox, multiple subjects, unchanged resources and previews.
- [ ] Run the focused test against the unmodified engine and verify failure because the API is absent.
- [ ] Implement strict snapshot/source/index/digest/duplicate/empty/collision validation and secure non-position-derived IDs.
- [ ] Orchestrate the update through `save_with_recovery` and verify the reopened archive before returning the new revision.
- [ ] Run the focused tests and inspect the diff.

### Task 2: Protect existing identities from snapshot replacement

**Files:**
- Modify: `engine/smartsvg_core/project_workspace_g22.py`
- Modify: `tests/test_g33e_persistent_subject_identity.py`

**Interfaces:**
- Consumes: persisted G1.2 subjects created by Task 1.
- Produces: refusal code `SUBJECT_IDENTITIES_REQUIRE_EXPLICIT_REBIND` when exact snapshot content changes.

- [ ] Add failing tests for reorder, content change and count change with existing subjects; allow exact identical replay.
- [ ] Implement the minimal guard before `save_base_masks` replaces any resource.
- [ ] Run focused backend tests.

### Task 3: Opt-in route and accessible Atelier action

**Files:**
- Modify: `engine/project_routes_g22.py`
- Create: `engine/web/js/smartsvg_subject_identity_g33e.mjs`
- Modify: `engine/web/js/smartsvg_express_atelier_preview.html`
- Create: `engine/tests/test_g33_subject_identity_ui.mjs`
- Modify: `tests/test_g33e_persistent_subject_identity.py`

**Interfaces:**
- Produces: POST `/smartsvg/g22/subject/identity` with same-origin header, confirmation, session expiry and exact project/mask evidence.
- Produces: `registerPersistentSubject(api, report, mask, options) -> Promise<result>`.

- [ ] Add failing route contract and browser tests for explicit confirmation, exact fields, double click, conflict, timeout/cancellation and late response.
- [ ] Add strict multipart fields and the route without exposing float32 bytes.
- [ ] Add the subject-card action only for a fresh verified catalog item without a persistent subject.
- [ ] Display loading, success with subject ID/new revision, and French recovery guidance.
- [ ] Run Python and Node focused tests.

### Task 4: Compatibility, independent review and publication

**Files:**
- Modify only files found necessary by Critical/Important review findings.
- Publish: Draft PR referencing issue #69.

- [ ] Run targeted backend/UI tests, full unittest admission suite, compileall and available CPU checks.
- [ ] Verify immutable V21.15.2 archive integrity.
- [ ] Review the complete diff for protected paths and contract drift.
- [ ] Obtain an independent architecture/integrity/concurrency/UI/test review.
- [ ] Fix Critical/Important findings with RED→GREEN tests and rerun the full suite.
- [ ] Push final commits, create a Draft PR, then verify G0, preflight and CPU checks on the exact HEAD.
