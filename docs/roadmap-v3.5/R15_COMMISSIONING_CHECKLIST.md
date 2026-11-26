# R15 commissioning and transition checklist

Status: owner proposal, not active. R13 remains sole live authority.

## Runtime decision
- GitHub-hosted runner is validated for read-only observation and CI log retrieval.
- Portable relay carries only PR/head/main/policy, action and plan fingerprints.
  Same-run artifact and cross-run cache are temporary, public metadata,
  untrusted and advisory. They do not restore leases or author-cycle proof.
- A production single-writer durable journal needs a controlled persistent
  runtime (e.g. private volume on an existing server). Do not deploy a
  self-hosted runner that executes arbitrary PR code. No new paid API.
- Existing scheduler tasks retain A/B responsibilities. Their optional
  handoffs can be collected independently; no fabricated cycle identity.

## Exit criteria before an effective R15 contract
1. Real queue observation and exact checkout/step-bound CI probe PASS.
2. Cross-runner relay PASS, then separate run restores previous checkpoint;
   drift must produce new advice, never reuse stale work.
3. Independently capture a real scheduler handoff and compare with GitHub.
   If unavailable, retain the current R13 review path instead of blocking
   unrelated engineering.
4. Select and qualify a persistent single-writer runtime and scheduler bridge.
   Exercise restart, no duplicate execution, uncertain merge response,
   exact-main G0 and recovery. Shadow-only inputs cannot authorize a merge.
5. Separate reviewed policy/READY transition with one effective authority,
   rollback to R13 and exact-head qualification. A never merges; B remains
   sole normal executor unless that reviewed contract explicitly changes it.

No live schedule, permissions, merge or authority change in this checklist.
