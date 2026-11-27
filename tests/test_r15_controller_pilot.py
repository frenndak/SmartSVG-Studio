import unittest
import json
from datetime import datetime, timedelta
from hashlib import sha256
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
        from unittest.mock import patch
        with patch("tools.smartsvg_controller_pilot.recover",return_value={
                "journal_ref":G,"generation":2,"intent":1,
                "journal_state":"DISPATCH_UNKNOWN","action":"VERIFY_REQUEST_TERMINALITY",
                "merge_authorized":False,"retry_authorized":False}) as recovery:
            result=packet(lambda p:self.fail("no candidate reads"),route,journal=J())
            recovery.assert_called_once()
        self.assertEqual(result["recovery"]["action"],"VERIFY_REQUEST_TERMINALITY")
        self.assertEqual(result["status"],"RECOVERY_REQUIRED")
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["retry_authorized"])
        self.assertEqual(datetime.fromisoformat(result["observed_at"]).utcoffset(), timedelta(0))
        digest = result.pop("evidence_digest")
        canonical = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
        self.assertEqual(digest, sha256(canonical.encode()).hexdigest())

    def test_qualified_pilot_stops_before_candidate_reads(self):
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        done=transition(transition(prepared,"DISPATCH_UNKNOWN","e"*64),
                        "QUALIFIED_READBACK","d"*64)
        class J:
            def read(self):
                return G,encode(done)
        route={"main":M,"policy_blob":P,"run_id":1,"attempt":1,"controller_head":M,
               "assignments":{"B":{"number":2,"head":H,"action":"REVIEW"}}}
        result=packet(lambda p:self.fail("completed pilot must not read candidate"),route,journal=J())
        self.assertEqual(result["status"],"PILOT_COMPLETE")
        self.assertEqual(result["journal_state"],"QUALIFIED_READBACK")
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["retry_authorized"])
        digest=result.pop("evidence_digest")
        self.assertEqual(digest,sha256(json.dumps(result,sort_keys=True,separators=(",",":"),
                                                   allow_nan=False).encode()).hexdigest())

    def test_prepared_intent_needs_requalification_not_candidate(self):
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        class J:
            def read(self):
                return G,encode(prepared)
        route={"main":M,"policy_blob":P,"run_id":1,"attempt":1,"controller_head":M,
               "assignments":{"B":{"number":2,"head":H,"action":"REVIEW"}}}
        result=packet(lambda p:self.fail("prepared requires no candidate reads"),route,journal=J())
        self.assertEqual(result["status"],"RECOVERY_REQUIRED")
        self.assertEqual(result["recovery"]["action"],"REQUALIFY_PREPARED_INTENT")
        self.assertFalse(result["recovery"]["merge_authorized"])
        self.assertFalse(result["recovery"]["retry_authorized"])
        self.assertFalse(result["recovery"]["independent_work_blocked"])

    def test_recovery_mismatched_generation_discards_advice(self):
        from unittest.mock import patch
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        class J:
            def read(self):
                return G,encode(prepared)
        route={"main":M,"policy_blob":P,"run_id":1,"attempt":1,"controller_head":M,
               "assignments":{"B":None}}
        with patch("tools.smartsvg_controller_pilot.recover",return_value={
                "journal_ref":G,"generation":2,"intent":1,
                "journal_state":"DISPATCH_UNKNOWN","action":"OBSERVE_COMPLETED_INTEGRATION"}):
            result=packet(None,route,journal=J())
        self.assertEqual(result["status"],"CONTEXT_CHANGED")
        self.assertNotIn("recovery",result)
        self.assertFalse(result["merge_authorized"])

    def test_recovery_journal_changes_after_planner(self):
        from unittest.mock import patch
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        class J:
            def __init__(self):
                self.calls=0
            def read(self):
                self.calls+=1
                return (G if self.calls==1 else H),encode(prepared)
        route={"main":M,"policy_blob":P,"run_id":1,"attempt":1,"controller_head":M,
               "assignments":{"B":None}}
        with patch("tools.smartsvg_controller_pilot.recover",return_value={
                "journal_ref":G,"generation":1,"intent":1,"journal_state":"PREPARED",
                "action":"REQUALIFY_PREPARED_INTENT"}):
            result=packet(None,route,journal=J())
        self.assertEqual(result["status"],"CONTEXT_CHANGED")
        self.assertNotIn("recovery",result)
        self.assertFalse(result["retry_authorized"])


    def test_recovery_only_reads_pending_subject_not_open_queue(self):
        from tools.smartsvg_controller_pilot import recovery_only_packet
        from tools.smartsvg_controller_observation import POLICY
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        pending=transition(prepared,"DISPATCH_UNKNOWN","e"*64)
        class J:
            def read(self):
                return G,encode(pending)
        def get(path):
            if path=="/branches/main":
                return {"commit":{"sha":M}}
            if path==f"/contents/{POLICY}?ref={M}":
                return {"sha":P}
            if path=="/pulls/1":
                repo={"full_name":"frenndak/SmartSVG-Studio"}
                return {"number":1,"head":{"sha":H,"repo":repo},
                        "base":{"ref":"main","repo":repo},"user":{"login":"frenndak"},
                        "state":"open","merged":False,"merge_commit_sha":None}
            self.fail("unexpected candidate or queue read: "+path)
        result=recovery_only_packet(get,run_id=1,attempt=1,controller_head=M,journal=J())
        self.assertEqual(result["qualification"],"FAILED_ROUTE_DIAGNOSTIC_ONLY")
        self.assertEqual(result["recovery"]["action"],"VERIFY_REQUEST_TERMINALITY")
        self.assertEqual(result["recovery"]["observation"]["state"],"NEGATIVE_READBACK")
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["retry_authorized"])
        digest=result.pop("evidence_digest")
        self.assertEqual(digest,sha256(json.dumps(result,sort_keys=True,separators=(",",":"),
                                                 allow_nan=False).encode()).hexdigest())

    def test_recovery_only_idle_or_stale_controller_emits_nothing(self):
        from tools.smartsvg_controller_pilot import recovery_only_packet
        class J:
            def read(self):
                return G,encode(Record())
        def get(path):
            return {"commit":{"sha":M}} if path=="/branches/main" else {"sha":P}
        self.assertIsNone(recovery_only_packet(get,run_id=1,attempt=1,controller_head=M,journal=J()))
        self.assertIsNone(recovery_only_packet(get,run_id=1,attempt=1,controller_head=H,journal=J()))

    def test_recovery_only_drops_diagnostic_on_main_drift(self):
        from tools.smartsvg_controller_pilot import recovery_only_packet
        prepared=prepare(Record(),number=1,head=H,main=M,tree=T,policy=P,evidence="f"*64)
        class J:
            def read(self):
                return G,encode(prepared)
        reads=0
        def get(path):
            nonlocal reads
            if path=="/branches/main":
                reads+=1
                return {"commit":{"sha":M if reads==1 else H}}
            return {"sha":P}
        self.assertIsNone(recovery_only_packet(get,run_id=1,attempt=1,controller_head=M,journal=J()))
