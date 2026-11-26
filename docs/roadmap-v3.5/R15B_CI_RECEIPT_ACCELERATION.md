# R15-B — exact CI receipt acceleration

Observed actual #195 head 7e557c8...: Windows job 139656342576 prints
test_real_export_buttons_follow_brush_and_history_transitions on a header
line, followed immediately by its unittest description and "... ok".
The old parser only recognized the single-line verbose form. The new
parser handles both, records both line numbers and rejects duplicate,
missing, intervening or out-of-step observations. Step binding checks
both timestamps and exact checkout. A bound receipt is still advisory.

Owner session read actual exact-head Linux G0 job 139656342189: eleven of
the twelve Windows-only skips explicitly PASS; directory swap needs
NumPy/Pillow and is skipped there. Actual CPU job 139656353290 explicitly
PASS for directory swap. Windows job 139656342576 has 1149 tests, 12 skips.
This is coverage of those named cross-platform exclusions, not semantic
review or blanket permission to merge. CI still rechecks workflow pins,
attempt and current-main applicability. No repeated historical lookup.

New commissioning step checks actual two-line Tk receipt for #195,
without dispatching work or changing R13. Previous durable terminal
restart run 45827354470 job 139934820299 passed, 220/220 targeted tests.
No scheduled R15 runs observed; root cause not established.
