"""Read-only qualification of a later main after an observed squash.

A descendant with a successful G0 is not proof of unchanged product semantics,
a review verdict, or permission to merge. Never re-use the old main's G0.
"""
from dataclasses import asdict
from .smartsvg_controller_live_reconcile import _g0, reconcile_live
from .smartsvg_controller_observation import _sha, POLICY
from .smartsvg_controller_decision import Status


def observe_successor(get, subject, original):
    result = {"state":"UNKNOWN","main":None,"merge_sha":None,"g0":None,
              "policy_blob":None,"qualification":"READBACK_ONLY",
              "merge_authorized":False,"retry_authorized":False}
    try:
        if original.get("state") != "MAIN_DRIFT" or not original.get("merge_sha"):
            return result
        if original.get("subject") != asdict(subject):
            return result
        merge, main = _sha(original["merge_sha"]), _sha(original["main"])
        if merge == main:
            return result
        result.update(main=main, merge_sha=merge)
        def comparison():
            c = get("/compare/" + merge + "..." + main)
            return (c.get("status"), c["base_commit"]["sha"],
                    c["merge_base_commit"]["sha"], c["ahead_by"], c["behind_by"])
        observed = comparison()
        if (observed[:3] != ("ahead",merge,merge)
                or type(observed[3]) is not int or observed[3] < 1
                or type(observed[4]) is not int or observed[4] != 0):
            result["state"] = "ANCESTRY_UNPROVED"
            return result
        policy = _sha(get(f"/contents/{POLICY}?ref={main}")["sha"])
        g0 = _g0(get, main)
        # Re-read both the original squash and the mutable workflow attempt.
        if (comparison() != observed or _g0(get,main) != g0
                or reconcile_live(get,subject) != original
                or _sha(get("/branches/main")["commit"]["sha"]) != main):
            result["state"] = "READBACK_DRIFT"
            return result
        result.update(policy_blob=policy,g0=dict(asdict(g0),status=g0.status.value))
        result["state"] = ("SUCCESSOR_G0_PASS" if g0.status is Status.PASS else
                           "SUCCESSOR_G0_FAILED" if g0.status is Status.FAIL else
                           "SUCCESSOR_G0_WAIT")
        return result
    except Exception:
        return result
