"""Read-only R15 GitHub observation. Raw receipts are not merge authorization."""
from datetime import datetime, timezone
import json
import re
import time
from http.client import RemoteDisconnected, IncompleteRead
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import quote

ROOT = "https://api.github.com/repos/frenndak/SmartSVG-Studio"
SHA = re.compile(r"[0-9a-f]{40}")
POLICY = "docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md"


class ObservationError(RuntimeError):
    pass


class QueueChanged(ObservationError):
    """The open queue changed during a read-only snapshot."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def github_get(path, token=None):
    """GET only; no redirects, writes, or credential persistence."""
    if not path.startswith("/") or path.startswith("//") or "#" in path:
        raise ObservationError("invalid relative endpoint")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "SmartSVG-R15-shadow"}
    if token:
        headers["Authorization"] = "Bearer " + token
    # Only an idempotent GET may be retried, once, for a narrow transient
    # transport failure. No retry of auth, rate-limit, malformed data,
    # context mismatch, or mutation. Callers still revalidate identities.
    for attempt in range(2):
        try:
            with build_opener(NoRedirect()).open(Request(ROOT + path, headers=headers), timeout=20) as r:
                raw = r.read(16 * 1024 * 1024 + 1)
            if len(raw) > 16 * 1024 * 1024:
                raise ObservationError("response too large")
            return json.loads(raw)
        except HTTPError as exc:
            retry = exc.code in (502, 503, 504) and not exc.headers.get("Retry-After")
            exc.close()
            if attempt or not retry:
                raise
        except URLError as exc:
            if attempt or not isinstance(exc.reason, (TimeoutError, ConnectionResetError, RemoteDisconnected)):
                raise
        except (TimeoutError, ConnectionResetError, RemoteDisconnected, IncompleteRead):
            if attempt:
                raise
        time.sleep(0.25)


def _sha(value):
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ObservationError("invalid SHA")
    return value


def pages(get, path, key=None, limit=50):
    """Explicit bounded pagination; reject count drift and duplicate IDs."""
    result, ids, count = [], set(), None
    for page in range(1, limit + 1):
        sep = "&" if "?" in path else "?"
        data = get(f"{path}{sep}per_page=100&page={page}")
        rows = data if key is None else data[key]
        if not isinstance(rows, list) or len(rows) > 100:
            raise ObservationError("invalid page")
        if key is not None:
            total = data.get("total_count")
            if type(total) is not int or total < 0 or (count is not None and count != total):
                raise ObservationError("collection count drift")
            count = total
        for row in rows:
            ident = row.get("id")
            if type(ident) is not int or ident in ids:
                raise ObservationError("missing or duplicate collection ID")
            ids.add(ident)
            result.append(row)
        if len(rows) < 100:
            if count is not None and len(result) != count:
                raise ObservationError("incomplete collection")
            return result
    raise ObservationError("pagination limit reached")


def branch_observation(get, pr):
    """A PR projection may lag its real branch; quarantine just that item."""
    h = pr["head"]
    repo = h.get("repo") or {}
    ref = h.get("ref")
    if repo.get("full_name") != "frenndak/SmartSVG-Studio":
        return {"status": "FOREIGN_OR_UNKNOWN", "sha": None}
    if (not isinstance(ref, str) or not ref or
            any(x in ("", ".", "..") for x in ref.split("/"))):
        return {"status": "INVALID_REF", "sha": None}
    try:
        data = get("/git/ref/heads/" + quote(ref, safe="/"))
        if data.get("ref") != "refs/heads/" + ref or data["object"]["type"] != "commit":
            return {"status": "INVALID_REF_RESPONSE", "sha": None}
        sha = _sha(data["object"]["sha"])
        return {"status": "MATCH" if sha == h["sha"] else "DIVERGED", "sha": sha}
    except Exception as exc:
        return {"status": "UNAVAILABLE", "sha": None, "error": type(exc).__name__}


def _open_queue(get):
    result = {}
    for row in pages(get, "/pulls?state=open"):
        number = row.get("number")
        if type(number) is not int or number < 1 or number in result:
            raise ObservationError("invalid or duplicate open PR number")
        head = row.get("head")
        sha = head.get("sha") if isinstance(head, dict) else None
        valid_head = isinstance(sha, str) and SHA.fullmatch(sha) is not None
        result[number] = (row, sha if valid_head else None)
    return result


def _unavailable_candidate(pr, reason):
    return {"pr": pr, "branch": {"status": "UNAVAILABLE", "sha": None},
            "runs": [], "reviews": [], "comments": [], "collection_error": reason}


def observe(get=github_get, *, isolate_head_churn=False):
    """Collect raw exact-head runs/jobs and review receipts; reject snapshot drift.

    A successful observation is NOT a verified policy, actual step PASS,
    independent A/B review, resolved-thread proof, or scheduler readback.
    Those remain separate gates. Global errors propagate. Candidate-local
    read errors are explicitly quarantined; no partial receipts retained.
    A caller retrying the snapshot may isolate changed heads while still
    requiring stable queue membership and main.
    """
    started = datetime.now(timezone.utc).isoformat()
    main = get("/branches/main")
    main_sha = _sha(main["commit"]["sha"])
    policy = get(f"/contents/{POLICY}?ref={main_sha}")
    policy_sha = _sha(policy["sha"])
    initial = _open_queue(get)
    def runs_for(sha, event):
        runs = pages(get, f"/actions/runs?head_sha={sha}&event={event}", "workflow_runs")
        out = []
        for run in runs:
            if run.get("head_sha") != sha or run.get("event") != event:
                raise ObservationError("unexpected workflow head or event")
            attempt = run.get("run_attempt")
            if type(attempt) is not int or attempt < 1:
                raise ObservationError("invalid workflow attempt")
            jobs = pages(get, f"/actions/runs/{run['id']}/attempts/{attempt}/jobs", "jobs")
            if any(j.get("run_id") != run["id"] or j.get("head_sha") != sha or
                   j.get("run_attempt") != attempt for j in jobs):
                raise ObservationError("unexpected job provenance")
            out.append({"run": run, "jobs": jobs})
        return out
    main_runs = runs_for(main_sha, "push")
    candidates = []
    # Failures confined to one PR must not erase independent usable work.
    # Global main/policy/rules/queue collection is still fail-closed.
    candidate_errors = (ObservationError, OSError, IncompleteRead, KeyError,
                        TypeError, ValueError, AttributeError, OverflowError)
    for number, (listed, head) in sorted(initial.items()):
        if head is None:
            candidates.append(_unavailable_candidate(listed, "ObservationError"))
            continue
        try:
            p = get(f"/pulls/{number}")
            if (not isinstance(p,dict) or type(p.get("number")) is not int
                    or not isinstance(p.get("state"),str)):
                raise ObservationError("invalid candidate detail")
            detail_head = _sha(p["head"]["sha"])
            if (not isinstance(p["head"].get("repo"),dict)
                    or not isinstance(p.get("base"),dict)
                    or not isinstance(p.get("user"),dict)):
                # Some read-only test projections intentionally omit optional
                # base/user; a present malformed value is never accepted.
                if (not isinstance(p["head"].get("repo"),dict)
                        or ("base" in p and not isinstance(p["base"],dict))
                        or ("user" in p and not isinstance(p["user"],dict))):
                    raise ObservationError("invalid candidate repository detail")
            # Nested base repository metadata is consumed by manifests and
            # must be checked here, not after leaving the isolation boundary.
            if ("base" in p and "repo" in p["base"]
                    and p["base"]["repo"] is not None
                    and not isinstance(p["base"]["repo"],dict)):
                raise ObservationError("invalid candidate base repository")
        except candidate_errors as exc:
            candidates.append(_unavailable_candidate(listed, type(exc).__name__))
            continue
        if p.get("number") != number or p.get("state") != "open":
            raise QueueChanged("PR changed during collection")
        if detail_head != head:
            if not isolate_head_churn:
                raise QueueChanged("PR head changed during detail read")
            candidates.append(_unavailable_candidate(listed, "CandidateHeadChanged"))
            continue
        branch = branch_observation(get, p)
        if branch["status"] != "MATCH":
            candidates.append({"pr": p, "branch": branch, "runs": [],
                               "reviews": [], "comments": []})
            continue
        try:
            runs = runs_for(head, "pull_request")
            # Exercise the same normalizer the planner will consume here.
            # Malformed step payloads must not escape candidate isolation.
            from .smartsvg_controller_evidence import step_receipts
            step_receipts(head, runs)
            reviews = pages(get, f"/pulls/{number}/reviews")
            comments = pages(get, f"/issues/{number}/comments")
        except candidate_errors as exc:
            # Discard ALL partial receipts for the affected PR. A successful
            # branch read is not proof of complete CI or review inventory.
            candidates.append({"pr":p,"branch":branch,
                               "runs":[],"reviews":[],"comments":[],
                               "collection_error":type(exc).__name__})
            continue
        candidates.append({"pr":p,"branch":branch,"runs":runs,
                           "reviews":reviews,"comments":comments})
    rulesets = pages(get, "/rulesets?includes_parents=true")
    if get("/branches/main")["commit"]["sha"] != main_sha:
        raise ObservationError("main changed during collection")
    final = _open_queue(get)
    if final.keys() != initial.keys():
        raise QueueChanged("PR queue changed during collection")
    if get("/branches/main")["commit"]["sha"] != main_sha:
        raise ObservationError("main changed during final queue read")
    for index, entry in enumerate(candidates):
        number = entry["pr"]["number"]
        before, after = initial[number][1], final[number][1]
        if before is None or after is None:
            candidates[index] = _unavailable_candidate(initial[number][0], "ObservationError")
            continue
        if before != after:
            if not isolate_head_churn:
                raise QueueChanged("PR head changed during collection")
            candidates[index] = _unavailable_candidate(final[number][0], "CandidateHeadChanged")
            continue
        if entry["branch"]["status"] == "MATCH":
            latest = branch_observation(get, entry["pr"])
            if latest["status"] != "MATCH":
                entry["branch"] = latest
                entry["runs"], entry["reviews"], entry["comments"] = [], [], []
    return {"started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
            "main": main, "policy_blob": policy_sha, "main_runs": main_runs,
            "candidates": candidates, "rulesets": rulesets,
            "qualification": "RAW_ONLY", "scheduler_verified": False,
            "threads_verified": False, "authority_verified": False}
