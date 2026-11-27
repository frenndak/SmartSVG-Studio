from contextlib import closing
from dataclasses import replace
import unittest
from unittest.mock import Mock

from tools.smartsvg_controller_mission_transport import (
    StoredSnapshot, sync_mission_snapshot, sync_independent_missions, IndependentSync,
)
from tools.smartsvg_controller_missions import MissionJournal
from tools.smartsvg_controller_objectives import Objective, Profile


MAIN, POLICY, ROADMAP, REVISION = (c * 40 for c in "abcd")
PROFILE = Profile("smartsvg", "frenndak/SmartSVG-Studio", "main", POLICY, ROADMAP)
A = Objective("mission-a", REVISION, "A", ("proof-a",))
B = Objective("mission-b", REVISION, "B", ("proof-b",))


def snapshot(*objectives, advance=None):
    with closing(MissionJournal(":memory:")) as journal:
        for objective in objectives:
            first = journal.create(PROFILE, objective, MAIN)
            if advance and objective == A:
                journal.advance(
                    PROFILE, A.key, expected_generation=first.generation,
                    expected_digest=first.digest, main=MAIN, revision=REVISION, role="A",
                    state="ACTIVE", next_action=advance, evidence="e"*64)
        return journal.export_snapshot(PROFILE)


class PrivateMissionTransportTests(unittest.TestCase):
    def test_conditional_write_combines_independent_histories(self):
        current = StoredSnapshot(12, snapshot(A))
        expected = snapshot(A, B)
        read = Mock(side_effect=(current, StoredSnapshot(13, expected)))
        write = Mock(return_value=True)
        self.assertEqual(sync_mission_snapshot(PROFILE, snapshot(B), read=read, replace=write),
                         "WRITE_VERIFIED")
        write.assert_called_once_with(12, expected)
        self.assertEqual(read.call_count, 2)

    def test_stale_local_prefix_preserves_remote_advance_without_write(self):
        read = Mock(return_value=StoredSnapshot("v3", snapshot(A, advance="RUN_TEST")))
        write = Mock()
        self.assertEqual(sync_mission_snapshot(PROFILE, snapshot(A), read=read, replace=write),
                         "ALREADY_CURRENT")
        write.assert_not_called()

    def test_incompatible_mission_histories_are_not_published(self):
        read = Mock(return_value=StoredSnapshot(12, snapshot(A, advance="REPAIR")))
        write = Mock()
        result = sync_mission_snapshot(
            PROFILE, snapshot(A, advance="VERIFY"), read=read, replace=write)
        self.assertEqual(result, "HISTORY_REJECTED")
        write.assert_not_called()

    def test_concurrent_version_change_does_not_retry_write(self):
        read = Mock(return_value=StoredSnapshot(12, snapshot(A)))
        write = Mock(return_value=False)
        self.assertEqual(sync_mission_snapshot(PROFILE, snapshot(B), read=read, replace=write),
                         "VERSION_CONFLICT")
        write.assert_called_once()
        read.assert_called_once()

    def test_lost_write_acknowledgement_is_reconciled_without_repeat_write(self):
        original = StoredSnapshot(12, snapshot(A))
        intended = StoredSnapshot(13, snapshot(A, B))
        for observed, expected in ((intended, "WRITE_VERIFIED"),
                                   (original, "WRITE_UNCONFIRMED"),
                                   (OSError("private path"), "WRITE_UNCONFIRMED")):
            with self.subTest(expected=expected):
                read = Mock(side_effect=(original, observed))
                write = Mock(side_effect=OSError("private payload"))
                self.assertEqual(sync_mission_snapshot(PROFILE, snapshot(B), read=read,
                                                       replace=write), expected)
                write.assert_called_once_with(12, intended.payload)
                self.assertEqual(read.call_count, 2)

    def test_other_profile_snapshot_is_refused_before_store_access(self):
        read = Mock()
        write = Mock()
        result = sync_mission_snapshot(
            replace(PROFILE, project="other"), snapshot(A), read=read, replace=write)
        self.assertEqual(result, "SNAPSHOT_INVALID")
        read.assert_not_called()
        write.assert_not_called()


class IndependentMissionTransportTests(unittest.TestCase):
    def test_conflict_isolated_and_independent_history_saved(self):
        current = StoredSnapshot(12, snapshot(A, advance="REPAIR"))
        expected = snapshot(A, B, advance="REPAIR")
        read = Mock(side_effect=(current, StoredSnapshot(13, expected)))
        write = Mock(return_value=True)
        result = sync_independent_missions(
            PROFILE, snapshot(A, B, advance="VERIFY"), read=read, replace=write)
        self.assertEqual(result, IndependentSync("WRITE_VERIFIED", (A.key,)))
        write.assert_called_once_with(12, expected)

    def test_only_conflict_never_writes_or_claims_resolution(self):
        read = Mock(return_value=StoredSnapshot(12, snapshot(A, advance="REPAIR")))
        write = Mock()
        result = sync_independent_missions(
            PROFILE, snapshot(A, advance="VERIFY"), read=read, replace=write)
        self.assertEqual(result, IndependentSync("ALREADY_CURRENT", (A.key,)))
        write.assert_not_called()

    def test_version_conflict_preserves_conflict_report_without_retry(self):
        read = Mock(return_value=StoredSnapshot(12, snapshot(A, advance="REPAIR")))
        write = Mock(return_value=False)
        result = sync_independent_missions(
            PROFILE, snapshot(A, B, advance="VERIFY"), read=read, replace=write)
        self.assertEqual(result, IndependentSync("VERSION_CONFLICT", (A.key,)))
        write.assert_called_once()
        read.assert_called_once()

    def test_invalid_remote_is_not_partially_salvaged(self):
        read = Mock(return_value=StoredSnapshot(12, b"{}"))
        write = Mock()
        result = sync_independent_missions(
            PROFILE, snapshot(B), read=read, replace=write)
        self.assertEqual(result, IndependentSync("HISTORY_REJECTED"))
        write.assert_not_called()

    def test_wrong_profile_refused_before_store_access(self):
        read = Mock()
        write = Mock()
        result = sync_independent_missions(
            replace(PROFILE, project="other"), snapshot(B), read=read, replace=write)
        self.assertEqual(result, IndependentSync("SNAPSHOT_INVALID"))
        read.assert_not_called()
        write.assert_not_called()

    def test_uncertain_ack_reconciled_once_with_conflict_report(self):
        current = StoredSnapshot(12, snapshot(A, advance="REPAIR"))
        expected = snapshot(A, B, advance="REPAIR")
        read = Mock(side_effect=(current, StoredSnapshot(13, expected)))
        write = Mock(side_effect=OSError("lost acknowledgement"))
        result = sync_independent_missions(
            PROFILE, snapshot(A, B, advance="VERIFY"), read=read, replace=write)
        self.assertEqual(result, IndependentSync("WRITE_VERIFIED", (A.key,)))
        write.assert_called_once_with(12, expected)
        self.assertEqual(read.call_count, 2)
