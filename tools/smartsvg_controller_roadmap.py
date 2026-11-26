"""Reviewed lot-level routing hints, not normative status or authorization.

The rank map reflects the current MASTER_PRIORISE delivery order. It is
pinned to its reviewed blob; if the document changes, fall back without
blocking normal routing. A lot label is only a hint, not semantic scope.
"""
import re

PATH = "docs/roadmap-v3.5/MASTER_PRIORISE.md"
PIN = "ec4f2e1dc5102840697c466b86fdc2ce99726f4b"
# Coarse first-entry order only. Transverse W00/W13/W15 and mixed lots
# require the affected consumer's scope; don't invent a global priority.
RANKS = {"W01":1,"W02":2,"W03":3,"W04":3,"W05":4,"W06":4,
         "W07":5,"W08":5,"W10":7,"W11":7,"W12":8,"W14":9,"W09":10,"W16":11}
LOT = re.compile(r"(?<![A-Za-z0-9])W(?:0[0-9]|1[0-6])(?![A-Za-z0-9])", re.I)


def explicit_lot(pr):
    title = pr.get("title")
    ref = pr.get("head",{}).get("ref")
    if not isinstance(title,str) or not isinstance(ref,str):
        return None
    t = {x.upper() for x in LOT.findall(title)}
    b = {x.upper() for x in LOT.findall(ref)}
    if len(t) != 1 or t != b:
        return None
    lot = next(iter(t))
    return lot if lot in RANKS else None


def roadmap_advice(snapshot,get):
    result={"qualification":"ADVISORY_ONLY","status":"UNAVAILABLE","source_blob":None,
            "candidates":[]}
    try:
        main=snapshot["main"]["commit"]["sha"]
        source=get(f"/contents/{PATH}?ref={main}")
        if source.get("sha") != PIN:
            result["status"]="ROADMAP_CHANGED"
            return {},result
        result.update(status="REVIEWED_ORDER",source_blob=PIN)
        ranks={}
        for entry in snapshot["candidates"]:
            pr=entry["pr"]
            lot=explicit_lot(pr)
            n=pr.get("number")
            if lot is not None and type(n) is int and n>0:
                ranks[n]=RANKS[lot]
                result["candidates"].append({"number":n,"lot":lot,"rank":RANKS[lot]})
        result["candidates"].sort(key=lambda x:x["number"])
        return ranks,result
    except (KeyError,TypeError,ValueError,AttributeError,OSError,RuntimeError):
        return {},{"qualification":"ADVISORY_ONLY","status":"UNAVAILABLE",
                   "source_blob":None,"candidates":[]}
