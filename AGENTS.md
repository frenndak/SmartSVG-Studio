# SmartSVG Agent Contract

Applies to every AI agent working in the intentionally **public** `frenndak/SmartSVG-Studio` repository.

## Protected reference
- Public visibility is intentional. Do not commit API keys, private artwork, personal data, commercial model weights or licensed media; do not make this repository private as a routine fix.
- Governing roadmap: **V3.3**, `docs/ROADMAP_MASTER_v3_3.md`, formally published by PR #60; consult `docs/ROADMAP_TRACEABILITY_v3_3.md`, `docs/ROADMAP_COVERAGE_v3_3.md`, and `docs/ROADMAP_HERITAGE_v3_3.md` for the 141 requirements and their full historical inheritance. The V3.2 master and freeze manifest remain intact as immutable historical archives. Never replace the active master without a separately authorized, verified roadmap revision.
- Preserve V21.14.1 historical frozen baseline untouched.
- The currently available build in the project Library is V21.15.2; import source and validate provenance before allowing autonomous engineering.
- Never claim real Cricut Explore 5 / Design Space validation, actual GPU RTX 3070 inference, or physical cut measurements unless evidence is provided.

## Development policy
1. Work only in a new branch from main, one roadmap micro-lot plus at most one focused correction per iteration.
2. Start with current repository files, open PRs, latest review, and gate criteria. Never fabricate evidence or claim tests not run.
3. Keep existing node IDs, ComfyUI ports, SVG/PNG output contracts and backwards compatibility unless approved migration and tests exist.
4. Treat PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche and SVG d'édition as four distinct output contracts. Print Then Cut uses PNG for the Design Space print workflow. Never imply internal vector editability when only cut contours were traced, or material readiness without verified evidence.
5. UX: Express-first, readable guidance, error recovery, keyboard/accessibility, small-screen and user input validation.
6. Verify SVG XML, namespaces, viewBox, contours, topology, explicit units, and mm; preserve pixel-resolution quality without false physical-print assurances.
7. Run available tests, describe absent dependencies and tests, write focused regression tests; do not downgrade assertions to get green.
8. Never modify `AGENTS.md`, `docs/ROADMAP_MASTER_v3_3.md`, `docs/ROADMAP_HERITAGE_v3_3.md`, `docs/ROADMAP_MASTER_v3_2.md`, `docs/ROADMAP_FREEZE_v3_2.json`, `.github/`, `.automation/`, tokens/secrets, or any frozen artifacts in automated cycles. Status/proof registers may be updated by separately reviewed micro-lots without changing historical requirements.
9. Do not add copyrighted third-party test images or user-owned samples to public repos.
10. Stop and report if current source, roadmap, tool access, or validation evidence is unavailable. Never silently bypass safety checks.

## Activation
Automation is disabled until the actual SmartSVG source is imported and a maintainer writes `.automation/READY` after checking the baseline provenance. The marker is necessary but not proof of validation. Scheduled AI agents must submit **draft PRs only** and must not approve or merge them autonomously. In a live, user-directed ChatGPT session, the repository owner may explicitly delegate **the integration decision** to the assistant, conditional on a documented counter-expertise of the actual diff, fresh green relevant CI, a current main/HEAD comparison, a reversible integration plan, and no unresolved blockers. This delegation does not manufacture an independent GitHub APPROVED review, override required GitHub branch protections, or certify Windows/GPU/Cricut performance. Changes to protected governance/workflow files must be handled in a separately documented, deliberately authorized micro-PR; scheduled agents remain prohibited from editing protected paths.
