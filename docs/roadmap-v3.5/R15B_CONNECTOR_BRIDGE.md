# R15-B — connector-native shadow transition commissioning

Owner-only isolated journal. No actual merge request was dispatched.
The previous completed shadow cancellation f5df4c1... was followed
by a synthetic intent for the already merged owner PR #196:
PREPARED e02622fc99d6965ee7eabe5ce18e4b89f9e9549b,
DISPATCH_UNKNOWN 24026a19bbb419ffd66bdbfdc2bdbd67206bbca5.
Both transitions were staged and read back with exact parent, bytes,
expected ref, force=false. The first intent used synthetic digests.
The real historical squash is not a B-cycle merge.

The read-only runner now reads the actual pinned journal and computes
a fresh recovery transition using live GitHub readback twice. It emits
one canonical bounded proposal, not a write or permission. The owner
must independently verify run/job/head, current policy and main,
exact expected journal ref/bytes, and canonical state transition;
stage a single-parent commit off-ref and perform one nonforced CAS,
then read back. Unknown or changed state => stop that transition.
This separates deterministic calculation from existing connector writes
without new credentials or paid services. No automatic production
integration authority, no public private data, no scheduler IDs.
The commissioning branch is not a production lock.


## Actual connector write and independent readback
Exact HEAD bafaa85... passed all four relevant workflows, 218/218 targeted
tests. Run 45816748182 job 139898330202 emitted the canonical proposal for
generation 5, digest 6ffe711ec91e2b96ef35a659c9e376f272be0431bd7fea9b7863b600dbcd1158.
The owner session checked exact prior journal bytes/ref, historical squash
parent/tree, current main, unchanged policy/G0 workflow, successful exact
G0 job step, and proposal context, then staged and non-forced CAS updated
the isolated journal. The orchestration call hit its tool-call limit after
the update; an independent subsequent read verified tip
fa5868c9a8789d7daed7a4f102fb258f81c9eb2c, exact terminal bytes, generation 5,
intent 2, QUALIFIED_READBACK, single parent 24026a19... and unchanged main.
No retry was attempted. This qualifies an actual durable recovery write
for a synthetic historical intent, not a real agent dispatch.
The new workflow reopens the terminal record and verifies no repeat write.

## Guarding the controller itself
Controller implementation and regression tests must be excluded from
ordinary code-only merge scope, even if they live under tools/tests.
The preflight path classifier now treats these files as owner governance.
This is a shadow guard, not a change of R13's effective policy; the final
R15-B policy revision must explicitly enforce the same exclusion.
