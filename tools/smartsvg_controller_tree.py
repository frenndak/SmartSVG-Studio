"""Conservative read-only Git tree prediction for disjoint additive edits.

Reject deletions, type/mode changes, overlapping edits, unverified trees and
directory/file collisions. No rename heuristic, content merge, writes or
authorization. Reconstruct Git object hashes, not an approximation of SHA.
"""
from hashlib import sha1
from .smartsvg_controller_observation import _sha

MAX_ENTRIES = 20000
MODES = {"100644", "100755", "120000", "160000"}


def _tree_hash(leaves):
    root={}
    for path,(mode,sha) in leaves.items():
        parts=path.split("/")
        if any(not x or x in (".","..") or "\0" in x for x in parts):
            raise ValueError("invalid tree path")
        if mode not in MODES:
            raise ValueError("invalid leaf mode")
        node=root
        for part in parts[:-1]:
            node=node.setdefault(part,{})
            if not isinstance(node,dict):
                raise ValueError("tree path collision")
        if parts[-1] in node:
            raise ValueError("duplicate path")
        node[parts[-1]]=(mode,_sha(sha))

    def visit(node):
        rows=[]
        for name,value in node.items():
            directory=isinstance(value,dict)
            mode,sha=("40000",visit(value)) if directory else value
            key=name.encode("utf-8")
            rows.append((key+(b"/" if directory else b""),mode.encode()+b" "+key+b"\0"+bytes.fromhex(sha)))
        raw=b"".join(item[1] for item in sorted(rows))
        return sha1(b"tree "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    return visit(root)


def _leaves(get, commit_sha):
    commit=get("/git/commits/"+_sha(commit_sha))
    if commit.get("sha")!=commit_sha:
        raise ValueError("wrong commit")
    root=_sha(commit["tree"]["sha"])
    tree=get("/git/trees/"+root+"?recursive=1")
    if tree.get("sha")!=root or tree.get("truncated") is not False:
        raise ValueError("incomplete tree")
    rows=tree["tree"]
    if not isinstance(rows,list) or len(rows)>MAX_ENTRIES:
        raise ValueError("tree exceeds bound")
    seen=set()
    leaves={}
    for row in rows:
        path,mode,kind=row["path"],row["mode"],row["type"]
        if not isinstance(path,str) or path in seen:
            raise ValueError("duplicate tree entry")
        seen.add(path)
        sha=_sha(row["sha"])
        if mode=="040000" and kind=="tree":
            continue
        if (mode not in MODES or kind!=("commit" if mode=="160000" else "blob")):
            raise ValueError("unsupported entry")
        leaves[path]=(mode,sha)
    if _tree_hash(leaves)!=root:
        raise ValueError("tree hash not reconstructed")
    return leaves


def overlay_tree(base,current,proposed):
    """Only independent regular-file additions/edits; reject all deletions."""
    if not base.keys()<=current.keys() or not base.keys()<=proposed.keys():
        return None
    left={k for k,v in current.items() if base.get(k)!=v}
    right={k for k,v in proposed.items() if base.get(k)!=v}
    if left & right:
        return None
    for changes,tree in ((left,current),(right,proposed)):
        for k in changes:
            if tree[k][0] not in ("100644","100755") or (k in base and base[k][0]!=tree[k][0]):
                return None
    # Combining changes can create a file/directory conflict. Hash builder
    # detects collisions; no attempt to resolve them.
    try:
        return _tree_hash(dict(current,**{k:proposed[k] for k in right}))
    except (ValueError,UnicodeError,RecursionError):
        return None


def disjoint_tree(get,main,head):
    try:
        comparison=get("/compare/"+main+"..."+head)
        if (comparison.get("status")!="diverged" or comparison["base_commit"]["sha"]!=main
                or any(type(comparison.get(k)) is not int or comparison[k]<1 for k in ("ahead_by","behind_by"))):
            return None
        base=_sha(comparison["merge_base_commit"]["sha"])
        if base in (main,head):
            return None
        return overlay_tree(_leaves(get,base),_leaves(get,main),_leaves(get,head))
    except Exception:
        return None
