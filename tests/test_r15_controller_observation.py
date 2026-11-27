import unittest
from tools.smartsvg_controller_observation import ObservationError, observe, pages

M, H, P = "a" * 40, "b" * 40, "c" * 40


def fixture(path):
    if path == "/branches/main":
        return {"commit": {"sha": M}, "protected": False}
    if path.startswith("/contents/"):
        return {"sha": P}
    pr = {"id": 1, "number": 195, "state": "open",
          "head": {"sha": H, "ref": "a/test", "repo": {"full_name": "frenndak/SmartSVG-Studio"}}}
    if path == "/git/ref/heads/a/test":
        return {"ref": "refs/heads/a/test", "object": {"sha": H, "type": "commit"}}
    if path.startswith("/pulls?state=open"):
        return [pr]
    if path == "/pulls/195":
        return pr
    if path.startswith("/actions/runs?"):
        return {"total_count": 0, "workflow_runs": []}
    if path.startswith(("/pulls/195/reviews?", "/issues/195/comments?", "/rulesets?")):
        return []
    raise AssertionError(path)


class ObservationTests(unittest.TestCase):
    def test_raw_only_no_inferred_approval(self):
        result = observe(fixture)
        self.assertEqual(result["policy_blob"], P)
        self.assertEqual(result["candidates"][0]["pr"]["head"]["sha"], H)
        self.assertEqual(result["qualification"], "RAW_ONLY")
        self.assertFalse(result["authority_verified"])
        self.assertFalse(result["scheduler_verified"])
        self.assertFalse(result["threads_verified"])

    def test_pagination_and_count(self):
        def get(path):
            rows = range(100) if path.endswith("page=1") else range(100, 101)
            return {"total_count": 101, "jobs": [{"id": x} for x in rows]}
        self.assertEqual(len(pages(get, "/jobs", "jobs")), 101)

    def test_duplicate_and_incomplete_fail_closed(self):
        with self.assertRaises(ObservationError):
            pages(lambda p: [{"id": 1}, {"id": 1}], "/pulls")
        with self.assertRaises(ObservationError):
            pages(lambda p: {"total_count": 2, "jobs": [{"id": 1}]}, "/jobs", "jobs")
        with self.assertRaises(ObservationError):
            pages(lambda p: [{"id": i} for i in range(100)], "/pulls", limit=1)

    def test_changed_main_rejected(self):
        count = 0
        def get(path):
            nonlocal count
            if path == "/branches/main":
                count += 1
                if count == 2:
                    return {"commit": {"sha": H}}
            return fixture(path)
        with self.assertRaises(ObservationError):
            observe(get)

    def test_wrong_run_sha_rejected(self):
        def get(path):
            if path.startswith("/actions/runs?"):
                return {"total_count": 1, "workflow_runs": [{"id": 2, "head_sha": H, "event": "push"}]}
            return fixture(path)
        with self.assertRaises(ObservationError):
            observe(get)

    def test_failed_read_not_empty_success(self):
        def get(path):
            if path.startswith("/rulesets?"):
                raise PermissionError("rulesets unavailable")
            return fixture(path)
        with self.assertRaises(PermissionError):
            observe(get)

    def test_stale_pr_projection_quarantined(self):
        def get(path):
            if path == "/git/ref/heads/a/test":
                return {"ref": "refs/heads/a/test", "object": {"sha": M, "type": "commit"}}
            if path.startswith("/actions/runs?head_sha=" + H):
                self.fail("stale PR must not collect CI as current")
            return fixture(path)
        row = observe(get)["candidates"][0]
        self.assertEqual(row["branch"], {"status": "DIVERGED", "sha": M})
        self.assertEqual(row["runs"], [])

    def test_branch_moves_during_collection(self):
        count = 0
        def get(path):
            nonlocal count
            if path == "/git/ref/heads/a/test":
                count += 1
                return {"ref": "refs/heads/a/test",
                        "object": {"sha": H if count == 1 else M, "type": "commit"}}
            return fixture(path)
        row = observe(get)["candidates"][0]
        self.assertEqual(row["branch"]["status"], "DIVERGED")
        self.assertEqual(row["comments"], [])

    def test_unavailable_branch_is_not_positive_evidence(self):
        def get(path):
            if path == "/git/ref/heads/a/test":
                raise PermissionError("unavailable")
            return fixture(path)
        row = observe(get)["candidates"][0]
        self.assertEqual(row["branch"]["status"], "UNAVAILABLE")
        self.assertEqual(row["branch"]["error"], "PermissionError")


class QueueChurnTests(unittest.TestCase):
    def test_queue_change_has_distinct_retryable_type(self):
        from tools.smartsvg_controller_observation import QueueChanged
        count=0
        def get(path):
            nonlocal count
            if path.startswith("/pulls?state=open"):
                count+=1
                if count==2:
                    return []
            return fixture(path)
        with self.assertRaises(QueueChanged):
            observe(get)

    def test_main_change_not_retryable_queue_churn(self):
        from tools.smartsvg_controller_observation import QueueChanged
        count=0
        def get(path):
            nonlocal count
            if path=="/branches/main":
                count+=1
                if count==3:
                    return {"commit":{"sha":H}}
            return fixture(path)
        with self.assertRaises(ObservationError) as error:
            observe(get)
        self.assertNotIsInstance(error.exception,QueueChanged)


class ReadRetryTests(unittest.TestCase):
    def test_transient_get_retries_once(self):
        from unittest.mock import patch, MagicMock
        from http.client import RemoteDisconnected
        from tools.smartsvg_controller_observation import github_get
        response=MagicMock()
        response.__enter__.return_value.read.return_value=b'{"ok":true}'
        with patch("tools.smartsvg_controller_observation.build_opener") as opener, patch("tools.smartsvg_controller_observation.time.sleep") as sleep:
            opener.return_value.open.side_effect=[RemoteDisconnected("temporary"),response]
            self.assertEqual(github_get("/branches/main"),{"ok":True})
            self.assertEqual(opener.return_value.open.call_count,2)
            sleep.assert_called_once_with(0.25)

    def test_permanent_transport_error_bounded(self):
        from unittest.mock import patch
        from tools.smartsvg_controller_observation import github_get
        with patch("tools.smartsvg_controller_observation.build_opener") as opener, patch("tools.smartsvg_controller_observation.time.sleep"):
            opener.return_value.open.side_effect=TimeoutError()
            with self.assertRaises(TimeoutError):
                github_get("/branches/main")
            self.assertEqual(opener.return_value.open.call_count,2)

    def test_no_retry_permission_rate_limit_or_invalid_json(self):
        from unittest.mock import patch, MagicMock
        from urllib.error import HTTPError
        from tools.smartsvg_controller_observation import github_get
        for code in (403,404,429):
            with patch("tools.smartsvg_controller_observation.build_opener") as opener:
                opener.return_value.open.side_effect=HTTPError("https://example.invalid",code,"denied",{},None)
                with self.assertRaises(HTTPError):
                    github_get("/branches/main")
                self.assertEqual(opener.return_value.open.call_count,1)
        response=MagicMock()
        response.__enter__.return_value.read.return_value=b'not-json'
        with patch("tools.smartsvg_controller_observation.build_opener") as opener:
            opener.return_value.open.return_value=response
            with self.assertRaises(ValueError):
                github_get("/branches/main")
            self.assertEqual(opener.return_value.open.call_count,1)


class CandidateIsolationTests(unittest.TestCase):
    def setUp(self):
        self.head2="d"*40
        repo={"full_name":"frenndak/SmartSVG-Studio"}
        self.prs=[dict(id=i,number=n,state="open",draft=False,mergeable=True,
                       head=dict(sha=h,ref=ref,repo=repo),
                       base=dict(ref="main",repo=repo),user=dict(login="frenndak"))
                  for i,n,h,ref in ((1,195,H,"a/test"),(2,196,self.head2,"b/test"))]
        self.bad=None

    def get(self,path):
        if self.bad and path.startswith(self.bad):
            raise PermissionError("private transport details")
        if path.startswith("/pulls?state=open"):
            return self.prs
        for p in self.prs:
            if path==f"/pulls/{p['number']}":
                return p
            if path=="/git/ref/heads/"+p["head"]["ref"]:
                return {"ref":"refs/heads/"+p["head"]["ref"],
                        "object":{"type":"commit","sha":p["head"]["sha"]}}
            if path.startswith((f"/pulls/{p['number']}/reviews?",
                                f"/issues/{p['number']}/comments?")):
                return []
        return fixture(path)

    def test_candidate_read_failure_preserves_other_pr_and_conservative_wip(self):
        from tools.smartsvg_controller_orchestration import Scope, build_plan
        for endpoint in ("/pulls/195", "/actions/runs?head_sha="+H,
                         "/issues/195/comments?", "/pulls/195/reviews?"):
            self.bad=endpoint
            snapshot=observe(self.get)
            first,second=snapshot["candidates"]
            self.assertEqual(first["collection_error"],"PermissionError")
            for key in ("runs","reviews","comments"):
                self.assertEqual(first[key],[])
            self.assertNotIn("collection_error",second)
            self.assertNotIn("private transport details",str(snapshot))
            plan=build_plan(snapshot,(Scope(195,H,"A",True),
                                      Scope(196,self.head2,"B",True)))
            self.assertEqual(plan.unknown,(195,))
            self.assertEqual(plan.code_wip,2)
            self.assertFalse(plan.queue_complete)
            self.assertEqual(tuple(p.number for p in plan.proposals),(196,))

    def test_global_reads_still_fail_closed(self):
        for endpoint in ("/branches/main","/rulesets?",
                         "/actions/runs?head_sha="+M,"/pulls?state=open"):
            self.bad=endpoint
            with self.assertRaises(PermissionError):
                observe(self.get)

    def test_invalid_candidate_job_provenance_is_quarantined(self):
        def get(path):
            if path.startswith("/actions/runs?head_sha="+H):
                return {"total_count":1,"workflow_runs":[
                    {"id":20,"head_sha":self.head2,"event":"pull_request",
                     "run_attempt":1}]}
            return self.get(path)
        snapshot=observe(get)
        self.assertEqual(snapshot["candidates"][0]["collection_error"],"ObservationError")
        self.assertNotIn("collection_error",snapshot["candidates"][1])


    def test_malformed_detail_or_exhausted_body_read_is_candidate_local(self):
        from http.client import IncompleteRead
        for malformed in (None, {}, {"number":195,"state":"open","head":None}):
            def get(path):
                return malformed if path=="/pulls/195" else self.get(path)
            rows=observe(get)["candidates"]
            self.assertIn("collection_error",rows[0])
            self.assertNotIn("collection_error",rows[1])
        def partial_body(path):
            if path.startswith("/issues/195/comments?"):
                raise IncompleteRead(b"partial")
            return self.get(path)
        rows=observe(partial_body)["candidates"]
        self.assertEqual(rows[0]["collection_error"],"IncompleteRead")
        self.assertEqual(rows[0]["comments"],[])
        self.assertNotIn("collection_error",rows[1])

    def test_valid_but_changed_detail_still_restarts_queue(self):
        from tools.smartsvg_controller_observation import QueueChanged
        def get(path):
            if path=="/pulls/195":
                return dict(self.prs[0],state="closed")
            return self.get(path)
        with self.assertRaises(QueueChanged):
            observe(get)


    def test_malformed_step_payload_does_not_escape_candidate_isolation(self):
        from tools.smartsvg_controller_evidence import SPECS
        workflow, job_name, _ = SPECS["g0"]
        def get(path):
            if path.startswith("/actions/runs?head_sha="+H):
                return {"total_count":1,"workflow_runs":[{"id":20,
                    "head_sha":H,"event":"pull_request","run_attempt":1,
                    "path":workflow,"status":"completed","conclusion":"success"}]}
            if path.startswith("/actions/runs/20/attempts/1/jobs?"):
                return {"total_count":1,"jobs":[{"id":21,"run_id":20,
                    "head_sha":H,"run_attempt":1,"name":job_name,
                    "status":"completed","conclusion":"success","steps":None}]}
            return self.get(path)
        snapshot=observe(get)
        self.assertEqual(snapshot["candidates"][0]["collection_error"],"TypeError")
        self.assertNotIn("collection_error",snapshot["candidates"][1])

    def test_manifest_ignores_quarantined_incomplete_projection(self):
        from tools.smartsvg_controller_commission import manifests
        from tools.smartsvg_controller_orchestration import Scope, build_plan
        self.bad="/pulls/195"
        snapshot=observe(self.get)
        snapshot["candidates"][0]["pr"]=dict(self.prs[0],user=None)
        scopes,_=manifests(snapshot)
        self.assertEqual([s["number"] for s in scopes["scopes"]],[196])
        plan=build_plan(snapshot,tuple(Scope(**s) for s in scopes["scopes"]))
        self.assertEqual(plan.unknown,(195,))
        self.assertEqual(plan.code_wip,2)


    def test_nested_malformed_base_repo_never_escapes_manifest(self):
        from tools.smartsvg_controller_commission import manifests
        from tools.smartsvg_controller_orchestration import Scope, build_plan
        def get(path):
            if path=="/pulls/195":
                return dict(self.prs[0],base={"ref":"main","repo":"malformed"})
            return self.get(path)
        snapshot=observe(get)
        self.assertEqual(snapshot["candidates"][0]["collection_error"],"ObservationError")
        scopes,_=manifests(snapshot)
        plan=build_plan(snapshot,tuple(Scope(**s) for s in scopes["scopes"]))
        self.assertEqual(plan.unknown,(195,))
        self.assertEqual(plan.code_wip,2)
        self.assertEqual(tuple(p.number for p in plan.proposals),(196,))

    def test_unreadable_queue_head_preserves_other_assignment_through_live_route(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from tools.smartsvg_controller_runtime import route

        for broken_reads in ({1}, {2}, {1, 2, 3}):
            with self.subTest(broken_reads=broken_reads), TemporaryDirectory() as tmp:
                queue_reads = 0

                def get(path):
                    nonlocal queue_reads
                    if path.startswith("/pulls?state=open"):
                        queue_reads += 1
                        if queue_reads in broken_reads:
                            return [dict(self.prs[0], head=None), self.prs[1]]
                    if path in ("/pulls/195", "/pulls/196"):
                        pr = self.get(path)
                        return dict(pr, base=dict(pr["base"], sha=M), changed_files=1)
                    if "/files?" in path:
                        return [{"filename": "tests/test_example.py",
                                 "status": "modified", "sha": P}]
                    return self.get(path)

                result = route(get, Path(tmp) / "routing.db", run_id=1, attempt=1,
                               controller_head=M, require_main=True)
                self.assertEqual(result["unknown"], [195])
                self.assertEqual(result["code_wip"], 2)
                self.assertFalse(result["queue_complete"])
                self.assertEqual(result["development_advice"]["available_slots"], 0)
                self.assertEqual(result["assignments"]["A"]["number"], 196)
                self.assertIsNone(result["assignments"]["B"])
                self.assertFalse(result["merge_authorized"])
                self.assertFalse(result["observation_restarted"])

    def test_invalid_queue_numbers_refuse_whole_observation(self):
        for number in (None, False, 0, -1, "195", 196):
            with self.subTest(number=number):
                def get(path):
                    if path.startswith("/pulls?state=open"):
                        return [dict(self.prs[0], number=number), self.prs[1]]
                    return self.get(path)
                with self.assertRaises(ObservationError):
                    observe(get)

    def test_valid_queue_head_change_keeps_bounded_restart(self):
        from tools.smartsvg_controller_observation import QueueChanged
        count = 0

        def get(path):
            nonlocal count
            if path.startswith("/pulls?state=open"):
                count += 1
                if count == 2:
                    old = self.prs[0]
                    return [dict(old, head=dict(old["head"], sha=P)), self.prs[1]]
            return self.get(path)

        with self.assertRaises(QueueChanged):
            observe(get)

    def test_repeated_head_churn_preserves_other_assignment(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from tools.smartsvg_controller_runtime import route

        old = self.prs[0]
        updated = dict(old, head=dict(old["head"], sha=P))
        for phase in ("detail", "final_queue"):
            with self.subTest(phase=phase), TemporaryDirectory() as tmp:
                queue_reads = 0

                def get(path):
                    nonlocal queue_reads
                    if path.startswith("/pulls?state=open"):
                        queue_reads += 1
                        if phase == "final_queue" and queue_reads in (2, 4):
                            return [updated, self.prs[1]]
                    if path in ("/pulls/195", "/pulls/196"):
                        pr = updated if path == "/pulls/195" and phase == "detail" else self.get(path)
                        return dict(pr, base=dict(pr["base"], sha=M), changed_files=1)
                    if "/files?" in path:
                        self.assertNotIn("/pulls/195/", path)
                        return [{"filename": "tests/test_example.py",
                                 "status": "modified", "sha": P}]
                    return self.get(path)

                result = route(get, Path(tmp) / "routing.db", run_id=1, attempt=1,
                               controller_head=M, require_main=True)
                self.assertTrue(result["observation_restarted"])
                self.assertEqual(result["unknown"], [195])
                self.assertEqual(result["candidate_failures"],
                                 [{"number": 195, "reason": "HEAD_CHANGED_DURING_READ"}])
                self.assertEqual(result["code_wip"], 2)
                self.assertFalse(result["queue_complete"])
                self.assertEqual(result["development_advice"]["available_slots"], 0)
                self.assertEqual(result["assignments"]["A"]["number"], 196)
                self.assertIsNone(result["assignments"]["B"])
                self.assertFalse(result["merge_authorized"])

    def test_retry_still_refuses_queue_membership_change(self):
        from tools.smartsvg_controller_observation import QueueChanged

        def get(path):
            if path == "/pulls/195":
                return dict(self.prs[0], state="closed")
            return self.get(path)

        with self.assertRaises(QueueChanged):
            observe(get, isolate_head_churn=True)
