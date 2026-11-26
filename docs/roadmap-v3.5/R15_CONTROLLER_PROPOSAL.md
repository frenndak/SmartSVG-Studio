# R15 — Controller shadow-mode proposal (owner session 2026-11-25)

Status: PROPOSAL / NOT ACTIVE. R13 remains the complete governing contract.
No authority transfer, workflow enablement, WIP increase, secret, new dependency,
paid inference, server installation or merger is authorized by this proposal.

## Objective
Replace repeated administrative reasoning with deterministic state and evidence.
Preserve every V3.5 product criterion and all GitHub protections. Existing A/B
tasks continue R13 while this independent owner governance tranche is reviewed.

## Stage 1: shadow controller
Local Python standard library + SQLite. Store immutable evidence by PR HEAD,
main, policy blob and evidence kind; mutable observations must be refreshed.
One atomic lease per work item, a fencing token for every checkpoint, expiry
and recovery without force-push. A lease in this database is not a GitHub
branch lock: single writer and expected HEAD remain mandatory. No network or
GitHub mutation in this prototype. Never treat a comment as approval.
Use a private persistent volume, not a public repository as a credential store.
Run tests against temporary databases and two independent connections.

## Stage 2: observation adapter
Fetch exact main, all open PRs (paginate), per-HEAD checks and actual executed
steps, review receipts and affected consumer blobs, scheduler evidence and
effective rules. Compare proposed decisions with R13 without executing them.
Keep CI evidence separate from independent review and physical qualification.
No inferred PASS, no automated untrusted PR code on a personal runner.
Collect cycle productivity, age, integration lead time, error categories and
roadmap traceability, not PR numbers as percent completion.

## Stage 3: controlled transition
After shadow evaluation on real cases and test coverage, submit a distinct
owner-reviewed policy revision that defines a single effective contract,
authority transfer, rollback, exact-head merge and post-merge G0 barriers.
Do not activate the proposed merger or increase WIP before that revision.
Evaluate Codex local session/effort/quotas and ZimaOS only after access and
budget are verified; no API spending or credentials in public workflows.

## Acceptance
Race claims, expiry/reclaim, stale fencing token, HEAD change, main change,
duplicate receipts, crash/restart, WIP full, CI skip/fail, required external
approval and post-merge G0 fail. Stage 1 does not claim to implement the later
adapter or merger. Preserve R13 scope, the four export roles, V1/source/masks,
141 inherited requirements, 140 DoD, 80 UX and 437 scenarios. A separate
review and exact-head CI are required for this governance PR.
