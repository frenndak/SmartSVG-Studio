"""Regression: closing native Atelier never waits for an in-flight confirmed writer."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import threading
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel


class NativeAtelierShutdownTests(unittest.TestCase):
    def test_shutdown_does_not_block_confirmed_running_writer(self):
        entered = threading.Event()
        release = threading.Event()
        finished = threading.Event()
        executor = ThreadPoolExecutor(max_workers=1)
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel._closed = False
        panel._history_generation = 7
        panel._history_worker = executor
        panel._close_brush = lambda: None

        def confirmed_write():
            entered.set()
            try:
                self.assertTrue(release.wait(5), "test worker release timed out")
            finally:
                finished.set()

        future = executor.submit(confirmed_write)
        try:
            self.assertTrue(entered.wait(3), "worker never started")
            closed = threading.Event()
            closer = threading.Thread(target=lambda: (panel.shutdown(), closed.set()), daemon=True)
            closer.start()
            self.assertTrue(closed.wait(1), "Tk shutdown blocked on running writer")
            self.assertTrue(panel._closed)
            self.assertEqual(panel._history_generation, 8)
            self.assertFalse(future.cancelled(), "confirmed running write was cancelled")
            panel.shutdown()  # idempotent
        finally:
            release.set()
            future.result(timeout=5)
            executor.shutdown(wait=True)
        self.assertTrue(finished.is_set())

    def test_real_tk_root_closes_while_confirmed_worker_is_running(self):
        """Exercise a real Tk event loop without waiting for a slow writer."""
        try:
            import tkinter as tk
            root = tk.Tk()
        except Exception as exc:
            self.skipTest("real Tk display unavailable: " + str(exc))
        root.withdraw()
        entered, release = threading.Event(), threading.Event()
        executor = ThreadPoolExecutor(max_workers=1)
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel._closed = False
        panel._history_generation = 0
        panel._history_worker = executor
        panel._close_brush = lambda: None

        def slow_write():
            entered.set()
            if not release.wait(5):
                raise AssertionError("worker release timed out")
            return "committed"

        future = executor.submit(slow_write)
        try:
            self.assertTrue(entered.wait(3))
            root.after(0, lambda: (panel.shutdown(), root.destroy()))
            import time
            started = time.monotonic()
            root.mainloop()
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertTrue(panel._closed)
            self.assertFalse(future.cancelled())
        finally:
            release.set()
            future.result(timeout=5)
            executor.shutdown(wait=True)
            try:
                root.destroy()
            except tk.TclError:
                pass

    def test_shutdown_cancels_queued_unconfirmed_work(self):
        entered = threading.Event()
        release = threading.Event()
        executor = ThreadPoolExecutor(max_workers=1)
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel._closed = False
        panel._history_generation = 0
        panel._history_worker = executor
        panel._close_brush = lambda: None

        def running():
            entered.set()
            release.wait(5)

        active = executor.submit(running)
        try:
            self.assertTrue(entered.wait(3))
            queued = executor.submit(lambda: "must not execute")
            panel.shutdown()
            self.assertTrue(queued.cancelled())
            self.assertFalse(active.cancelled())
        finally:
            release.set()
            active.result(timeout=5)
            executor.shutdown(wait=True)


if __name__ == "__main__":
    unittest.main()
