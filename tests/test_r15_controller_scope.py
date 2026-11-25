import unittest
from copy import deepcopy

from tools.smartsvg_controller_observation import ObservationError
from tools.smartsvg_controller_scope import inspect_scope

H,M,B = "a"*40,"b"*40,"c"*40
REPO = "frenndak/SmartSVG-Studio"


def fixture(files, *, base=M, count=None):
    pr={"number":195,"state":"open","changed_files":len(files) if count is None else count,
        "head":{"sha":H,"ref":"a/test","repo":{"full_name":REPO}},
        "base":{"sha":base,"ref":"main","repo":{"full_name":REPO}},
        "user":{"login":"frenndak"}}
    def get(path):
        if path=="/branches/main":
            return {"commit":{"sha":M}}
        if path=="/pulls/195":
            return deepcopy(pr)
        if path=="/git/ref/heads/a/test":
            return {"ref":"refs/heads/a/test","object":{"type":"commit","sha":H}}
        if path.startswith("/pulls/195/files?"):
            page=int(path.rsplit("=",1)[1])
            return deepcopy(files[(page-1)*100:page*100])
        raise AssertionError(path)
    return get


def row(path,status="modified",**kwargs):
    return {"filename":path,"status":status,"sha":B,"patch":"@@ example",**kwargs}


def inspect(get):
    return inspect_scope(get,195,head=H,main=M)


class ScopeTests(unittest.TestCase):
    def test_engine_and_test_only_classification(self):
        r=inspect(fixture([row("engine/a.py"),row("tests/test_a.py")]))
        self.assertTrue(r.engine_changed)
        self.assertTrue(r.base_matches_main)
        self.assertEqual(r.excluded_paths,())
        self.assertEqual(r.qualification,"PATHS_ONLY")
        self.assertEqual(len(r.inventory_digest),64)
        r=inspect(fixture([row("tests/test_a.py")]))
        self.assertFalse(r.engine_changed)

    def test_rename_checks_both_paths(self):
        r=inspect(fixture([row("tests/test_a.py","renamed",previous_filename="docs/policy.md")]))
        self.assertEqual(r.excluded_paths,("docs/policy.md",))
        self.assertIn("docs/policy.md",r.paths)

    def test_old_base_reported_not_rewritten(self):
        r=inspect(fixture([row("tests/test_a.py")],base=B))
        self.assertFalse(r.base_matches_main)
        self.assertEqual(r.base,B)

    def test_pagination_count_and_duplicate(self):
        files=[row("tests/test_"+str(i)+".py") for i in range(101)]
        self.assertEqual(len(inspect(fixture(files)).files),101)
        for get in (fixture(files,count=102),fixture([files[0],files[0]]),
                    fixture(files,count=3001)):
            with self.assertRaises(ObservationError):
                inspect(get)

    def test_branch_and_main_drift(self):
        source=fixture([row("tests/test_a.py")])
        for endpoint in ("/git/ref/heads/a/test","/branches/main","/pulls/195"):
            calls=0
            def get(path):
                nonlocal calls
                value=source(path)
                if path==endpoint:
                    calls+=1
                    if calls==2:
                        if endpoint=="/git/ref/heads/a/test":
                            value["object"]["sha"]=B
                        elif endpoint=="/branches/main":
                            value["commit"]["sha"]=B
                        else:
                            value["changed_files"]=2
                return value
            with self.assertRaises(ObservationError):
                inspect(get)

    def test_missing_patch_not_complete_diff(self):
        f=row("tests/test_a.py")
        del f["patch"]
        r=inspect(fixture([f]))
        self.assertIsNone(r.files[0].patch_digest)
        self.assertEqual(r.qualification,"PATHS_ONLY")

    def test_digest_binds_metadata_and_patch(self):
        a=row("tests/test_a.py")
        b=dict(a,patch="different")
        self.assertNotEqual(inspect(fixture([a])).inventory_digest,
                            inspect(fixture([b])).inventory_digest)
