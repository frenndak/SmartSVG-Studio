"""R15.2 minimal objective planning contract, not an executor or authority.

An explicitly reviewed adapter supplies a bounded objective inventory and
independently observed criterion receipts. This pure planner has no network,
storage, credentials, merge or permission API. Observed criteria do not mean
an objective is qualified, integrated, or DONE. No inferred dependencies.
"""
from dataclasses import dataclass
import re

TOKEN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}")
REPO = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}/[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}")
SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
MAX_OBJECTIVES = 128
MAX_CRITERIA = 64
ROLES = ("A", "B")
STATUSES = ("PASS", "FAIL", "WAIT", "UNKNOWN")


def _matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _tokens(values, limit, *, nonempty=False):
    return (type(values) is tuple and len(values) <= limit
            and (bool(values) or not nonempty)
            and all(_matches(TOKEN, v) for v in values)
            and len(set(values)) == len(values))


@dataclass(frozen=True)
class Profile:
    project: str
    repository: str
    branch: str
    policy_blob: str
    roadmap_blob: str
    version: int = 1


@dataclass(frozen=True)
class Objective:
    key: str
    revision: str
    role: str
    criteria: tuple
    dependencies: tuple = ()
    priority: int = 50
    age: int = 0
    preparation_allowed: bool = False


@dataclass(frozen=True)
class Receipt:
    profile: Profile
    main: str
    objective: str
    revision: str
    criterion: str
    status: str
    executed: bool
    digest: str


@dataclass(frozen=True)
class Advice:
    objective: str
    role: str
    action: str
    criteria: tuple
    blockers: tuple
    qualification: str = "ADVISORY_ONLY"


@dataclass(frozen=True)
class Plan:
    profile: Profile
    main: str
    objectives: tuple
    ignored_receipts: int
    qualification: str = "ADVISORY_ONLY"
    merge_authorized: bool = False
    agent_work_executed: bool = False


def _validate_profile(profile):
    if (type(profile) is not Profile or type(profile.version) is not int
            or profile.version != 1
            or not _matches(TOKEN, profile.project)
            or not _matches(REPO, profile.repository)
            or not _matches(TOKEN, profile.branch)
            or not _matches(SHA, profile.policy_blob)
            or not _matches(SHA, profile.roadmap_blob)):
        raise ValueError("invalid project profile")


def _validate_objective(o):
    if (type(o) is not Objective or not _matches(TOKEN, o.key)
            or not _matches(SHA, o.revision) or o.role not in ROLES
            or not _tokens(o.criteria, MAX_CRITERIA, nonempty=True)
            or not _tokens(o.dependencies, MAX_OBJECTIVES)
            or type(o.priority) is not int or not 0 <= o.priority <= 100
            or type(o.age) is not int or not 0 <= o.age <= 10000
            or type(o.preparation_allowed) is not bool):
        raise ValueError("invalid objective")


def _receipt_valid(r, profile, main, by_key):
    if (type(r) is not Receipt or r.profile != profile or r.main != main
            or not _matches(TOKEN, r.objective)
            or not _matches(TOKEN, r.criterion)
            or r.status not in STATUSES or type(r.executed) is not bool
            or not _matches(DIGEST, r.digest)):
        return False
    o = by_key.get(r.objective)
    return bool(o and r.revision == o.revision and r.criterion in o.criteria
                and (r.status not in ("PASS", "FAIL") or r.executed is True))


def plan_objectives(profile, main, objectives, receipts=()):
    """Use exact-context receipts; isolate unknown dependencies and cycles.

    No result authorizes creating a PR, transferring a writer, skipping a
    review, or promoting a criterion. The caller must re-read mutable facts
    and enforce existing policy. Preparation is separately opted in, never
    equivalent to qualifying an objective with unfinished dependencies.
    """
    _validate_profile(profile)
    if (not _matches(SHA, main) or type(objectives) is not tuple
            or len(objectives) > MAX_OBJECTIVES or type(receipts) is not tuple
            or len(receipts) > MAX_OBJECTIVES * MAX_CRITERIA * 4):
        raise ValueError("invalid objective inventory")
    by_key = {}
    for o in objectives:
        _validate_objective(o)
        if o.key in by_key:
            raise ValueError("duplicate objective")
        by_key[o.key] = o

    # DFS stack identifies cycle members; a descendant is blocked, not
    # mislabeled as a cycle member. The inventory is explicitly bounded.
    visited, active, stack, cycles = set(), set(), [], set()
    def visit(key):
        if key in active:
            cycles.update(stack[stack.index(key):])
            return
        if key in visited:
            return
        active.add(key)
        stack.append(key)
        for dep in by_key[key].dependencies:
            if dep in by_key:
                visit(dep)
        stack.pop()
        active.remove(key)
        visited.add(key)
    for key in sorted(by_key):
        visit(key)

    observed = {}
    digest_scopes = {}
    ignored = 0
    for r in receipts:
        if not _receipt_valid(r, profile, main, by_key):
            ignored += 1
            continue
        key = (r.objective, r.criterion)
        observed.setdefault(key, set()).add((r.status, r.digest))
        digest_scopes.setdefault(r.digest, set()).add(key)
    # A receipt identity is criterion-scoped. A verifier may reuse a source
    # document, but it must emit distinct criterion-bound receipt identities.
    ambiguous = {scope for scopes in digest_scopes.values() if len(scopes) > 1
                 for scope in scopes}
    def status(key, criterion):
        scope = (key, criterion)
        values = observed.get(scope, set())
        statuses = {state for state, _ in values}
        if scope in ambiguous or len(statuses) != 1:
            return "UNKNOWN"
        return next(iter(statuses))

    results = {}
    def evaluate(key):
        if key in results:
            return results[key]
        o = by_key[key]
        if key in cycles:
            result = Advice(key, o.role, "BLOCKED_GRAPH", (), ("DEPENDENCY_CYCLE",))
        else:
            missing = tuple(sorted(dep for dep in o.dependencies if dep not in by_key))
            known = [(dep, evaluate(dep)) for dep in o.dependencies if dep in by_key]
            invalid = tuple(sorted(dep for dep, result in known
                                   if result.action == "BLOCKED_GRAPH"))
            waiting = tuple(sorted(dep for dep, result in known
                                   if result.action != "CRITERIA_OBSERVED"))
            states = {c: status(key, c) for c in o.criteria}
            if missing or invalid:
                result = Advice(key, o.role, "BLOCKED_GRAPH", (),
                                tuple("UNKNOWN:" + d for d in missing) +
                                tuple("BLOCKED:" + d for d in invalid))
            elif waiting:
                result = Advice(key, o.role,
                                "PREPARE_INDEPENDENT" if o.preparation_allowed
                                else "WAIT_DEPENDENCY", (), waiting)
            elif any(s == "FAIL" for s in states.values()):
                result = Advice(key, o.role, "REPAIR_CRITERION",
                                tuple(c for c in o.criteria if states[c] == "FAIL"), ())
            elif any(s == "UNKNOWN" for s in states.values()):
                result = Advice(key, o.role, "VERIFY_CRITERION",
                                tuple(c for c in o.criteria if states[c] == "UNKNOWN"), ())
            elif any(s == "WAIT" for s in states.values()):
                result = Advice(key, o.role, "WAIT_EVIDENCE",
                                tuple(c for c in o.criteria if states[c] == "WAIT"), ())
            else:
                result = Advice(key, o.role, "CRITERIA_OBSERVED", o.criteria, ())
        results[key] = result
        return result
    for key in sorted(by_key):
        evaluate(key)

    # Rank only advisory actions. Count downstream depth in the valid DAG;
    # incomplete or cyclic paths cannot manufacture criticality.
    children = {key: [] for key in by_key}
    for key, o in by_key.items():
        if results[key].action == "BLOCKED_GRAPH":
            continue
        for dep in o.dependencies:
            children[dep].append(key)
    depths = {}
    def depth(key):
        if key not in depths:
            depths[key] = max((1 + depth(child) for child in children[key]), default=0)
        return depths[key]
    order = {"REPAIR_CRITERION": 0, "VERIFY_CRITERION": 1,
             "PREPARE_INDEPENDENT": 2, "WAIT_EVIDENCE": 3,
             "WAIT_DEPENDENCY": 4, "BLOCKED_GRAPH": 5, "CRITERIA_OBSERVED": 6}
    # Bounded age advantage allows older work to overtake within an action
    # class. The age value is an adapter-supplied observation, not a clock.
    ranked = sorted(results.values(), key=lambda a: (
        order[a.action], by_key[a.objective].priority - min(100, by_key[a.objective].age),
        -depth(a.objective), -by_key[a.objective].age, a.objective))
    return Plan(profile, main, tuple(ranked), ignored)


def next_objective(plan, role):
    """Select useful work for a role, never a reservation or mutation."""
    if type(plan) is not Plan or role not in ROLES:
        raise ValueError("invalid selection")
    return next((a for a in plan.objectives if a.role == role and a.action in
                 ("REPAIR_CRITERION", "VERIFY_CRITERION", "PREPARE_INDEPENDENT")), None)
