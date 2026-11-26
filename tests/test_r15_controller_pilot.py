import unittest
from tools.smartsvg_controller_pilot import predicted_tree, packet
from tools.smartsvg_controller_git_journal import PilotJournalTransport, JournalTransport
from tools.smartsvg_controller_cas import Record, encode, prepare, transition

M,H,T,P,G=(x*40 for x in "abcde")

class PilotTests(unittest.TestCase):
    def test_pins_are_distinct(self):
        self.assertNotEqual(PilotJournalTransport.branch,JournalTransport.branch)
        self.assertEqual(PilotJournalTransport.branch,"r15b/integration-journal-v1")
        self.assertEqual(PilotJournalTransport.genesis,"3ae1078e65c7fa8052042fe65852c50720ae93e0")
        self.assertNotEqual(PilotJournalTransport.genesis,JournalTransport.genesis)

    def test_tree_from_proven_ancestor(self):
        def get(path):
            if path.startswith("/compare/"):
                return {"status":"ahead","base_commit":{"sha":M},"merge_base_commit":{"sha":M},
                        "behind_by":0,"ahead_by":2}
            return {"sha":H,"tree":{"sha":T}}
        self.assertEqual(predicted_tree(get,1,H,M),T)

    def test_exact_preview_parents(self):
        def get(path):
            if path.startswith("/compare/"):
                return {"status":"diverged"}
            if path.startswith("/git/ref/"):
                return {"ref":"refs/pull/1/merge","object":{"type":"commit","sha":G}}
            return {"sha":G,"parents":[{"sha":M},{"sha":H}],"tree":{"sha":T}}
        self.assertEqual(predicted_tree(get,1,H,M),T)
        def wrong(path):
            r=get(path)
            if path.startswith("/git/commits/"):
                r["parents"].reverse()
            return r
        self.assertIsNone(predicted_tree(wrong,1,H,M))

    def test_unavailable_tree_is_not_guessed(self):
        def get(path):
            raise OSError()
        self.assertIsNone(predicted_tree(get,1,H,M))

    def test_unresolved_journal_precedes_candidate_and_never_authorizes(self):
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        class J:
            def read(self):
                return G,encode(transition(prepared,"DISPATCH_UNKNOWN","e"*64))
        route={"main":M,"policy_blob":P,"run_id":1,"attempt":1,"controller_head":M,
               "assignments":{"B":{"number":1,"head":H,"action":"REVIEW"}}}
        result=packet(lambda p:self.fail("no candidate reads"),route,journal=J())
        self.assertEqual(result["status"],"RECOVERY_REQUIRED")
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["retry_authorized"])
