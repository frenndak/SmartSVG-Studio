import base64
from hashlib import sha1
import unittest
from tools.smartsvg_controller_cas import Record, encode, decode, prepare, transition
from tools.smartsvg_controller_git_journal import (
    JournalTransport, PilotJournalTransport, BRANCH, GENESIS, GENESIS_PARENT, REPO)

A,B,C,D = (x*40 for x in "abcd")
E = "e"*64


class GitJournalTests(unittest.TestCase):
    def setUp(self):
        self.objects = {}
        self.ref = GENESIS
        self.next = 0
        self.calls = []
        self.initial = Record()
        self.prepared = prepare(self.initial, number=196, head=A, main=B,
                                tree=C, policy=D, evidence=E)
        self.add(GENESIS, GENESIS_PARENT, encode(self.initial))
        self.transport = JournalTransport(self.get, self.tree, self.commit, self.advance)

    def add(self, sha, parent, raw):
        t = sha1(b"tree" + raw).hexdigest()
        b = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.objects["/git/commits/"+sha] = {"sha":sha,"parents":[{"sha":parent}],"tree":{"sha":t}}
        self.objects["/git/trees/"+t] = {"sha":t,"truncated":False,"tree":[
            {"path":"state.json","mode":"100644","type":"blob","sha":b,"size":len(raw)}]}
        self.objects["/git/blobs/"+b] = {"sha":b,"encoding":"base64","size":len(raw),
                                            "content":base64.b64encode(raw).decode()}
        return t

    def get(self, path):
        if path == "/git/ref/heads/"+BRANCH:
            return {"ref":"refs/heads/"+BRANCH,"object":{"type":"commit","sha":self.ref}}
        return self.objects[path]

    def tree(self, **args):
        self.assertEqual(args["repository_full_name"], REPO)
        self.assertNotIn("base_tree_sha", args)
        self.raw = args["tree_elements"][0]["content"].encode()
        return {"sha":sha1(b"tree"+self.raw).hexdigest()}

    def commit(self, **args):
        self.next += 1
        sha = f"{self.next:040x}"
        self.assertEqual(self.add(sha,args["parent_sha"],self.raw),args["tree_sha"])
        return {"sha":sha}

    def advance(self, **args):
        self.calls.append(args)
        self.assertFalse(args["force"])
        self.assertEqual(args["branch_name"],BRANCH)
        self.assertEqual(args["expected_sha"],self.ref)
        self.ref = args["sha"]
        return {"success":True}

    def test_restart_and_cancel(self):
        self.assertEqual(self.transport.write(GENESIS,self.initial,self.prepared).state,"APPLIED")
        restarted = JournalTransport(self.get,self.tree,self.commit,self.advance)
        ref, raw = restarted.read()
        self.assertEqual(decode(raw),self.prepared)
        cancelled = transition(self.prepared,"CANCELLED_PREPARED",E)
        self.assertEqual(restarted.write(ref,self.prepared,cancelled).state,"APPLIED")
        self.assertEqual(decode(restarted.read()[1]),cancelled)
        self.assertEqual(len(self.calls),2)

    def test_history_rejects_illegal_edge(self):
        self.add(A,GENESIS,encode(transition(self.prepared,"DISPATCH_UNKNOWN",E)))
        self.ref=A
        with self.assertRaises(ValueError):
            self.transport.read()

    def test_missing_genesis(self):
        self.add(A,B,encode(self.prepared))
        self.ref=A
        with self.assertRaises(KeyError):
            self.transport.read()

    def test_tree_has_no_other_files(self):
        t=self.get("/git/commits/"+GENESIS)["tree"]["sha"]
        self.get("/git/trees/"+t)["tree"].append({"path":"extra"})
        with self.assertRaises(ValueError):
            self.transport.read()

    def test_blob_hash_mismatch(self):
        t=self.get("/git/commits/"+GENESIS)["tree"]["sha"]
        b=self.get("/git/trees/"+t)["tree"][0]["sha"]
        self.get("/git/blobs/"+b)["content"]=base64.b64encode(b" "*len(encode(self.initial))).decode()
        with self.assertRaises(ValueError):
            self.transport.read()

    def test_stale_writer_no_advance(self):
        self.transport.write(GENESIS,self.initial,self.prepared)
        self.assertEqual(self.transport.write(GENESIS,self.initial,self.prepared).state,"STALE")
        self.assertEqual(len(self.calls),1)

    def test_staged_wrong_parent_refused(self):
        self.add(A,B,encode(self.prepared))
        with self.assertRaises(ValueError):
            self.transport.advance(GENESIS,A)
        self.assertEqual(self.calls,[])

    def test_single_pilot_rejects_new_intent_after_qualified_readback(self):
        pilot = PilotJournalTransport(self.get, self.tree, self.commit, self.advance)
        dispatched = transition(self.prepared, "DISPATCH_UNKNOWN", E)
        done = transition(dispatched, "QUALIFIED_READBACK", E)
        again = prepare(done, number=197, head=A, main=B, tree=C, policy=D, evidence=E)
        # Generic commissioning history remains reusable.
        JournalTransport.validate_edge(done, again)
        with self.assertRaisesRegex(ValueError, "pilot already qualified"):
            pilot.validate_edge(done, again)
        cancelled = transition(self.prepared, "CANCELLED_PREPARED", E)
        pilot.validate_edge(cancelled, prepare(cancelled, number=197, head=A,
                                              main=B, tree=C, policy=D, evidence=E))

    def test_pilot_read_rejects_history_continuing_after_qualification(self):
        pilot = PilotJournalTransport(self.get, self.tree, self.commit, self.advance)
        def get(path):
            if path == "/git/ref/heads/" + pilot.branch:
                return {"ref": "refs/heads/" + pilot.branch,
                        "object": {"type": "commit", "sha": self.ref}}
            return self.get(path)
        pilot.get = get
        self.add(pilot.genesis, pilot.genesis_parent, encode(self.initial))
        prev = pilot.genesis
        dispatched = transition(self.prepared, "DISPATCH_UNKNOWN", E)
        done = transition(dispatched, "QUALIFIED_READBACK", E)
        again = prepare(done, number=197, head=A, main=B, tree=C, policy=D, evidence=E)
        for i, record in enumerate((self.prepared, dispatched, done, again), 1):
            sha = f"{i:040x}"
            self.add(sha, prev, encode(record))
            prev = sha
            self.ref = sha
            if record == done:
                self.assertEqual(decode(pilot.read()[1]), done)
        with self.assertRaisesRegex(ValueError, "pilot already qualified"):
            pilot.read()
