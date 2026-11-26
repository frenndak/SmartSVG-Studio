# R15-B — stale merge preview recovery

Initial commissioning 45838368201 job 139973145085 passed all five
exact candidate CI receipts, but expected_tree=null. Real #195 preview
3eacf0177a863ad301a49f2baeb8477219a30f75 has parents c161e663... and
7e557c8..., not current main 492e442.... It is stale, not evidence of
a conflict. Never accept that tree as current.

Read-only conservative disjoint prediction reconstructs Git tree hashes
from complete recursive trees for comparison merge base, main and head.
Reject deletion, changed file modes, nonregular modified files, any
overlap, path collisions, truncated trees or hash mismatch. No content
merge, rename handling or mutation. No claim of actual squash until
post-merge verification. If unavailable, retain existing R13 fallback
before an intent; no additional rebase solely for missing prediction.

Five focused regressions and a real #195 commissioning assertion added.
Prior 232/232 targeted PASS; exact new CI pending. B still needs actual
distinct technical review and all R13 gates. No production journal writes.
