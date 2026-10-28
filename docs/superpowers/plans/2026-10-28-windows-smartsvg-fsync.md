# Windows `.smartsvg` Durability Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore durable `.smartsvg` creation and recovery on Windows without weakening atomic-write guarantees.

**Architecture:** Keep the existing validate, temporary ZIP, readback, and atomic publish sequence. Change only the temporary archive synchronization boundary so `os.fsync()` receives a writable descriptor on Windows, while retaining the same on-disk bytes and rollback behavior.

**Tech Stack:** Python standard library (`zipfile`, `os`, `unittest`)

**Spec:** `AGENTS.md` development policies 3 and 7; `docs/ETAT_ACTUEL_SMARTSVG.md` project-save contract

## Global Constraints

- Preserve `.smartsvg` schema, archive members, hashes, node IDs, and public interfaces.
- Do not touch frozen roadmap, source releases, workflows, governance, or automation files.
- Keep failures fail-closed and preserve the last good snapshot.
- Make no Windows, GPU, or Cricut claim beyond fresh evidence.

## Review Focus

- Windows `_commit()` rejects a read-only descriptor: the regression must prove the synced descriptor is writable.
- A failed synchronization must still abort before publishing the destination.
- Overwrite mode must retain atomic replacement and the previous valid snapshot on pre-publish failure.
- Archive readback must still occur before publication.
- Linux behavior and archive bytes must remain unchanged.

---

### Task 1: Synchronizable temporary project archive

**Files:**
- Modify: `engine/tests/test_project_archive_g13.py`
- Modify: `engine/smartsvg_core/project_archive.py`

**Interfaces:**
- Consumes: `save_project(path, project, overwrite=False)` and the existing atomic-write sequence.
- Produces: the same return dictionary and archive format, with a writable descriptor passed to `os.fsync()`.

- [x] **Step 1: Write the failing regression test**

Add `test_temporary_archive_is_fsynced_through_writable_descriptor`. Observe the real temporary archive handle and require both mode `r+b` and `handle.writable()`. Call `save_project` and assert the archive still round-trips. Add injected-fsync creation/overwrite regressions plus an event-order check proving readback precedes publication.

- [x] **Step 2: Verify the regression is red**

Run: `$env:PYTHONPATH='engine'; python engine/tests/test_project_archive_g13.py ArchiveG13Tests.test_temporary_archive_is_fsynced_through_writable_descriptor -v`

Expected: error `PROJECT_SAVE_FAILED` caused by a bad/read-only file descriptor.

- [x] **Step 3: Implement the minimal durability fix**

Open the already-written temporary ZIP with mode `r+b` for the file `fsync`; do not change validation, readback, link/replace, or directory sync logic.

- [x] **Step 4: Verify targeted green behavior**

Run the new regression plus `test_exact_save_close_open_15_operations_and_3_undo`, `test_no_overwrite_by_default_and_atomic_overwrite`, and `test_bad_write_never_destroys_last_good_snapshot`.

Expected: all selected tests pass on Windows Python 3.14.

- [x] **Step 5: Verify proportional suites and inspect the diff**

Run the full G1.3 archive test file, the wrapper suite `tests/test_g13_project_archive.py` if present, source-integrity check, then the repository test commands with UTF-8 mode. Classify unrelated environment failures explicitly.

- [x] **Step 6: Commit**

Commit only the plan, regression test, minimal implementation, and any narrowly necessary operational status update after fresh verification.
