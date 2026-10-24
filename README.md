# SmartSVG Studio

Private source repository for SmartSVG Studio (ComfyUI / Cricut preparation).

## Source of truth

- Planned roadmap: SmartSVG Studio MASTER ROADMAP v3.2 (frozen consolidated copy, to be imported).
- Latest candidate archive in the project library: `ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip` (to be imported and verified).
- Keep historic frozen baseline V21.14.1 separate, unchanged.
- Never publish private source, user images, test fixtures, prompts, logs or exports in the public orchestration repo.

## Bootstrap safety

The automated development runner MUST NOT modify this repository until the actual source tree and authoritative roadmap are imported and a maintainer creates `.automation/READY` after verifying them. Changes must be proposed through draft pull requests, never pushed to `main` by automation.

See: `frenndak/SmartSVG-Automation` for the public orchestration skeleton.

## Bootstrap V21.15.2 - Private source import

The canonical V3.2 roadmap is in docs/ROADMAP_MASTER_v3_2.md.
No substitute, partial reconstruction, or fake source tree is acceptable.

1. Review and merge the existing G0 branch/PR #1, including its archive verifier and isolated importer.
2. Upload the original ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip to a PRIVATE release named smartsvg-v21.15.2-source (exact asset filename).
3. Actions > SmartSVG - Import private source release > Run workflow.
4. The bootstrap extracts into engine/ on a new PRIVATE branch and proposes a draft PR.
5. Independently validate the internal package manifest, node compatibility, existing tests, PNG Print Then Cut, editable SVG, cut SVG and ComfyUI.
6. Only once independently validated, set up an operator-created .automation/READY marker; use the public orchestrator only with explicit accepted runner visibility and properly scoped secrets.

Do not claim GPU inference, Design Space import, or real Cricut cutting was tested until actually observed.
Current state: code archive is absent from the repository; the G0 bootstrap tool is in PR #1.
