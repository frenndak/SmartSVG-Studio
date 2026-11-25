"""Read-only R15 GitHub observation. Raw receipts are not merge authorization."""
from datetime import datetime, timezone
import json
import re
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import quote

ROOT = "https://api.github.com/repos/frenndak/SmartSVG-Studio"
SHA = re.compile(r"[0-9a-f]{40}")
POLICY = "docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md"


class ObservationError(RuntimeError):
    pass


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
    with build_opener(NoRedirect()).open(Request(ROOT + path, headers=headers), timeout=20) as r:
        raw = r.read(16 * 1024 * 1024 + 1)
    if len(raw) > 16 * 1024 * 1024:
        raise ObservationError("response too large")
    return json.loads(raw)


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


def observe(get=github_get):
    """Collect raw exact-head runs/jobs and review receipts; reject snapshot drift.

    A successful observation is NOT a verified policy, actual step PASS,
    independent A/B review, resolved-thread proof, or scheduler readback.
    Those remain separate gates. Errors propagate; no partial success returned.
    """
    started = datetime.now(timezone.utc).isoformat()
    main = get("/branches/main")
    main_sha = _sha(main["commit"]["sha"])
    policy = get(f"/contents/{POLICY}?ref={main_sha}")
    policy_sha = _sha(policy["sha"])
    def open_prs():
        return pages(get, "/pulls?state=open")
    def identity(rows):
        return sorted((p["number"], _sha(p["head"]["sha"])) for p in rows)
    initial = open_prs()
    if len({p["number"] for p in initial}) != len(initial):
        raise ObservationError("duplicate PR number")
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
    for number, head in identity(initial):
        p = get(f"/pulls/{number}")
        if p.get("number") != number or p.get("state") != "open" or p["head"]["sha"] != head:
            raise ObservationError("PR changed during collection")
        branch = branch_observation(get, p)
        if branch["status"] != "MATCH":
            candidates.append({"pr": p, "branch": branch, "runs": [],
                               "reviews": [], "comments": []})
            continue
        candidates.append({"pr": p, "branch": branch, "runs": runs_for(head, "pull_request"),
                           "reviews": pages(get, f"/pulls/{number}/reviews"),
                           "comments": pages(get, f"/issues/{number}/comments")})
    rulesets = pages(get, "/rulesets?includes_parents=true")
    if get("/branches/main")["commit"]["sha"] != main_sha or identity(open_prs()) != identity(initial):
        raise ObservationError("main or PR queue changed during collection")
    for entry in candidates:
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
