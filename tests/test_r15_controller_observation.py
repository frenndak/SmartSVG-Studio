import unittest
from tools.smartsvg_controller_observation import ObservationError, observe, pages

M, H, P = "a" * 40, "b" * 40, "c" * 40


def fixture(path):
    if path == "/branches/main":
        return {"commit": {"sha": M}, "protected": False}
    if path.startswith("/contents/"):
        return {"sha": P}
    pr = {"id": 1, "number": 195, "state": "open", "head": {"sha": H}}
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
