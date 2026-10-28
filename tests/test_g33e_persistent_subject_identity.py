"""G3.3e-b1: persistent Subject identity over exact G2.4 float32 masks."""
from hashlib import sha256
import asyncio
from pathlib import Path
import re
import struct
import tempfile
import time
import sys
from types import SimpleNamespace
from unittest import mock
import unittest
import zlib

from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError
from engine.project_routes_g22 import register_project_routes


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
        with mock.patch.dict(sys.modules, {"aiohttp": SimpleNamespace(web=Web)}):
            register_project_routes(routes, self.temp.name)
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


if __name__ == "__main__":
    unittest.main()
