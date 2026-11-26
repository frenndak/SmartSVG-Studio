# R15-B — recovery observation persistence

Read-only live GitHub observations are now connected to the shadow CAS
journal transition interface. The recovery result must match the exact
journal ref/generation/intent, and be freshly repeated before one CAS.
Positive terminal readback requires the observed squash to be current main,
exact G0 step PASS, identical G0 workflow blob and policy blob relative to
the original main. Later main, wait, failure and negative readback remain
nonterminal. No duplicate identical observation; no automatic retry on
ambiguous write. Prepared intent is not dispatched. No merge authority.

The CI commissioning uses a synthetic intent for the actual #196 squash,
actual live GitHub observations and an injected in-memory writer. It does
not mutate the pinned live shadow branch. Existing live Git transport
commissioning and this coordinator are separate proofs; a connector-native
production writer with verified scheduler cycle and policy is still absent.

R15-A observation 2026-11-26 11:50Z: main remains f00f665, its push routing
45758552417 passed, but /actions/runs?event=schedule returns no runs.
Both latest agent reports say NO_RUN. The cause is not established; do not
claim automatic scheduling is working. A/B retain immediate R13 fallback.
No new paid service, no scheduler/merge privilege change.
