# Native application foundation

Goal: give the existing standalone Tk prototype a shared window with Home, Project, Fabrique and Appearance workspaces, ready to host subsequent tools.

Architecture: a small injected-widget AppShell owns layout/navigation only. The existing read-only project reader remains the sole project presenter; the existing template form becomes embeddable while its popup API stays compatible. Appearance preferences still load at startup and apply globally.

Tech stack: existing Python/Tk/ttk; no added dependencies or packaging change.

Spec: roadmap V3.4 lot 07 (V34-041/046 subset) and UX design addendum U2. This slice does not qualify the full UX or Windows gates.

Global constraints: changing pages must not read/write projects, submit jobs, reset forms or create duplicate windows. Preserve PNG reading, worker generation checks, lazy Tk bootstrap, theme persistence and template geometry. Do not advertise unavailable editing/export actions.

Review focus: actual entry-point wiring; retained session/error/draft state; theme loaded before first page; keyboard routing; shutdown; no hidden popup; no claim of real GUI/DPI qualification from doubles.

## Task 1 — shared native shell and embedded workspaces

- [x] Demonstrate missing shell with focused failing tests.
- [x] Implement navigation/layout, embed existing tools, wire home actions and shortcuts.
- [x] Prove 100 navigation changes preserve real template state and project bytes; test desktop wiring and reader shutdown.
- [x] Run focused and full available suites plus isolated probe; independent review and exact-head CI before integration.


Implementation decision: retain the reversible existing Tk prototype and mount tools in registered frames. No GUI framework migration or new project model. The popup template API remains available for existing callers. The shell itself never reads archives or submits jobs.

Evidence: 8 new shell/integration tests and the existing native suites pass (76 total); the complete root suite passes (609). Isolated `python -I -S engine/standalone_desktop_v34.py --probe` passes without Tk/ComfyUI. Real V1 archive reading, retained error/summary state, 100 route changes, draft retention, cancel, F5, shortcuts, shutdown and no project mutation are exercised. Headless widget doubles are used at the Tk boundary; actual Windows geometry, 200% DPI and screen-reader qualification remain open. Independent review and remote CI are recorded in the PR, not inferred from these local results.
