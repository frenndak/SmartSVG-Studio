# R15-B — dedicated Git-ref CAS commissioning (2026-11-26)

Shadow-only. No integration authority change. R13 remains effective.

## Live connector probe

Dedicated branch `owner/r15b-cas-probe-20261126`, initial main
`f00f665d075259e521b4067d700d55b2a9b892ee`. Two distinct sibling commits:
`f265b1741bea863a41162bbf4e89fb3c52ab1be4` and
`c0b87826dae944b69440c29bfe17dfaf6bceea07`. First non-forced update
with expected initial SHA returned success. Second stale update with the
same expected SHA returned a generic connector GraphQL error. Exact
branch comparison with first commit returned identical and state file
readback returned candidate 1. No writes to main or agent branches.
This demonstrates one stale sibling contention case; not a proof of
all transport failure modes or branch protection. Leave probe isolated.

## Implementation contract

The pure CAS rehearsal stores canonical public-only metadata, one
unresolved intent at a time, exact PR/head/main/tree/policy and evidence
digest, monotonic generations and explicit pre-dispatch cancellation.
It stages a single-parent commit, requests a non-forced ref update,
and always reads back exact candidate plus canonical bytes. An unchanged
ref after a failed request is ambiguous; never retry automatically.
No raw logs, scheduler IDs, comments, tokens, arbitrary payloads.
History in Git is durable only while history is not rewritten.

The callback adapter is not production transport. Before activating:
verify exact branch pin and parent/tree, enforce no deletion or force
updates (including other authorized writers), verify independent live
receipts and scheduler authority, prove restart and concurrent races
with the production caller; prove terminal rejection explicitly and
handle historical duplicate intent IDs. A SHA/digest alone is not proof
of authorization. QUALIFIED_READBACK here is a rehearsal transition,
not an authenticated merge outcome. No production writer or automatic
merger enabled; unresolved integration does not prevent unrelated
development, CI or review. No new paid service.
