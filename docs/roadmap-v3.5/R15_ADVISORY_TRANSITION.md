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
