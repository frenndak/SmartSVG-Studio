# Native template previews Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a usable card/tray geometry preview to the existing standalone desktop shell.

**Architecture:** Reuse `smartsvg_core/template_geometry_v34.py` without a second generator, export path or writer. A focused Tk panel draws immutable preview results and clears stale geometry when inputs change. The desktop opens one reusable panel, independently of project selection.

**Tech Stack:** Python standard library; existing lazy Tk/ttk UI.

**Spec:** `docs/roadmap-v3.4/16_PATRONS_PARAMETRIQUES.md`, V34-126/128 preview subset; owner-authorized continuous implementation. The design choice is to extend the existing Tk prototype, without choosing the final framework or adding dependencies.

## Global Constraints

- Preserve all 141 inherited requirements and four distinct output contracts.
- No project/source/export writes, no network/model calls, no ComfyUI or torch imports.
- Use the existing geometry for an 80 × 50 × 30 mm tray with 10 mm tabs: 140 × 110 mm, five CUT paths and eight SCORE paths.
- A folded card uses width/height only; wall/tab inputs are disabled and ignored.
- Geometry is a nominal draft; SCORE assignment and Attacher remain manual, material qualification UNKNOWN.

## Review Focus

- Invalid/nonfinite/collapsed dimensions clear stale geometry and show an actionable message.
- Editing any parameter or changing template invalidates the previous preview.
- Small/large resize preserves aspect ratio and operation styles.
- No files change when either template is opened, edited, rendered or closed.
- Loading the desktop probe stays possible with `python -I -S`, without Tk imports.

### Task 1: Native template panel and shell entry point

**Files:** create `engine/native_templates_tk_v34.py`, `tests/test_v34_native_templates.py`; modify `engine/standalone_desktop_v34.py`.

**Interfaces:** `NativeTemplatePreview(root, tk, ttk)` receives widget APIs like the existing theme picker; exposes its window, input variables and `calculate()` callback to normal UI wiring. `open_template_preview(current, root, tk, ttk)` creates/reuses one live window. Geometry results come directly from `folded_card` / `open_tray`.

- [ ] Add failing tests for default tray, card switch, invalid inputs, stale-input invalidation, resize/style invariants, single-window reuse and no-write behavior.
- [ ] Run `python -m unittest discover -s tests -p 'test_v34_native_templates.py' -v`; expect failure because panel module/entry point is missing.
- [ ] Implement the panel and native shell button, retaining lazy widget imports and read-only capabilities.
- [ ] Run focused native tests, complete Python suite, isolated desktop probe and diff checks; record actual results and platform limits.
- [ ] Commit; obtain independent whole-branch review and exact-head CI before owner-authorized integration. Verify main G0 after fusion.
