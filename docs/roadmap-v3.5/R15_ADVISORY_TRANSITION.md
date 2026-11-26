# Proposed R15-A transition: advisory orchestration with R13 execution

Status: PROPOSED, not authority. This is the shortest useful operational
transition, before a durable automatic integrator is qualified.

## Controller output
The independent route-shadow job emits exactly one R15_ROUTE_V1 JSON line,
bound to its own controller HEAD, workflow run/attempt, observed main/policy
and candidate HEAD. It does not depend on the historical commissioning PR
or a test probe. Empty queue, unknown candidate and unavailable runner must
not prevent agents from doing independent R13 work.

## Consumer contract
Existing A/B tasks may use the latest successful owner-qualified routing
report as a prioritization hint after checking the exact run/job, controller
HEAD against a reviewed pin, current main, policy blob and candidate HEAD.
Do not assume that age alone authenticates data or that a matching plan is a
completed task. Compare with current actionable work and exact checkpoints.
If report absent, stale, inconsistent or unavailable, continue normal R13.
Never wait for the controller; no extra human intervention, no duplicate
review solely to satisfy the relay. A never merges, B alone may integrate
under the complete R13 gate contract. R15-A adds no merge gate and no
authority to skip tests, write outside scope, or share credentials.

## Commission and promotion
Qualify route-shadow independently of fixed probe, observe actual consumption
by both scheduled tasks, and record whether productive actions improve.
An owner-reviewed subsequent policy revision can promote the route job to a
main-only scheduled read-only workflow, with no new paid inference or server.
Until then it is triggered only for owner PR 196. Full deterministic merger,
private durable leases, scheduler history and operational authority transfer
remain separate R15-B acceptance; do not call R15-A a complete R15 deployment.
Rollback of R15-A: stop consuming hints; existing R13 procedure remains valid.


## Automatic refresh candidate
The proposed `.github/workflows/r15-advisory-routing.yml` runs at H:12 UTC
(and on main pushes or manual dispatch on main) after its owner-reviewed
promotion to default main. The PR 196 job is a test, not activation.
The schedule precedes B H:25 and A H:55; GitHub schedules can be delayed or
dropped. If main advances, the old run refuses to publish a main-bound plan.
The agents must never wait for a delayed or missing route.

Production discovery: select a completed successful run of exactly this
workflow path, event schedule/push/workflow_dispatch, branch main,
matching current main/controller head; verify the current workflow blob
against the separately reviewed promotion pin, job route-live and exact
successful Publish reduced live routing advice step. Then read that exact job
log and require a unique well-formed R15_ROUTE_V1 line with matching run,
attempt, current main/policy, and assigned current PR HEAD. Maximum age 90
minutes, no future timestamp. Unavailable, ambiguous or stale => R13
immediate fallback. Pilot PR runs are not production runs.

Observed service issue: B's 2026-11-26 03:25Z result reports scheduler
readback HTTP 404 Action not found. This is not authority and is not solved
by routing. Keep R13 no-merge semantics; continue code and technical review.
A separately reviewed operational authorization channel is required before
an authority transition. Never treat a routing hint or cached scheduler
snapshot as live scheduler permission.
