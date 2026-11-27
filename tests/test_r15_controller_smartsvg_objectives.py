from contextlib import redirect_stdout
from io import StringIO
import json
import unittest
from pathlib import Path
from sqlite3 import OperationalError
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from dataclasses import replace
from hashlib import sha256
from tools.smartsvg_controller_mission_cli import MAX_REVISION_BYTES, main as mission_cli
from tools.smartsvg_controller_missions import MissionJournal
from tools.smartsvg_controller_objectives import Profile, Receipt, plan_objectives
from tools.smartsvg_controller_smartsvg_objectives import (
    REPOSITORY, POLICY_PATH, POLICY_PIN, BACKLOG_PATH, SOURCE_PINS, SLICES,
    observe_smartsvg_mission_resumption, observe_smartsvg_objectives,
)

M = "a"*40
P = Profile("smartsvg",REPOSITORY,"main",POLICY_PIN,dict(SOURCE_PINS)[BACKLOG_PATH])
REVISIONS = {row[0]: M for row in SLICES}


def source(path):
    if path == "/branches/main":
        return {"commit":{"sha":M}}
    for name,pin in ((POLICY_PATH,POLICY_PIN),*SOURCE_PINS):
        if path == f"/contents/{name}?ref={M}":
            return {"sha":pin}
    raise AssertionError(path)


def rows(result):
    return {o.key:o for o in result.objectives}


def pass_receipts(o):
    return tuple(Receipt(P,M,o.key,o.revision,c,"PASS",True,
                         sha256((o.key+":"+c).encode()).hexdigest()) for c in o.criteria)


class SmartSVGObjectiveAdapterTests(unittest.TestCase):
    def observe(self, revisions=REVISIONS, get=source, profile=P):
        return observe_smartsvg_objectives(get,profile,M,revisions)

    def test_exact_pins_and_partial_graph_not_authority(self):
        r=self.observe()
        self.assertEqual(r.status,"OBSERVED_PARTIAL_GRAPH")
        self.assertEqual(len(r.objectives),len(SLICES))
        self.assertEqual(r.missing_revisions,())
        self.assertIn("CAL-CUT",r.unmapped)
        self.assertIn("W15-release",r.unmapped)
        self.assertFalse(r.merge_authorized)
        self.assertFalse(r.agent_work_executed)
        plan=plan_objectives(P,M,r.objectives)
        self.assertFalse(any(a.action=="BLOCKED_GRAPH" for a in plan.objectives))
        self.assertFalse(any(a.action=="CRITERIA_OBSERVED" for a in plan.objectives))

    def test_sd0_a_independent_and_sd1_only_one_export_proof(self):
        o=rows(self.observe())
        self.assertEqual(o["W05-SD0-A"].dependencies,())
        self.assertIn("W03-ONE-TYPED-EXPORT",o["W06-SD1-A"].dependencies)
        self.assertNotIn("W03-BASIC-CUT-BACKEND",o["W06-SD1-A"].dependencies)
        self.assertNotIn("W03-PTC-BACKEND",o["W06-SD1-A"].dependencies)
        self.assertNotIn("W03-ONE-TYPED-EXPORT",o["W08-PTC-ASSISTANT"].dependencies)
        self.assertEqual(o["W08-PTC-ASSISTANT"].dependencies,("W03-PTC-BACKEND",))

    def test_one_export_is_explicit_receipt_not_automatically_inferred(self):
        o=rows(self.observe())
        proof=pass_receipts(o["W01-V1-CORE"])+pass_receipts(o["W03-BASIC-CUT-BACKEND"])
        plan=plan_objectives(P,M,tuple(o.values()),proof)
        actions={a.objective:a.action for a in plan.objectives}
        self.assertEqual(actions["W03-BASIC-CUT-BACKEND"],"CRITERIA_OBSERVED")
        self.assertEqual(actions["W03-ONE-TYPED-EXPORT"],"VERIFY_CRITERION")
        self.assertEqual(actions["W06-SD1-A"],"WAIT_DEPENDENCY")
        proof+=pass_receipts(o["W03-ONE-TYPED-EXPORT"])
        plan=plan_objectives(P,M,tuple(o.values()),proof)
        actions={a.objective:a.action for a in plan.objectives}
        self.assertEqual(actions["W03-ONE-TYPED-EXPORT"],"CRITERIA_OBSERVED")
        self.assertEqual(actions["W08-PTC-ASSISTANT"],"WAIT_DEPENDENCY")

    def test_missing_revision_blocks_only_affected_nodes(self):
        r=self.observe({k:v for k,v in REVISIONS.items() if k!="W01-V1-CORE"})
        self.assertEqual(r.missing_revisions,("W01-V1-CORE",))
        plan=plan_objectives(P,M,r.objectives)
        actions={a.objective:a.action for a in plan.objectives}
        self.assertEqual(actions["W02-MANUAL-SUBJECT"],"BLOCKED_GRAPH")
        self.assertEqual(actions["W05-SD0-A"],"VERIFY_CRITERION")
        self.assertEqual(actions["W13-ACCESSIBILITY"],"VERIFY_CRITERION")

    def test_source_or_policy_change_disables_only_optional_adapter(self):
        for name,_ in ((POLICY_PATH,POLICY_PIN),*SOURCE_PINS):
            def changed(path):
                if path==f"/contents/{name}?ref={M}":
                    return {"sha":"b"*40}
                return source(path)
            result=self.observe(get=changed)
            self.assertEqual(result.status,"SOURCE_REVIEW_REQUIRED")
            self.assertEqual(result.objectives,())
        self.assertEqual(self.observe(profile=replace(P,policy_blob="b"*40)).status,
                         "SOURCE_REVIEW_REQUIRED")

    def test_main_drift_or_optional_transport_failure_never_produces_graph(self):
        calls=0
        def drift(path):
            nonlocal calls
            if path=="/branches/main":
                calls+=1
                if calls==2:
                    return {"commit":{"sha":"b"*40}}
            return source(path)
        self.assertEqual(self.observe(get=drift).status,"CONTEXT_CHANGED")
        def failed(path):
            raise OSError("private response")
        r=self.observe(get=failed)
        self.assertEqual(r.status,"UNAVAILABLE")
        self.assertEqual(r.objectives,())
        self.assertNotIn("private response",str(r))

    def test_wrong_project_and_unrecognized_revision_refused(self):
        r=self.observe(profile=replace(P,project="synthetic"))
        self.assertEqual(r.status,"PROFILE_MISMATCH")
        self.assertEqual(self.observe({**REVISIONS,"invented":M}).status,
                         "REVISION_INPUT_INVALID")
        self.assertEqual(self.observe({"W01-V1-CORE":"not-sha"}).status,
                         "REVISION_INPUT_INVALID")


    def test_resumption_uses_reviewed_graph_and_continues_independent_work(self):
        revisions = {key: M for key in ("W01-V1-CORE", "W05-SD0-A",
                                         "W03-BASIC-CUT-BACKEND")}
        objectives = rows(self.observe(revisions))
        core = objectives["W01-V1-CORE"]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "missions.sqlite"
            journal = MissionJournal(path)
            try:
                checkpoint = journal.create(P, core, M)
                waiting = journal.advance(
                    P, core.key, expected_generation=checkpoint.generation,
                    expected_digest=checkpoint.digest, main=M, revision=M, role="B",
                    state="WAITING", next_action="VERIFY_CRITERION", evidence="b"*64)
            finally:
                journal.close()
            reopened = MissionJournal(path)
            try:
                result = observe_smartsvg_mission_resumption(
                    source, reopened, P, M, revisions, role="B")
                self.assertEqual(reopened.latest(P, core.key), waiting)
            finally:
                reopened.close()
        self.assertEqual(result.status, "OBSERVED_PARTIAL_GRAPH")
        self.assertFalse(result.merge_authorized)
        self.assertFalse(result.agent_work_executed)
        missions = {m.objective.objective: m for m in result.mission_plan.missions}
        self.assertEqual(missions[core.key].checkpoint_status, "WAITING")
        self.assertEqual(missions["W03-BASIC-CUT-BACKEND"].objective.action,
                         "WAIT_DEPENDENCY")
        self.assertEqual(result.mission_plan.selected.objective.objective, "W05-SD0-A")

    def test_resumption_drops_advice_when_main_moves_during_checkpoint_read(self):
        journal = Mock()
        journal.latest.return_value = None
        main_reads = 0

        def get(path):
            nonlocal main_reads
            if path == "/branches/main":
                main_reads += 1
                if main_reads == 3:
                    return {"commit": {"sha": "b"*40}}
            return source(path)

        result = observe_smartsvg_mission_resumption(
            get, journal, P, M, {"W01-V1-CORE": M}, role="B")
        journal.latest.assert_called_once_with(P, "W01-V1-CORE")
        self.assertEqual(result.status, "CONTEXT_CHANGED")
        self.assertIsNone(result.mission_plan)
        self.assertEqual(result.objectives, ())

    def test_resumption_never_reads_checkpoints_from_an_unreviewed_graph(self):
        journal = Mock()
        result = observe_smartsvg_mission_resumption(
            source, journal, replace(P, policy_blob="b"*40), M,
            {"W01-V1-CORE": M}, role="B")
        journal.latest.assert_not_called()
        self.assertEqual(result.status, "SOURCE_REVIEW_REQUIRED")
        self.assertIsNone(result.mission_plan)


    def test_unavailable_local_journal_returns_no_resumption_advice(self):
        journal = Mock()
        journal.latest.side_effect = OperationalError("private database path")
        result = observe_smartsvg_mission_resumption(
            source, journal, P, M, {"W01-V1-CORE": M}, role="B")
        self.assertEqual(result.status, "LOCAL_JOURNAL_UNAVAILABLE")
        self.assertIsNone(result.mission_plan)
        self.assertNotIn("private database path", repr(result))


class SmartSVGMissionCommandTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "missions #.sqlite"
        self.revision_path = Path(directory.name) / "revisions.json"
        self.revisions = {key: M for key in ("W01-V1-CORE", "W05-SD0-A")}
        self.revision_path.write_text(json.dumps(self.revisions), encoding="utf-8")

    def call(self, get=source, *, snapshot=None, peer=None):
        result = StringIO()
        state_args = ["--journal", str(self.path)] if snapshot is None else [
            "--snapshot", str(snapshot)]
        args = ["--main", M, "--role", "B", *state_args,
                "--revisions", str(self.revision_path)]
        if peer is not None:
            args.extend(("--peer-snapshot", str(peer)))
        with patch("tools.smartsvg_controller_mission_cli.github_get",
                   side_effect=lambda path, token: get(path)), redirect_stdout(result):
            code = mission_cli(args)
        return code, json.loads(result.getvalue())

    def test_command_reopens_read_only_and_suggests_independent_work(self):
        graph = observe_smartsvg_objectives(source, P, M, self.revisions)
        core = rows(graph)["W01-V1-CORE"]
        journal = MissionJournal(self.path)
        try:
            first = journal.create(P, core, M)
            journal.advance(P, core.key, expected_generation=first.generation,
                            expected_digest=first.digest, main=M, revision=M, role="B",
                            state="WAITING", next_action="VERIFY_CRITERION",
                            evidence="b"*64)
        finally:
            journal.close()
        before = self.path.read_bytes()
        code, report = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(report["selection"], {
            "objective": "W05-SD0-A",
            "action": "VERIFY_CRITERION",
            "checkpoint_status": "NEW",
        })
        self.assertFalse(report["merge_authorized"])
        self.assertFalse(report["agent_work_executed"])
        self.assertNotIn(str(self.path), repr(report))
        self.assertNotIn("b"*64, repr(report))

    def test_command_never_creates_a_missing_database(self):
        get = Mock(side_effect=source)
        code, report = self.call(get)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "LOCAL_JOURNAL_UNAVAILABLE")
        self.assertIsNone(report["selection"])
        self.assertFalse(self.path.exists())
        get.assert_not_called()

    def test_command_bounds_revision_input_before_network_access(self):
        self.revision_path.write_bytes(b" " * (MAX_REVISION_BYTES + 1))
        get = Mock(side_effect=source)
        code, report = self.call(get)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "REVISION_INPUT_INVALID")
        get.assert_not_called()

    def test_command_drops_selection_when_main_moves(self):
        journal = MissionJournal(self.path)
        journal.close()
        main_reads = 0

        def drift(path):
            nonlocal main_reads
            if path == "/branches/main":
                main_reads += 1
                if main_reads == 3:
                    return {"commit": {"sha": "b"*40}}
            return source(path)

        code, report = self.call(drift)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "CONTEXT_CHANGED")
        self.assertIsNone(report["selection"])


    def test_command_reopens_snapshot_without_creating_a_local_database(self):
        journal = MissionJournal(":memory:")
        try:
            graph = observe_smartsvg_objectives(source, P, M, self.revisions)
            core = rows(graph)["W01-V1-CORE"]
            first = journal.create(P, core, M)
            journal.advance(P, core.key, expected_generation=first.generation,
                            expected_digest=first.digest, main=M, revision=M, role="B",
                            state="WAITING", next_action="VERIFY_CRITERION",
                            evidence="b"*64)
            snapshot = self.path.with_name("private-snapshot.json")
            snapshot.write_bytes(journal.export_snapshot(P))
        finally:
            journal.close()
        code, report = self.call(snapshot=snapshot)
        self.assertEqual(code, 0)
        self.assertEqual(report["selection"]["objective"], "W05-SD0-A")
        self.assertFalse(self.path.exists())
        self.assertNotIn("b"*64, repr(report))

    def test_command_refuses_invalid_snapshot_before_network_access(self):
        snapshot = self.path.with_name("invalid.json")
        snapshot.write_bytes(b'{"private":"do not print"}')
        get = Mock(side_effect=source)
        code, report = self.call(get, snapshot=snapshot)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "MISSION_SNAPSHOT_UNAVAILABLE")
        self.assertNotIn("do not print", repr(report))
        get.assert_not_called()


    def test_pair_quarantines_conflict_and_selects_independent_mission(self):
        graph = observe_smartsvg_objectives(source, P, M, self.revisions)
        core = rows(graph)["W01-V1-CORE"]
        snapshots = []
        for label, action, evidence in (("local", "REPAIR", "b"*64),
                                        ("peer", "VERIFY", "c"*64)):
            journal = MissionJournal(":memory:")
            try:
                first = journal.create(P, core, M)
                journal.advance(P, core.key, expected_generation=first.generation,
                                expected_digest=first.digest, main=M, revision=M,
                                role="B", state="ACTIVE", next_action=action,
                                evidence=evidence)
                path = self.path.with_name(label + ".json")
                path.write_bytes(journal.export_snapshot(P))
                snapshots.append(path)
            finally:
                journal.close()
        before = [p.read_bytes() for p in snapshots]
        code, report = self.call(snapshot=snapshots[0], peer=snapshots[1])
        self.assertEqual(code, 0)
        self.assertEqual(report["quarantined_missions"], [core.key])
        self.assertEqual(report["selection"]["objective"], "W05-SD0-A")
        self.assertEqual([p.read_bytes() for p in snapshots], before)
        self.assertNotIn("b"*64, repr(report))
        self.assertNotIn("c"*64, repr(report))
        self.assertFalse(self.path.exists())

    def test_pair_invalid_peer_refuses_all_advice_before_network(self):
        journal = MissionJournal(":memory:")
        try:
            snapshot = self.path.with_name("local.json")
            snapshot.write_bytes(journal.export_snapshot(P))
        finally:
            journal.close()
        peer = self.path.with_name("peer.json")
        peer.write_bytes(b"{}")
        get = Mock(side_effect=source)
        code, report = self.call(get, snapshot=snapshot, peer=peer)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "MISSION_SNAPSHOT_UNAVAILABLE")
        self.assertIsNone(report["selection"])
        get.assert_not_called()

    def test_pair_requires_local_snapshot_instead_of_database(self):
        get = Mock(side_effect=source)
        code, report = self.call(get, peer=self.path.with_name("peer.json"))
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "SNAPSHOT_PAIR_REQUIRED")
        get.assert_not_called()
        self.assertFalse(self.path.exists())
