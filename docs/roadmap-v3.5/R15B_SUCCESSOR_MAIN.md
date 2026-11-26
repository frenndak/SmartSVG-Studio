# R15-B successor-main recovery

A previously observed squash may be followed by another legitimate product
merge. The recovery coordinator now collects separate read-only evidence for
the successor main: exact comparison base, ancestry, fresh push G0 and
current policy blob; it rechecks the original reconciliation and main.
The action remains REQUALIFY_CURRENT_MAIN even when the successor G0 passes:
semantic applicability and authority are not inferred from ancestry or CI.
No retry, merge, state mutation or authority transition.

The CI replay combines a synthetic historical intent with actual GitHub
readback of owner squash #196. It never writes the shadow journal and must
not be represented as an actual scheduled-agent dispatch. Unit tests cover
descendant, divergence, wrong base, failed/pending G0 and changed main.

Owner observation: no scheduled routing runs were returned for current
main or repository-wide schedule query; only push run 45758552417 was
returned. Workflow-specific listing is unsupported by the installed
connector; no workflow dispatch action available. Latest A/B cycles
reported NO_RUN and no new artifact. Do not extend stale route validity or
claim consumption. Continue R13 fallback and investigate runner availability.
