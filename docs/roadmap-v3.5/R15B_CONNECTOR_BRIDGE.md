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
