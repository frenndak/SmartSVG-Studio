# R15-B — pinned shadow journal adapter

The isolated branch owner/r15b-journal-shadow-20261126 has exactly one
file, state.json. Genesis e7e13f8b7da3da1fc4cb85369a6c323172c9c90f is
anchored to f00f665d075259e521b4067d700d55b2a9b892ee. Live connector
commissioning in separate calls: PREPARED 87e94263136dd5749c8f8d1b5f5f6a3e39701c86,
restart readback, CANCELLED_PREPARED f5df4c1b101fb87c8681b4e55f1339edbc9ec124.
Both updates were non-forced and exact-parent/tree/bytes were checked.
Digests are synthetic; no merge was requested. This is not agent execution.

Adapter verifies pinned branch, single-parent chain to genesis, each
canonical transition, exact file-only tree and Git blob hash, and rechecks
ref after traversal. Writes stage off-ref, verify parent and bytes, then
use expected ref and force=false. No merge API or credentials. Read-only
CI replays the live journal; tests exercise the injected writer.

Limits: history bounded to 256 commits; production needs an independently
reviewed rollover/anchor plan, branch non-rewrite protections and verified
live receipts. Ruleset collection returned empty at commissioning; no claim
of enforced protection. Never use this branch as a production integration
lock. Connector injection is implemented but actual automated agent wiring
and authenticated scheduler receipt remain outstanding. R13 unchanged.
