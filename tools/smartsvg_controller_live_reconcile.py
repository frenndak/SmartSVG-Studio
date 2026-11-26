"""Read-only R15-B reconciliation of a merge attempt using GitHub facts.

A positive readback is evidence of repository state, not proof of who sent
a request, not a merger authorization, and not a substitute for review.
An open PR / timeout never authorizes retry. No mutation API is exposed.
"""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from .smartsvg_controller_observation import _sha, pages, ObservationError
from .smartsvg_controller_evidence import SPECS, step_receipts
from .smartsvg_controller_decision import Status

REPO="frenndak/SmartSVG-Studio"


@dataclass(frozen=True)
class Subject:
    number: int
    head: str
    prior_main: str
    expected_tree: str | None = None


def _identity(pr, subject):
    if (pr.get("number") != subject.number or pr.get("head",{}).get("sha") != subject.head
            or (pr.get("head",{}).get("repo") or {}).get("full_name") != REPO
            or (pr.get("base",{}).get("repo") or {}).get("full_name") != REPO
            or pr.get("base",{}).get("ref") != "main"
            or pr.get("user",{}).get("login") != "frenndak"):
        raise ObservationError("PR identity mismatch")
    return (pr.get("state"),pr.get("merged"),pr.get("merge_commit_sha"))


def _g0(get, sha):
    path,_,_=SPECS["g0"]
    runs=pages(get,"/actions/runs?head_sha="+sha+"&event=push","workflow_runs")
    matching=[]
    for run in runs:
        if run.get("head_sha")!=sha or run.get("event")!="push":
            raise ObservationError("unexpected run identity")
        if run.get("path")!=path:
            continue
        if run.get("head_branch")!="main":
            raise ObservationError("unexpected G0 branch")
        rid,attempt=run.get("id"),run.get("run_attempt")
        if type(rid) is not int or rid<1 or type(attempt) is not int or attempt<1:
            raise ObservationError("invalid G0 run identity")
        jobs=[]
        if run.get("status")=="completed" and run.get("conclusion")=="success":
            jobs=pages(get,f"/actions/runs/{rid}/attempts/{attempt}/jobs","jobs")
        matching.append({"run":run,"jobs":jobs})
    return step_receipts(sha,matching,event="push")[0]


def reconcile_live(get, subject):
    """Return reduced readback; tolerate failures without granting retries."""
    if (not isinstance(subject,Subject) or type(subject.number) is not int
            or subject.number<1):
        raise ValueError("invalid subject")
    _sha(subject.head)
    _sha(subject.prior_main)
    if subject.expected_tree is not None:
        _sha(subject.expected_tree)

    def result(state,*,main=None,merge=None,g0=None,reason=""):
        data={"subject":asdict(subject),"state":state,"main":main,"merge_sha":merge,
              "g0":None if g0 is None else dict(asdict(g0),status=g0.status.value),
              "reason":reason,"qualification":"LIVE_READBACK_ONLY",
              "merge_authorized":False,"retry_authorized":False}
        return dict(data,digest=sha256(json.dumps(data,sort_keys=True,
                    separators=(",",":"),allow_nan=False).encode()).hexdigest())

    try:
        main=_sha(get("/branches/main")["commit"]["sha"])
        path="/pulls/"+str(subject.number)
        identity=_identity(get(path),subject)
        state,merged,merge=identity
        if state=="open" and merged is False:
            if (_identity(get(path),subject)!=identity
                    or _sha(get("/branches/main")["commit"]["sha"])!=main):
                return result("UNKNOWN",reason="READBACK_DRIFT")
            return result("NEGATIVE_READBACK" if main==subject.prior_main else "MAIN_DRIFT",
                          main=main,reason="REQUEST_TERMINALITY_NOT_PROVED")
        if state!="closed" or merged is not True:
            return result("UNKNOWN",main=main,reason="NOT_MERGED_OR_UNAVAILABLE")
        merge=_sha(merge)
        if merge==subject.prior_main or merge==subject.head:
            return result("UNKNOWN",main=main,reason="UNEXPECTED_SQUASH_SHA")
        commit=get("/git/commits/"+merge)
        parents=commit.get("parents",[])
        if (commit.get("sha")!=merge or len(parents)!=1
                or parents[0].get("sha")!=subject.prior_main):
            return result("UNKNOWN",main=main,reason="SQUASH_PARENT_MISMATCH")
        tree=_sha(commit["tree"]["sha"])
        if subject.expected_tree is not None and tree!=subject.expected_tree:
            return result("UNKNOWN",main=main,reason="EXPECTED_TREE_MISMATCH")
        # A later main is not authorization to accept the old G0.
        if main!=merge:
            if (_identity(get(path),subject)!=identity
                    or _sha(get("/branches/main")["commit"]["sha"])!=main):
                return result("UNKNOWN",reason="READBACK_DRIFT")
            return result("MAIN_DRIFT",main=main,merge=merge,reason="REQUALIFY_CURRENT_MAIN")
        g0=_g0(get,merge)
        if (_g0(get,merge)!=g0 or _identity(get(path),subject)!=identity
                or _sha(get("/branches/main")["commit"]["sha"])!=main):
            return result("UNKNOWN",reason="READBACK_DRIFT")
        state=("MERGED_G0_PASS" if g0.status is Status.PASS else
               "G0_FAILED" if g0.status is Status.FAIL else "WAIT_G0")
        return result(state,main=main,merge=merge,g0=g0,
                      reason="STEP_READBACK_NOT_AUTHORITY")
    except Exception as exc:
        return result("UNKNOWN",reason=type(exc).__name__)
