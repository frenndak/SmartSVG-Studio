"""G3.3e-b1: persistent Subject identity over exact G2.4 float32 masks."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
import asyncio
import importlib
from pathlib import Path
import re
import struct
import tempfile
import time
import sys
from types import ModuleType, SimpleNamespace
from unittest import mock
import unittest
import zlib

from smartsvg_core.mask_snapshot_g24 import SNAPSHOT_KEY, SNAPSHOT_PATH, create_snapshot, encode_preview_l8
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_recovery import save_with_recovery, RecoveryError
from smartsvg_core.subject_identity_g33e import register_subject_identity as bind_subject_identity, SubjectIdentityError
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError


def png(width=4, height=3):
    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload +
                struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))
    row = b"\x00" + bytes([95]) * (width * 4)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(row * height)) +
            chunk(b"IEND", b""))


class PersistentSubjectIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = ManagedWorkspace(self.temp.name)
        created = self.workspace.create(
            "subjects", png(), profile="Sticker - contour du sujet",
            width_mm=40, dpi=300, notes="")
        self.source_fingerprint = "a" * 64
        first = [
            0.0, 0.49, 0.5, 1.0,
            0.0, 0.75, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
        ]
        second = [
            1.0, 1.0, 0.0, 0.0,
            1.0, 0.6, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
        ]
        self.raw = struct.pack("<24f", *(first + second))
        self.workspace.save_base_masks(
            "subjects", raw_float32=self.raw, shape=[2, 3, 4],
            image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint,
            expected_sha256=created["sha256"])

    @property
    def path(self):
        return Path(self.temp.name) / "SmartSVG_Managed_Projects" / "subjects.smartsvg"

    def binding(self, index=0):
        state = self.workspace.inspect("subjects")
        catalog = state["base_masks"]["mask_identity"]
        return state, catalog["bindings"][index], catalog["source_id"]

    def register(self, *, index=0, expected_sha256=None):
        state, item, source_id = self.binding(index)
        return self.workspace.register_subject_identity(
            "subjects",
            mask_index=index,
            mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id=source_id,
            source_sha256=self.source_fingerprint,
            expected_sha256=expected_sha256 or state["sha256"],
            confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000,
        )

    def test_create_reopen_and_recognize_preserves_exact_mask_resources(self):
        before = load_project(self.path)
        before_resources = dict(before.resources)
        before_snapshot_sha = sha256(
            before.resources["snapshots/base_masks_float32_v1.zlib"]).hexdigest()

        result = self.register()

        self.assertEqual(result["status"], "subject_identity_created")
        self.assertRegex(result["subject_id"], r"^subject-[a-f0-9]{32}$")
        reopened = load_project(self.path)
        self.assertEqual(len(reopened.subjects), 1)
        subject = reopened.subjects[0]
        self.assertEqual(subject.subject_id, result["subject_id"])
        self.assertEqual(subject.source_id, "source-original")
        self.assertEqual(subject.mask_id, "base-mask-00")
        self.assertEqual(subject.bbox_px, (1, 0, 3, 2))
        self.assertEqual(reopened.resources, before_resources)
        self.assertEqual(
            sha256(reopened.resources["snapshots/base_masks_float32_v1.zlib"]).hexdigest(),
            before_snapshot_sha)
        current = self.workspace.inspect("subjects")
        state, item, source_id = self.binding(0)
        again = self.workspace.register_subject_identity(
            "subjects", mask_index=0, mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id=source_id, source_sha256=self.source_fingerprint,
            expected_sha256=current["sha256"], confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000)
        self.assertEqual(again["status"], "subject_identity_exists")
        self.assertEqual(again["subject_id"], result["subject_id"])
        self.assertEqual(again["sha256"], current["sha256"])
        self.assertEqual(len(load_project(self.path).subjects), 1)

    def test_existing_identity_allows_identical_snapshot_replay(self):
        created = self.register()
        state = self.workspace.inspect("subjects")
        replay = self.workspace.save_base_masks(
            "subjects", raw_float32=self.raw, shape=[2, 3, 4],
            image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint,
            expected_sha256=state["sha256"])
        reopened = load_project(self.path)
        self.assertEqual(reopened.subjects[0].subject_id, created["subject_id"])
        self.assertEqual(replay["status"], "full_resolution_masks_saved")

    def test_existing_identity_refuses_changed_snapshot_without_touching_project(self):
        self.register()
        before = self.workspace.inspect("subjects")
        values = list(struct.unpack("<24f", self.raw))
        values[0] = 0.9
        changed = struct.pack("<24f", *values)
        with self.assertRaisesRegex(
                WorkspaceError, "SUBJECT_IDENTITIES_REQUIRE_EXPLICIT_REBIND"):
            self.workspace.save_base_masks(
                "subjects", raw_float32=changed, shape=[2, 3, 4],
                image_fingerprint="b" * 64,
                editor_fingerprint=self.source_fingerprint,
                expected_sha256=before["sha256"])
        self.assertEqual(self.workspace.inspect("subjects")["sha256"], before["sha256"])
        self.assertEqual(load_project(self.path).subjects[0].subject_id,
                         self.workspace.inspect("subjects")["base_masks"]["mask_identity"]
                         ["bindings"][0]["subject_id"])

    def test_existing_identity_refuses_reordered_snapshot(self):
        self.register()
        before = self.workspace.inspect("subjects")
        stride = 4 * 3 * 4
        reordered = self.raw[stride:] + self.raw[:stride]
        with self.assertRaisesRegex(
                WorkspaceError, "SUBJECT_IDENTITIES_REQUIRE_EXPLICIT_REBIND"):
            self.workspace.save_base_masks(
                "subjects", raw_float32=reordered, shape=[2, 3, 4],
                image_fingerprint="b" * 64,
                editor_fingerprint=self.source_fingerprint,
                expected_sha256=before["sha256"])
        self.assertEqual(self.workspace.inspect("subjects")["sha256"], before["sha256"])


    def test_existing_identity_refuses_new_float32_bytes_with_same_bbox(self):
        created = self.register()
        before = self.workspace.inspect("subjects")
        project = load_project(self.path)
        values = list(struct.unpack("<24f", self.raw))
        values[5] = 0.9  # remains foreground; bbox is intentionally unchanged
        changed = struct.pack("<24f", *values)
        meta, compressed = create_snapshot(
            changed, [2, 3, 4], image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint)
        resources = dict(project.resources)
        resources[SNAPSHOT_PATH] = compressed
        masks = []
        stride = 4 * 3 * 4
        for index, mask in enumerate(project.masks):
            preview = encode_preview_l8(
                changed[index * stride:(index + 1) * stride], 4, 3)
            path = project.mask_paths[mask.mask_id]
            resources[path] = preview
            masks.append(replace(mask, sha256=sha256(preview).hexdigest()))
        forged = replace(
            project,
            document={**project.document, SNAPSHOT_KEY: meta},
            masks=tuple(masks),
            resources=resources,
        )
        save_with_recovery(
            self.path, forged, expected_sha256=before["sha256"])
        state, item, source_id = self.binding(0)
        self.assertIsNone(item["subject_id"])
        self.assertEqual(item["subject_proof_status"], "mismatch")
        with self.assertRaisesRegex(
                WorkspaceError, "SUBJECT_IDENTITY_PROOF_MISMATCH"):
            self.workspace.register_subject_identity(
                "subjects", mask_index=0, mask_id=item["mask_id"],
                mask_sha256_float32=item["mask_sha256_float32"],
                source_id=source_id, source_sha256=self.source_fingerprint,
                expected_sha256=state["sha256"], confirmed=True,
                expires_at_ms=int(time.time() * 1000) + 60_000)


    def test_read_catalog_and_recognition_reject_changed_source_fingerprint(self):
        self.register()
        before = self.workspace.inspect("subjects")
        project = load_project(self.path)
        meta = dict(project.document[SNAPSHOT_KEY])
        meta["editor_fingerprint"] = "d" * 64
        forged = replace(
            project, document={**project.document, SNAPSHOT_KEY: meta})
        save_with_recovery(
            self.path, forged, expected_sha256=before["sha256"])
        state, item, source_id = self.binding(0)
        self.assertIsNone(item["subject_id"])
        self.assertEqual(item["subject_proof_status"], "mismatch")
        with self.assertRaisesRegex(
                WorkspaceError, "SUBJECT_IDENTITY_PROOF_MISMATCH"):
            self.workspace.register_subject_identity(
                "subjects", mask_index=0, mask_id=item["mask_id"],
                mask_sha256_float32=item["mask_sha256_float32"],
                source_id=source_id, source_sha256="d" * 64,
                expected_sha256=state["sha256"], confirmed=True,
                expires_at_ms=int(time.time() * 1000) + 60_000)


    def test_core_rejects_duplicate_empty_and_collision_cases(self):
        first = self.raw[:4 * 3 * 4]
        self.workspace.save_base_masks(
            "subjects", raw_float32=first + first, shape=[2, 3, 4],
            image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint,
            expected_sha256=self.workspace.inspect("subjects")["sha256"])
        state, item, source_id = self.binding(0)
        with self.assertRaisesRegex(SubjectIdentityError, "AMBIGUOUS_MASK_CONTENT"):
            bind_subject_identity(
                load_project(self.path), mask_index=0,
                mask_id=item["mask_id"],
                mask_sha256_float32=item["mask_sha256_float32"],
                source_id=source_id, source_sha256=self.source_fingerprint)

        empty = bytes(4 * 3 * 4)
        self.workspace.save_base_masks(
            "subjects", raw_float32=empty + self.raw[4 * 3 * 4:],
            shape=[2, 3, 4], image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint,
            expected_sha256=self.workspace.inspect("subjects")["sha256"])
        state, item, source_id = self.binding(0)
        with self.assertRaisesRegex(SubjectIdentityError, "MASK_HAS_NO_G26_FOREGROUND"):
            bind_subject_identity(
                load_project(self.path), mask_index=0,
                mask_id=item["mask_id"],
                mask_sha256_float32=item["mask_sha256_float32"],
                source_id=source_id, source_sha256=self.source_fingerprint)

        self.workspace.save_base_masks(
            "subjects", raw_float32=self.raw, shape=[2, 3, 4],
            image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint,
            expected_sha256=self.workspace.inspect("subjects")["sha256"])
        project = load_project(self.path)
        state, first_item, source_id = self.binding(0)
        state, second_item, _ = self.binding(1)
        project, _, _ = bind_subject_identity(
            project, mask_index=0, mask_id=first_item["mask_id"],
            mask_sha256_float32=first_item["mask_sha256_float32"],
            source_id=source_id, source_sha256=self.source_fingerprint,
            subject_id_factory=lambda: "1" * 32)
        with self.assertRaisesRegex(SubjectIdentityError, "SUBJECT_ID_COLLISION"):
            bind_subject_identity(
                project, mask_index=1, mask_id=second_item["mask_id"],
                mask_sha256_float32=second_item["mask_sha256_float32"],
                source_id=source_id, source_sha256=self.source_fingerprint,
                subject_id_factory=lambda: "1" * 32)

    def test_workspace_rejects_unconfirmed_expired_stale_and_wrong_binding(self):
        state, item, source_id = self.binding(0)
        base = dict(
            mask_index=0, mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id=source_id, source_sha256=self.source_fingerprint,
            expected_sha256=state["sha256"], confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000)
        cases = [
            ({"confirmed": False}, "SUBJECT_IDENTITY_CONFIRMATION_REQUIRED"),
            ({"expires_at_ms": int(time.time() * 1000) - 1}, "SUBJECT_IDENTITY_SESSION_EXPIRED"),
            ({"expected_sha256": "0" * 64}, "PROJECT_CHANGED"),
            ({"mask_sha256_float32": "0" * 64}, "MASK_FLOAT32_SHA_MISMATCH"),
            ({"mask_id": "base-mask-99"}, "MASK_IDENTITY_MISMATCH"),
            ({"source_id": "source-wrong"}, "SUBJECT_SOURCE_MISMATCH"),
            ({"mask_index": 99}, "MASK_INDEX_OUT_OF_RANGE"),
        ]
        for changes, code in cases:
            with self.subTest(code=code), self.assertRaisesRegex(WorkspaceError, code):
                self.workspace.register_subject_identity(
                    "subjects", **{**base, **changes})

    def test_concurrent_same_revision_creates_exactly_one_subject(self):
        state = self.workspace.inspect("subjects")
        catalog = state["base_masks"]["mask_identity"]
        source_id = catalog["source_id"]

        def attempt(index):
            item = catalog["bindings"][index]
            try:
                return self.workspace.register_subject_identity(
                    "subjects", mask_index=index, mask_id=item["mask_id"],
                    mask_sha256_float32=item["mask_sha256_float32"],
                    source_id=source_id,
                    source_sha256=self.source_fingerprint,
                    expected_sha256=state["sha256"], confirmed=True,
                    expires_at_ms=int(time.time() * 1000) + 60_000)
            except WorkspaceError as exc:
                return str(exc)

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, (0, 1)))
        successes = [item for item in outcomes if isinstance(item, dict)]
        failures = [item for item in outcomes if isinstance(item, str)]
        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)
        self.assertIn(
            failures[0],
            {"PROJECT_LOCKED", "PROJECT_CHANGED", "PROJECT_CHANGED_DURING_SAVE"})
        self.assertEqual(len(load_project(self.path).subjects), 1)

    def test_pending_recovery_and_save_failure_never_report_success(self):
        before, item, source_id = self.binding(0)
        arguments = dict(
            mask_index=0, mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id=source_id, source_sha256=self.source_fingerprint,
            expected_sha256=before["sha256"], confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000)
        pending = self.path.with_name("subjects.pending-backup.smartsvg")
        pending.write_bytes(self.path.read_bytes())
        with self.assertRaisesRegex(
                WorkspaceError, "PENDING_BACKUP_REVIEW_REQUIRED"):
            self.workspace.register_subject_identity("subjects", **arguments)
        self.assertEqual(
            sha256(self.path.read_bytes()).hexdigest(), before["sha256"])
        pending.unlink()

        with mock.patch(
                "smartsvg_core.project_workspace_g22.save_with_recovery",
                side_effect=RecoveryError("SAVE_FAILED")):
            with self.assertRaisesRegex(WorkspaceError, "SAVE_FAILED"):
                self.workspace.register_subject_identity("subjects", **arguments)
        self.assertEqual(self.workspace.inspect("subjects")["sha256"], before["sha256"])

    def test_idempotent_recognition_preserves_accessories(self):
        first = self.register(index=0)
        second = self.register(index=1)
        state = self.workspace.inspect("subjects")
        project = load_project(self.path)
        subjects = tuple(
            replace(subject, accessory_ids=(second["subject_id"],))
            if subject.subject_id == first["subject_id"] else subject
            for subject in project.subjects)
        save_with_recovery(
            self.path, replace(project, subjects=subjects),
            expected_sha256=state["sha256"])
        result = self.register(index=0)
        self.assertEqual(result["status"], "subject_identity_exists")
        reopened = load_project(self.path)
        subject = next(item for item in reopened.subjects
                       if item.subject_id == first["subject_id"])
        self.assertEqual(subject.accessory_ids, (second["subject_id"],))



    def test_save_readback_verification_is_part_of_recovery_transaction(self):
        import smartsvg_core.project_workspace_g22 as workspace_module
        original = workspace_module.save_with_recovery
        with mock.patch.object(
                workspace_module, "save_with_recovery", wraps=original) as saver:
            self.register()
        self.assertIn("verify_saved_project", saver.call_args.kwargs)



    def test_opt_in_route_requires_exact_confirmed_metadata(self):
        state, item, source_id = self.binding(0)

        class Routes:
            def __init__(self):
                self.gets, self.posts = {}, {}
            def get(self, path):
                return lambda fn: self.gets.setdefault(path, fn) or fn
            def post(self, path):
                def decorate(fn):
                    self.posts[path] = fn
                    return fn
                return decorate

        class Web:
            @staticmethod
            def json_response(data, status=200, headers=None):
                return SimpleNamespace(data=data, status=status, headers=headers or {})
            class Response:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)

        class Part:
            def __init__(self, name, value):
                self.name, self.value, self.done = name, value.encode(), False
            async def read_chunk(self, size=65536):
                if self.done:
                    return b""
                self.done = True
                return self.value

        class Reader:
            def __init__(self, fields):
                self.parts = [Part(key, value) for key, value in fields.items()]
            async def next(self):
                return self.parts.pop(0) if self.parts else None

        class Request:
            content_length = None
            headers = {
                "X-SmartSVG-UI": "1",
                "Origin": "http://localhost:8188",
                "Host": "localhost:8188",
            }
            def __init__(self, fields):
                self.reader = Reader(fields)
            async def multipart(self):
                return self.reader

        routes = Routes()
        engine_package = ModuleType("engine")
        engine_package.__path__ = [str(Path(__file__).resolve().parents[1] / "engine")]
        module_patch = mock.patch.dict(sys.modules, {
            "engine": engine_package,
            "aiohttp": SimpleNamespace(web=Web),
        })
        module_patch.start()
        self.addCleanup(module_patch.stop)
        route_module = importlib.import_module("engine.project_routes_g22")
        route_module.register_project_routes(routes, self.temp.name)
        handler = routes.posts["/smartsvg/g22/subject/identity"]
        response = asyncio.run(handler(Request({
            "name": "subjects",
            "expected_sha256": state["sha256"],
            "source_id": source_id,
            "source_sha256": self.source_fingerprint,
            "mask_index": "0",
            "mask_id": item["mask_id"],
            "mask_sha256_float32": item["mask_sha256_float32"],
            "expires_at_ms": str(int(time.time() * 1000) + 60_000),
            "confirmed": "yes",
        })))
        self.assertEqual(response.status, 200)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["result"]["mask_id"], "base-mask-00")
        self.assertRegex(response.data["result"]["subject_id"], r"^subject-[a-f0-9]{32}$")

        rejected = Request({
            "name": "subjects",
            "confirmed": "yes",
        })
        rejected.headers = {
            "X-SmartSVG-UI": "1",
            "Origin": "https://evil.example",
            "Host": "localhost:8188",
        }
        response = asyncio.run(handler(rejected))
        self.assertEqual(response.status, 403)
        self.assertEqual(response.data["error_code"], "ORIGIN_REJECTED")


if __name__ == "__main__":
    unittest.main()
