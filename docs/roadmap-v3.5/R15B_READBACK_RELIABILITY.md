# R15-B — readiness readback reliability

Ready-for-review run 45834218028 job 139958665779 failed in repeated
live recovery readback, after initial exact historical squash/G0 PASS
and pinned journal restart PASS. Assertion line 15 checks the observed
merge SHA; previous logs lacked the reduced result at that assertion.
The exact cause is unproved. Do not classify it as network failure or
ignore it because an earlier run passed.

Add at most one retry of idempotent metadata GET for transient disconnect,
timeout, reset, incomplete read or 502/503/504 without Retry-After.
No retry of auth, rate limits, invalid payload, context mismatch or
mutation. No bypass of final revalidation. Emit safe action/state/reason
or exception type on replay failure. Three new regression tests.

R15-A schedule remains unobserved (zero schedule runs returned); current
R13 fallback is still active. Owner promotion remains blocked pending
successful exact new-head commissioning. No new paid service or authority.
