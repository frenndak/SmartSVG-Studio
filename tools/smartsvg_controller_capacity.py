"""R15-A bounded advisory new-work capacity, not a reservation or authorization.

A new task needs a live roadmap lot, dependencies, ownership and scope review.
This deliberately does not manufacture a PR number or fake a GitHub lease.
"""
def development_advice(report):
    assignments = report["assignments"]
    wip = report["code_wip"]
    if (type(wip) is not int or wip < 0
            or set(assignments) != {"A","B"}):
        raise ValueError("invalid work capacity")
    result = {"qualification":"ADVISORY_ONLY","available_slots":0,
              "roles":[],"reason":"QUEUE_INCOMPLETE"}
    # No inferred capacity for unknown scopes, drift or incomplete inventory.
    if report.get("queue_complete") is not True or report.get("unknown") != [] and report.get("unknown") != ():
        return result
    slots = max(0,3-wip)
    result["available_slots"] = slots
    if not slots:
        result["reason"]="WIP_FULL"
        return result
    idle = [role for role in ("A","B") if assignments[role] is None]
    # A gets first suggestion if only one slot and both are idle. B may
    # develop when A has an existing assignment; actual scopes stay separate.
    result["roles"] = idle[:slots]
    result["reason"] = "SELECT_ROADMAP_LOT" if result["roles"] else "EXISTING_ASSIGNMENTS"
    return result
