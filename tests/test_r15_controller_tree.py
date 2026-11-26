import unittest
from tools.smartsvg_controller_tree import _tree_hash, overlay_tree, disjoint_tree

A,B,C,D=("a"*40,"b"*40,"c"*40,"d"*40)
F=lambda sha:("100644",sha)

class DisjointTreeTests(unittest.TestCase):
    def test_disjoint_edits_and_additions(self):
        base={"engine/x":F(A),"tools/y":F(B)}
        main={"engine/x":F(A),"tools/y":F(C),"docs/z":F(D)}
        head={"engine/x":F(D),"tools/y":F(B),"tests/a":F(A)}
        self.assertEqual(overlay_tree(base,main,head),
            _tree_hash({"engine/x":F(D),"tools/y":F(C),"docs/z":F(D),"tests/a":F(A)}))

    def test_overlap_delete_and_mode_rejected(self):
        base={"x":F(A)}
        self.assertIsNone(overlay_tree(base,{"x":F(B)},{"x":F(C)}))
        self.assertIsNone(overlay_tree(base,{},{"x":F(C)}))
        self.assertIsNone(overlay_tree(base,{"x":("100755",A)},{"x":F(A)}))

    def test_file_directory_collision_rejected(self):
        self.assertIsNone(overlay_tree({},{"x":F(A)},{"x/y":F(B)}))

    def test_known_git_empty_tree_hash(self):
        self.assertEqual(_tree_hash({}),"4b825dc642cb6eb9a060e54bf8d69288fbee4904")

    def test_exact_tree_objects_and_corruption(self):
        states={A:{"x":F(A),"y":F(B)},B:{"x":F(C),"y":F(B)},C:{"x":F(A),"y":F(D)}}
        roots={k:_tree_hash(v) for k,v in states.items()}
        def get(path):
            if path.startswith("/compare/"):
                return {"status":"diverged","base_commit":{"sha":B},"merge_base_commit":{"sha":A},"ahead_by":1,"behind_by":1}
            if path.startswith("/git/commits/"):
                sha=path.rsplit("/",1)[1]
                return {"sha":sha,"tree":{"sha":roots[sha]}}
            root=path.rsplit("/",1)[1].split("?")[0]
            leaves=next(v for k,v in states.items() if roots[k]==root)
            return {"sha":root,"truncated":False,"tree":[{"path":k,"mode":v[0],"sha":v[1],"type":"blob"} for k,v in leaves.items()]}
        self.assertEqual(disjoint_tree(get,B,C),_tree_hash({"x":F(C),"y":F(D)}))
        def bad(path):
            r=get(path)
            if path.startswith("/git/trees/"):
                r["tree"][0]["sha"]=D
            return r
        self.assertIsNone(disjoint_tree(bad,B,C))
