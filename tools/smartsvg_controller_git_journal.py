"""Pinned Git journal transport for the isolated R15-B commissioning branch.

The injected functions use GitHub connector calls; this module does not
provide credentials, a merge endpoint, or production authority.
"""
import base64
from hashlib import sha1
from .smartsvg_controller_cas import Record, decode, encode, prepare, transition, persist, _ref

REPO = "frenndak/SmartSVG-Studio"
BRANCH = "owner/r15b-journal-shadow-20261126"
GENESIS = "e7e13f8b7da3da1fc4cb85369a6c323172c9c90f"
GENESIS_PARENT = "f00f665d075259e521b4067d700d55b2a9b892ee"
MAX_HISTORY = 256


def validate_edge(old, new):
    if new.intent == old.intent + 1:
        expected = prepare(old, number=new.number, head=new.head, main=new.main,
                           tree=new.tree, policy=new.policy, evidence=new.evidence)
    else:
        expected = transition(old, new.state, new.evidence)
    if expected != new:
        raise ValueError("invalid history transition")


class JournalTransport:
    """Only the pinned commissioning branch; no arbitrary ref parameter.

    get(relative_path) returns the REST object. create_tree/create_commit/
    update_ref accept the installed connector's keyword arguments and
    return its normalized result dict (without the outer result wrapper).
    """
    def __init__(self, get, create_tree=None, create_commit=None, update_ref=None):
        self.get = get
        self.create_tree = create_tree
        self.create_commit = create_commit
        self.update_ref = update_ref

    def tip(self):
        data = self.get("/git/ref/heads/" + BRANCH)
        if data["ref"] != "refs/heads/" + BRANCH or data["object"]["type"] != "commit":
            raise ValueError("wrong journal ref")
        return _ref(data["object"]["sha"])

    def commit(self, sha):
        _ref(sha)
        data = self.get("/git/commits/" + sha)
        if data["sha"] != sha or len(data["parents"]) != 1:
            raise ValueError("wrong commit or parent count")
        parent = _ref(data["parents"][0]["sha"])
        tree_sha = _ref(data["tree"]["sha"])
        tree = self.get("/git/trees/" + tree_sha)
        if tree["sha"] != tree_sha or tree.get("truncated") is not False or len(tree["tree"]) != 1:
            raise ValueError("invalid journal tree")
        row = tree["tree"][0]
        if (row["path"], row["mode"], row["type"]) != ("state.json", "100644", "blob"):
            raise ValueError("invalid journal file")
        blob_sha = _ref(row["sha"])
        blob = self.get("/git/blobs/" + blob_sha)
        if blob["sha"] != blob_sha or blob["encoding"] != "base64":
            raise ValueError("invalid blob identity")
        raw = base64.b64decode("".join(blob["content"].split()), validate=True)
        if len(raw) != row["size"] or len(raw) != blob["size"] or len(raw) > 2048:
            raise ValueError("invalid blob length")
        if sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != blob_sha:
            raise ValueError("blob hash mismatch")
        decode(raw)
        return parent, raw

    def read(self):
        tip = self.tip()
        current = tip
        newest = None
        child = None
        for _ in range(MAX_HISTORY):
            parent, raw = self.commit(current)
            record = decode(raw)
            if newest is None:
                newest = raw
            if child is not None:
                validate_edge(record, child)
            if current == GENESIS:
                if parent != GENESIS_PARENT or record != Record():
                    raise ValueError("invalid genesis")
                if self.tip() != tip:
                    raise ValueError("journal drift")
                return tip, newest
            child, current = record, parent
        raise ValueError("journal history limit or missing genesis")

    def stage(self, parent, raw):
        tip, before = self.read()
        if parent != tip:
            raise ValueError("stale parent")
        validate_edge(decode(before), decode(raw))
        tree = _ref(self.create_tree(repository_full_name=REPO,
                    tree_elements=[{"path": "state.json", "mode": "100644",
                                    "type": "blob", "content": raw.decode("ascii")}])["sha"])
        sha = _ref(self.create_commit(repository_full_name=REPO,
                    message="test(r15b): shadow journal transition",
                    tree_sha=tree, parent_sha=parent)["sha"])
        if self.commit(sha) != (parent, raw):
            raise ValueError("staged commit mismatch")
        return sha

    def advance(self, expected, candidate):
        tip, before = self.read()
        parent, after = self.commit(candidate)
        if tip != expected or parent != expected:
            raise ValueError("stale or wrong parent")
        validate_edge(decode(before), decode(after))
        return self.update_ref(repository_full_name=REPO, branch_name=BRANCH,
                               sha=candidate, expected_sha=expected, force=False)

    def write(self, expected, previous, proposed):
        return persist(self.read, self.stage, self.advance, expected=expected,
                       previous=previous, proposed=proposed)
