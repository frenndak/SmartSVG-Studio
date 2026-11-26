# R15-B recovery coordinator

The shadow recovery planner joins the pinned journal reader with the live
reconciliation adapter. It identifies idle, prepared, unresolved and
terminal intents without writing or dispatching. Unresolved intents
reconcile the exact recorded PR, head, parent, expected tree and historical
policy blob. A changed journal discards the readback. Unknown/negative
readbacks never permit retry; all outcomes leave unrelated development
available. The report is not a production qualification or integration
authority. Existing R13 remains effective.

The next steps are to qualify the coordinator against actual GitHub
observations, correlate scheduled-agent receipts, and define a separately
reviewed production journal and authority transition. The previous split
unittest output defect remains open.
