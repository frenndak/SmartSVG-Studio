"""Advisory routing from correlated review receipts, never merge authority.

External packets are untrusted routing hints until their independent origin
and semantic content are verified. A favorable correlation changes the next
inspection task, not review qualification or any integration permission.
"""
from dataclasses import replace

from .smartsvg_controller_decision import Status
from .smartsvg_controller_review import ReviewContext, correlate_review


def route_review_hints(plan, snapshot, packets=()):
    if not isinstance(packets, (tuple, list)) or len(packets) > 100:
        raise ValueError("invalid review packet collection")
    by_number = {}
    ambiguous = set()
    for packet in packets:
        if not isinstance(packet, dict) or type(packet.get("number")) is not int:
            # Unaddressable optional evidence cannot select or cancel any PR.
            continue
        n = packet["number"]
        if n in by_number:
            ambiguous.add(n)
        by_number[n] = packet
    entries = {row["pr"]["number"]: row for row in snapshot["candidates"]}
    proposals = []
    for p in plan.proposals:
        packet = by_number.get(p.number)
        # Raw CI failures, unknown scope and owner governance are never
        # superseded by an advisory review packet.
        if p.action != "REVIEW" or packet is None or p.number in ambiguous:
            proposals.append(p)
            continue
        try:
            if (packet["head"], packet["main"], packet["policy_blob"], packet["writer"]) != (
                    p.head, plan.main, plan.policy_blob, p.writer):
                proposals.append(p)
                continue
            comment_id = packet["comment_id"]
            if type(comment_id) is not int:
                raise ValueError("invalid comment ID")
            matches = [c for c in entries[p.number]["comments"]
                       if c.get("id") == comment_id]
            if len(matches) != 1:
                proposals.append(p)
                continue
            ctx = ReviewContext(p.number, p.head, plan.main, plan.policy_blob,
                                p.writer, packet["author_run"],
                                packet["author_completed_at"], packet["head_committed_at"])
            result = correlate_review(ctx, packet["role"], packet["scheduler"], matches[0])
        except (KeyError, TypeError, ValueError, AttributeError):
            proposals.append(p)
            continue
        if result.status == "CORRELATED_ADVERSE":
            proposals.append(replace(p, action="VERIFY_FINDING",
                                     reasons=("ADVERSE_HINT_UNVERIFIED",)))
        elif result.status == "CORRELATED_FAVORABLE":
            missing = tuple(s.name + ":" + s.status.value
                            for s in p.steps if s.status is not Status.PASS)
            if missing:
                proposals.append(replace(p, action="CI_INSPECT",
                    reasons=("FAVORABLE_HINT_UNVERIFIED",
                             "CHECK_APPLICABILITY_OR_MISSING_EVIDENCE", *missing)))
            else:
                proposals.append(replace(p, action="QUALIFY_ONLY",
                    reasons=("FAVORABLE_HINT_UNVERIFIED",
                             "SEMANTIC_AND_LIVE_GATES_NOT_QUALIFIED")))
        else:
            proposals.append(p)
    return replace(plan, proposals=tuple(proposals))
