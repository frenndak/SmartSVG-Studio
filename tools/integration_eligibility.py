"""Fail-closed, read-only SmartSVG integration eligibility evaluator.

Input is a JSON snapshot of *fresh* GitHub API responses collected from a
trusted checkout on main. This command NEVER merges or marks a PR ready.
A positive result is advisory until HEAD/main are re-fetched before merging.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED = ("SmartSVG G0 - Admission Tests", "SmartSVG - Live Engine CPU Smoke")
EXPECTED_REPO = "frenndak/SmartSVG-Studio"


def _sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def _audited(comments, number, head):
    """Check actual audit receipt without treating issue comments as authorization."""
    for comment in reversed(comments):
        body = comment.get("body", "")
        if not isinstance(body, str) or not body.startswith("SMARTSVG_AUDIT_V1\n"):
            continue
        props = {}
        for line in body.splitlines()[1:]:
            if "=" in line:
                key, value = line.split("=", 1)
                props[key.strip()] = value.strip()
        if props.get("PR") == str(number) and props.get("HEAD") == head:
            # The newest matching audit supersedes an older positive verdict.
            return props.get("VERDICT") == "GO_POUR_REVUE_INTEGRATION"
    return False


def assess(snapshot):
    """Return a deterministic decision with all independent blockers."""
    blockers = []
    if not isinstance(snapshot, dict) or snapshot.get("schema") != 1:
        return {"status": "BLOCKED", "blockers": ["SNAPSHOT_INVALID"]}
    pr = snapshot.get("pr") or {}
    comparison = snapshot.get("comparison") or {}
    number = pr.get("number")
    head = (pr.get("head") or {}).get("sha")
    base = pr.get("base") or {}
    main = snapshot.get("main_sha")
    author = (pr.get("user") or {}).get("login")
    if snapshot.get("repo") != EXPECTED_REPO:
        blockers.append("REPO_MISMATCH")
    if (type(number) is not int or number <= 0 or
            not _sha(head) or not _sha(main) or
            not isinstance(author, str) or not author):
        return {"status": "BLOCKED", "blockers": blockers + ["IDENTITY_INVALID"]}
    if pr.get("state") != "open":
        blockers.append("PR_NOT_OPEN")
    if pr.get("draft") is not False:
        blockers.append("PR_DRAFT")
    if base.get("ref") != "main":
        blockers.append("STACK_PARENT_PENDING")
    if pr.get("mergeable") is not True:
        blockers.append("MERGEABILITY_UNKNOWN_OR_FALSE")
    if (comparison.get("status") != "ahead" or
            type(comparison.get("behind_by")) is not int or
            comparison["behind_by"] != 0 or
            type(comparison.get("ahead_by")) is not int or
            comparison["ahead_by"] < 1):
        blockers.append("MAIN_ANCESTRY_UNPROVEN")
    if snapshot.get("checked_head_sha") != head or snapshot.get("checked_main_sha") != main:
        blockers.append("STALE_SNAPSHOT")

    # Require an exhaustive GitHub changed-file inventory before deciding which
    # CI suites apply. A missing/truncated list MUST NOT waive CPU tests.
    changes = snapshot.get("changed_files")
    expected_files = pr.get("changed_files")
    if (not isinstance(changes, list) or not changes or
            type(expected_files) is not int or expected_files != len(changes)):
        blockers.append("CHANGESET_UNVERIFIED")
        needs_cpu = True
    else:
        paths = [item.get("filename") if isinstance(item, dict) else None
                 for item in changes]
        if (any(not isinstance(path, str) or not path or path.startswith("/")
                or "\\x00" in path or ".." in path.split("/") for path in paths)
                or len(set(paths)) != len(paths)):
            blockers.append("CHANGESET_UNVERIFIED")
            needs_cpu = True
        else:
            needs_cpu = any(path.startswith("engine/") for path in paths)

    workflows = snapshot.get("workflow_runs")
    if not isinstance(workflows, list):
        workflows = []
        blockers.append("WORKFLOWS_MISSING")
    for name in (REQUIRED if needs_cpu else REQUIRED[:1]):
        all_runs = [run for run in workflows if isinstance(run, dict)
                    and run.get("name") == name and run.get("head_sha") == head]
        # Even a direct-branch success cannot hide a newer failed/pending run
        # for the same workflow and exact candidate commit.
        sort_key = lambda r: (str(r.get("run_started_at") or r.get("created_at") or ""),
                              int(r.get("run_attempt") or 0), int(r.get("id") or 0))
        all_runs.sort(key=sort_key)
        direct = [run for run in all_runs
                  if run.get("event") == "workflow_dispatch"
                  and run.get("head_branch") == (pr.get("head") or {}).get("ref")]
        latest_all_ok = (bool(all_runs) and all_runs[-1].get("status") == "completed"
                         and all_runs[-1].get("conclusion") == "success")
        direct_ok = (bool(direct) and direct[-1].get("status") == "completed"
                     and direct[-1].get("conclusion") == "success")
        if not (latest_all_ok and direct_ok):
            blockers.append("CI_NOT_SUCCESS:" + name)

    reviews = snapshot.get("reviews")
    if not isinstance(reviews, list):
        reviews = []
        blockers.append("REVIEWS_MISSING")
    latest = {}
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login")
        if not isinstance(login, str):
            continue
        # Only the latest vote per reviewer counts. Dismissed and stale approvals
        # do not authorize integration.
        if login not in latest or str(review.get("submitted_at") or "") >= str(latest[login].get("submitted_at") or ""):
            latest[login] = review
    if any(v.get("state") == "CHANGES_REQUESTED" for v in latest.values()):
        blockers.append("UNRESOLVED_CHANGE_REQUEST")
    approvers = [v for login, v in latest.items()
                 if login != author and not login.endswith("[bot]")
                 and (v.get("user") or {}).get("type") == "User"
                 and v.get("state") == "APPROVED" and v.get("commit_id") == head]
    if not approvers:
        blockers.append("INDEPENDENT_GITHUB_APPROVAL_MISSING")

    comments = snapshot.get("audit_comments")
    if not isinstance(comments, list) or not _audited(comments, number, head):
        blockers.append("INDEPENDENT_AUDIT_GO_MISSING")
    return {
        "status": "ELIGIBLE_FOR_MAINTAINER_MERGE_REVIEW" if not blockers else "BLOCKED",
        "pr": number,
        "head_sha": head,
        "main_sha": main,
        "blockers": blockers,
        "automatic_merge_allowed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = assess(data)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "BLOCKED", "blockers": ["INVALID_INPUT:" + type(exc).__name__],
                  "automatic_merge_allowed": False}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "ELIGIBLE_FOR_MAINTAINER_MERGE_REVIEW" else 2


if __name__ == "__main__":
    sys.exit(main())
