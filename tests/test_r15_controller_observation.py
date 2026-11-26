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
